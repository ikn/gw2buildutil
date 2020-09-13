import re
import collections

from ... import build, definitions
from .. import util, text as parse_text


url_pattern = re.compile(r'^http://gw2skills.net/editor/\?[A-Za-z0-9+-/]+$')

def parse_url (lines):
    if len(lines) > 1:
        raise util.ParseError('first intro paragraph should have only 1 line')
    if url_pattern.match(lines[0]) is None:
        raise util.ParseError('first intro line doesn\'t look like a valid URL')
    return lines[0]


def parse_description (paragraphs):
    return build.MarkdownBody(
        '\n\n'.join('\n'.join(lines) for lines in paragraphs))


stats_pattern = re.compile(r'^'
    r'\w+( [\w +]+)?(, \w+( [\w +]+)?)*'
    r'$')

def parse_stats (meta, line):
    if stats_pattern.match(line) is None:
        raise util.ParseError('stats definition doesn\'t match expected '
                              'format: {}'.format(repr(line)))

    gear_stats = {}
    for section in line.split(', '):
        words = section.split()
        stats = (build.PvpStatsEnum
                 if meta.game_mode is build.GameModes.PVP
                 else build.StatsEnum).from_id(words[0])
        gear_groups = parse_text.parse_gear_groups(section[len(words[0]) + 1:])

        if not gear_groups:
            gear_stats[None] = stats
        for gear_group in gear_groups:
            gear_stats[gear_group] = stats

    if None not in gear_stats:
        raise util.ParseError('no default stats found')
    return gear_stats


def stats_lookup (names, stats):
    for name in names:
        if name in stats:
            return stats[name]
    return stats[None]


weapons_pattern = re.compile(r'^'
    r'(?P<types1>\w+( \w+)?) \((?P<sigils1>\w+ \w+)\)'
    r'( / (?P<types2>\w+( \w+)?) \((?P<sigils2>\w+ \w+)\))?'
    r'$')

def parse_weapons (line, stats, meta):
    match = weapons_pattern.match(line)
    if match is None:
        raise util.ParseError('weapons definition doesn\'t match expected '
                              'format: {}'.format(repr(line)))
    fields = match.groupdict()
    parse_sigil = (parse_text.parse_pvp_sigil
                   if meta.game_mode == build.GameModes.PVP
                   else parse_text.parse_sigil)

    def build_weapon (type_, hand, sigils):
        weapon_stats = stats_lookup((type_, build.GearGroups.WEAPONS), stats)
        return build.Weapon(type_, hand, weapon_stats, sigils)

    def build_weapon_set (weapons_field, sigils_field):
        types = [build.WeaponTypes.from_id(t) for t in weapons_field.split()]
        sigils = [parse_sigil(s) for s in sigils_field.split()]
        if len(types) == 2:
            return (
                build_weapon(types[0], build.WeaponHands.MAIN, (sigils[0],)),
                build_weapon(types[1], build.WeaponHands.OFF, (sigils[1],)))
        else:
            return (build_weapon(types[0], build.WeaponHands.BOTH, sigils),)

    return build.Weapons(
        build_weapon_set(fields['types1'], fields['sigils1']),
        (build_weapon_set(fields['types2'], fields['sigils2'])
         if fields['types2'] is not None else None))


runes_pattern = re.compile(r'^('
    r'(?P<single>[\w ]+)'
    r'|'
    r'(?P<multi>\d [\w ]+( \+ \d [\w ]+)+)'
    r') runes$')

def parse_runes (runes_line):
    match = runes_pattern.match(runes_line)
    if match is None:
        raise util.ParseError('runes definition doesn\'t match expected '
                              'format: {}'.format(repr(runes_line)))

    fields = match.groupdict()
    if fields['single'] is not None:
        runes = collections.Counter({fields['single']: 6})
    else:
        rune_items = (item.split() for item in fields['multi'].split(' + '))
        runes = collections.Counter(
            {type_: int(count) for count, type_ in rune_items})
    if sum(runes.values()) != 6:
        raise util.ParseError('wrong total rune count: {}'.format(dict(runes)))
    return runes


def parse_armour (runes, stats):
    return build.Armour([build.ArmourPiece(
        type_,
        stats_lookup((type_, build.GearGroups.ARMOUR), stats),
        parse_text.parse_rune(rune)
    ) for type_, rune in zip(build.ArmourTypes, runes.elements())])


def parse_pvp_armour (runes, stats):
    if len(runes) > 1:
        raise util.ParseError('different runes are not allowed in PvP')

    return build.PvpArmour(parse_text.parse_pvp_rune(next(iter(runes))))


