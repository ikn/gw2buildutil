import re
import collections

from ... import build, definitions
from .. import util, text as parse_text


def group_paragraphs (lines):
    paragraph = []
    for line in lines:
        if line:
            paragraph.append(line)
        else:
            yield paragraph
            paragraph = []
    yield paragraph


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
    '\w+( [\w +]+)?(, \w+( [\w +]+)?)*'
    '$')

def parse_stats (meta, line):
    gear_stats = {}
    if stats_pattern.match(line) is None:
        raise util.ParseError('stats definition doesn\'t match expected '
                              'format: {}'.format(repr(line)))

    for section in line.split(', '):
        words = section.split()
        stats = (definitions.pvp_stats
                 if meta.game_modes is definitions.game_modes['pvp']
                 else definitions.stats)[words[0]]
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
    '(?P<types1>\w+( \w+)?) \((?P<sigils1>\w+ \w+)\)'
    '( / (?P<types2>\w+( \w+)?) \((?P<sigils2>\w+ \w+)\))?'
    '$')

def parse_weapons (line, stats):
    match = weapons_pattern.match(line)
    if match is None:
        raise util.ParseError('weapons definition doesn\'t match expected '
                              'format: {}'.format(repr(line)))
    fields = match.groupdict()
    def_hand = definitions.weapon_hand

    def build_weapon (type_, hand, sigils):
        weapon_stats = stats_lookup(
            (type_, definitions.gear_group['weapons']), stats)
        return build.Weapon(type_, hand, weapon_stats, sigils)

    def build_weapon_hand (weapons_field, sigils_field):
        types = [definitions.weapon_type[t]
                 for t in weapons_field.lower().split()]
        sigils = [parse_text.parse_sigil(s) for s in sigils_field.split()]
        if len(types) == 2:
            return (build_weapon(types[0], def_hand['main'], (sigils[0],)),
                    build_weapon(types[1], def_hand['off'], (sigils[1],)))
        else:
            return (build_weapon(types[0], def_hand['both'], sigils),)

    return build.Weapons(
        build_weapon_hand(fields['types1'], fields['sigils1']),
        (build_weapon_hand(fields['types2'], fields['sigils2'])
         if fields['types2'] is not None else None))


runes_pattern = re.compile(r'^('
    '(?P<single>[\w ]+)'
    '|'
    '(?P<multi>\d [\w ]+( \+ \d [\w ]+)+)'
    ') runes$')

def parse_armour (runes_line, stats):
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

    types = set(definitions.armour_type.values())
    return build.Armour([build.ArmourPiece(
        type_,
        stats_lookup((type_, definitions.gear_group['armour']), stats),
        parse_text.parse_rune(rune)
    ) for type_, rune in zip(types, runes.elements())])


def parse_trinkets (stats):
    g = definitions.gear_group
    t = definitions.trinket_type
    return build.Trinkets([
        build.Trinket(t['back'], stats_lookup(
            (g['back'], g['trinkets']), stats)),
        build.Trinket(t['accessory 1'], stats_lookup(
            (g['accessory 1'], g['accessories'], g['trinkets']), stats)),
        build.Trinket(t['accessory 2'], stats_lookup(
            (g['accessory 2'], g['accessories'], g['trinkets']), stats)),
        build.Trinket(t['amulet'], stats_lookup(
            (g['amulet'], g['trinkets']), stats)),
        build.Trinket(t['ring 1'], stats_lookup(
            (g['ring 1'], g['rings'], g['trinkets']), stats)),
        build.Trinket(t['ring 2'], stats_lookup(
            (g['ring 2'], g['rings'], g['trinkets']), stats)),
    ])


def parse_traits (line):
    # TODO
    return None


def parse_food (line):
    # TODO
    return None


def parse_prof_options (line, meta):
    # TODO
    return None


def parse_setup (lines, meta):
    if len(lines) not in (4, 5, 6):
        raise util.ParseError(
            'second intro paragraph has the wrong number of lines: '
            '{}, expected 4-6'.format(len(lines)))

    # TODO: food optional - determine whether prof line must or must not exist based on the profession
    profs = definitions.profession
    prof_line = lines[5] if len(lines) == 6 else None
    stats = parse_stats(meta, lines[1])
    return {
        'gear': build.Gear(
            parse_weapons(lines[0], stats),
            parse_armour(lines[2], stats),
            parse_trinkets(stats),
            None), #parse_food(lines[4])),
        'traits': parse_traits(lines[3]),
        'profession options': parse_prof_options(prof_line, meta)
    }


def parse_skills (lines):
    # TODO
    # 1 paragraph: lines heal, utilities, elite
    # for rev, this is instead the legends
    return None


def parse (lines, meta):
    paragraphs = list(group_paragraphs(
        util.strip_empty_lines(lines, inner='collapse')))
    if len(paragraphs) < 3:
        raise util.ParseError('intro is incomplete')

    setup = parse_setup(paragraphs[-2], meta)
    return build.Intro(
        parse_url(paragraphs[0]),
        parse_description(paragraphs[1:-2]),
        setup['gear'],
        setup['traits'],
        parse_skills(paragraphs[-1]),
        setup['profession options'])