def parse_trinkets (stats):
    T = build.TrinketTypes
    G = build.GearGroups
    return build.Trinkets([
        build.Trinket(T.BACK, stats_lookup(
            (T.BACK, G.TRINKETS), stats)),
        build.Trinket(T.ACCESSORY_1, stats_lookup(
            (T.ACCESSORY_1, G.ACCESSORIES, G.TRINKETS), stats)),
        build.Trinket(T.ACCESSORY_2, stats_lookup(
            (T.ACCESSORY_2, G.ACCESSORIES, G.TRINKETS), stats)),
        build.Trinket(T.AMULET, stats_lookup(
            (T.AMULET, G.TRINKETS), stats)),
        build.Trinket(T.RING_1, stats_lookup(
            (T.RING_1, G.RINGS, G.TRINKETS), stats)),
        build.Trinket(T.RING_2, stats_lookup(
            (T.RING_2, G.RINGS, G.TRINKETS), stats)),
    ])


traits_pattern = re.compile(r'^'
    f'{parse_text.words_pattern}' r'( [1-3]){3}'
    r'(, ' f'{parse_text.words_pattern}' r'( [1-3]){3}){2}'
    r'$')

def parse_traits (line):
    if traits_pattern.match(line) is None:
        raise util.ParseError('traits definition doesn\'t match expected '
                              f'format: {repr(line)}')

    specs = []
    for spec_text in line.split(', '):
        parts = spec_text.split(' ')
        name = ' '.join(parts[:-3])
        choices_text = parts[-3:]
        choices = [build.TraitChoices.from_index(int(choice_text) - 1)
                   for choice_text in choices_text]
        specs.append(
            build.SpecialisationChoices(build.Specialisation(name), choices))

    return build.Traits(specs)


def parse_consumables (line):
    consumables = parse_text.parse_words_seq(line, 'consumables')
    if len(consumables) > 2:
        raise util.ParseError('expected 1 or 2 consumables, got '
                              f'{len(consumables)}')

    return build.Consumables(*consumables)


num_prof_lines = collections.defaultdict(lambda: 0, {
    definitions.profession['ranger'].profession: 1,
})


def parse_ranger_pets (line):
    return build.RangerPets(parse_text.parse_words_seq(line, 'ranger pets'))


def parse_prof_options (lines, meta):
    if meta.profession.same_base(definitions.profession['ranger']):
        return parse_ranger_pets(lines[0])
    else:
        return None


def parse_setup (lines, meta):
    prof_lines = num_prof_lines[meta.profession.profession]
    min_lines = 4 + prof_lines
    max_lines = 5 + prof_lines
    num_lines = len(lines)
    if num_lines not in list(range(min_lines, max_lines + 1)):
        raise util.ParseError(
            'second intro paragraph has the wrong number of lines: '
            f'got {num_lines}, expected {min_lines}-{max_lines}')
    if num_lines == max_lines and meta.game_mode == build.GameModes.PVP:
        raise util.ParseError('consumables are not allowed for PvP builds')

    stats = parse_stats(meta, lines[1])
    if meta.game_mode == build.GameModes.PVP:
        gear = build.PvpGear(
            stats[None],
            parse_weapons(lines[0], stats, meta),
            parse_pvp_armour(parse_runes(lines[2]), stats))
    else:
        gear = build.Gear(
            parse_weapons(lines[0], stats, meta),
            parse_armour(parse_runes(lines[2]), stats),
            parse_trinkets(stats),
            (parse_consumables(lines[4])
            if num_lines == max_lines else build.Consumables()))

    return {
        'gear': gear,
        'traits': parse_traits(lines[3]),
        'profession options': parse_prof_options(lines[-prof_lines:], meta),
    }


def parse_revenant_skills (lines):
    if len(lines) != 1:
        raise util.ParseError(
            'third intro paragraph has the wrong number of lines: '
            f'got {len(lines)}, expected 1')

    legends_text = parse_text.parse_words_seq(lines[0], 'legends', 2)
    return build.RevenantSkills([build.RevenantLegends.from_id(legend_text)
                                 for legend_text in legends_text])


def parse_skills (lines, meta):
    if meta.profession.same_base(definitions.profession['revenant']):
        return parse_revenant_skills(lines)

    if len(lines) != 3:
        raise util.ParseError(
            'third intro paragraph has the wrong number of lines: '
            f'got {len(lines)}, expected 3')

    return build.Skills(
        parse_text.parse_words_seq(lines[0], 'heal skill', 1)[0],
        parse_text.parse_words_seq(lines[1], 'utility skills', 3),
        parse_text.parse_words_seq(lines[2], 'elite skill', 1)[0])


def parse (lines, meta):
    paragraphs = list(util.group_paragraphs(
        util.strip_empty_lines(lines, inner='collapse')))
    if len(paragraphs) < 3:
        raise util.ParseError('intro is incomplete')

    setup = parse_setup(paragraphs[-2], meta)
    return build.Intro(
        parse_url(paragraphs[0]),
        parse_description(paragraphs[1:-2]),
        setup['gear'],
        setup['traits'],
        parse_skills(paragraphs[-1], meta),
        setup['profession options'])
