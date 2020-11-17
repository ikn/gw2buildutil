import re
import collections

from ... import build, api, util
from .. import parseutil

wds_pat = parseutil.words_pattern


url_pattern = re.compile(r'^http://gw2skills.net/editor/\?[A-Za-z0-9+-/]+$')

def parse_url (lines):
    if len(lines) > 1:
        raise parseutil.ParseError(
            'first intro paragraph should have only 1 line')
    if url_pattern.match(lines[0]) is None:
        raise parseutil.ParseError(
            'first intro line doesn\'t look like a valid URL')
    return lines[0]


def parse_description (paragraphs):
    return build.TextBody(
        '\n\n'.join('\n'.join(lines) for lines in paragraphs))


stats_pattern = re.compile('^'
    f'{parseutil.sep_pattern(", ", parseutil.sep_pattern(" + ", wds_pat))}'
    '$')

def parse_stats (line, meta, api_storage):
    if stats_pattern.match(line) is None:
        raise parseutil.ParseError('stats definition doesn\'t match expected '
                                   'format: {}'.format(repr(line)))

    stats_entity_type = (
        api.entity.PvpStats if meta.game_mode is build.GameModes.PVP
        else api.entity.Stats)
    gear_stats = {}
    for section in line.split(', '):
        words = section.split()
        try:
            stats = api_storage.from_id(stats_entity_type, words[0])
        except KeyError:
            raise parseutil.ParseError(f'unknown stats: {words[0]}')
        gear_groups = parseutil.parse_gear_groups(section[len(words[0]) + 1:])

        if not gear_groups:
            gear_stats[None] = stats
        for gear_group in gear_groups:
            gear_stats[gear_group] = stats

    if None not in gear_stats:
        raise parseutil.ParseError('no default stats found')
    return gear_stats


def stats_lookup (names, stats):
    for name in names:
        if name in stats:
            return stats[name]
    return stats[None]


def lookup_sigil (id_, api_storage):
    try:
        return api_storage.from_id(api.entity.Sigil, id_)
    except KeyError:
        raise parseutil.ParseError(f'unknown sigil: {id_}')


weapons_pattern = re.compile('^'
    f'(?P<types1>{wds_pat}) \\((?P<sigils1>{wds_pat}, {wds_pat})\\)'
    f'( / (?P<types2>{wds_pat}) \\((?P<sigils2>{wds_pat}, {wds_pat})\\))?'
    '$')

def parse_weapons (line, stats, meta, api_storage):
    match = weapons_pattern.match(line)
    if match is None:
        raise parseutil.ParseError('weapons definition doesn\'t match expected '
                                   'format: {}'.format(repr(line)))
    fields = match.groupdict()
    parse_sigil = (
        build.PvpSigils.from_id if meta.game_mode == build.GameModes.PVP
        else lambda text: lookup_sigil(text, api_storage))

    def build_weapon (type_, hand, sigils):
        weapon_stats = stats_lookup((type_, build.GearGroups.WEAPONS), stats)
        return build.Weapon(type_, hand, weapon_stats, sigils)

    def build_weapon_set (weapons_field, sigils_field):
        types = [build.WeaponTypes.from_id(t) for t in weapons_field.split()]
        sigils = [parse_sigil(s) for s in sigils_field.split(', ')]
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


def lookup_rune (id_, api_storage):
    try:
        return api_storage.from_id(api.entity.Rune, id_)
    except KeyError:
        raise parseutil.ParseError(f'unknown rune: {id_}')


runes_pattern = re.compile('^('
    f'(?P<single>{wds_pat})'
    '|'
    f'(?P<multi>\\d {wds_pat}( \\+ \\d {wds_pat})+)'
    ') runes$')

def parse_runes (runes_line):
    match = runes_pattern.match(runes_line)
    if match is None:
        raise parseutil.ParseError('runes definition doesn\'t match expected '
                                   'format: {}'.format(repr(runes_line)))

    fields = match.groupdict()
    if fields['single'] is not None:
        runes = collections.Counter({fields['single']: 6})
    else:
        rune_items = (item.split(' ', 1)
                      for item in fields['multi'].split(' + '))
        runes = collections.Counter(
            {type_: int(count) for count, type_ in rune_items})
    if sum(runes.values()) != 6:
        raise parseutil.ParseError(f'wrong total rune count: {dict(runes)}')
    return runes


def parse_armour (runes, stats, api_storage):
    return build.Armour([build.ArmourPiece(
        type_,
        stats_lookup((type_, build.GearGroups.ARMOUR), stats),
        lookup_rune(rune, api_storage)
    ) for type_, rune in zip(build.ArmourTypes, runes.elements())])


def parse_pvp_armour (runes, stats):
    if len(runes) > 1:
        raise parseutil.ParseError('different runes are not allowed in PvP')

    return build.PvpArmour(build.PvpRunes.from_id(next(iter(runes))))


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


traits_pattern = re.compile('^'
    f'{wds_pat}' '( [1-3]){3}'
    f'(, {wds_pat}' '( [1-3]){3}){2}'
    '$')

def parse_traits (line, api_storage):
    if traits_pattern.match(line) is None:
        raise parseutil.ParseError('traits definition doesn\'t match expected '
                                   f'format: {repr(line)}')

    specs = []
    for spec_text in line.split(', '):
        id_, *choices_text = spec_text.rsplit(' ', 3)
        choices = [build.TraitChoices.from_index(int(choice_text) - 1)
                   for choice_text in choices_text]
        try:
            spec = api_storage.from_id(api.entity.Specialisation, id_)
        except KeyError:
            raise parseutil.ParseError(f'unknown specialisation: {id_}')
        specs.append(build.SpecialisationChoices(spec, choices))

    return build.Traits(specs)


def lookup_consumable (id_, api_storage):
    try:
        return api_storage.from_id(api.entity.Food, id_)
    except KeyError:
        try:
            return api_storage.from_id(api.entity.UtilityConsumable, id_)
        except KeyError:
            raise parseutil.ParseError(f'unknown consumable: {id_}')


def parse_consumables (line, api_storage):
    consumables_text = parseutil.parse_words_seq(line, 'consumables')
    if not consumables_text or len(consumables_text) > 2:
        raise parseutil.ParseError('expected 1 or 2 consumables, got '
                                   f'{len(consumables_text)}')

    consumables = [lookup_consumable(text, api_storage)
                   for text in consumables_text]
    by_type = {}
    for c in consumables:
        t = type(c)
        if t in by_type:
                 raise util.ParseError(
                     f'multiple {t.type_id()} consumables specified: '
                     f'{by_type[t].name}, {c.name}')
        by_type[t] = c

    return build.Consumables(by_type.get(api.entity.Food),
                             by_type.get(api.entity.UtilityConsumable))


num_prof_lines = collections.defaultdict(lambda: 0, {
    'ranger': 1,
})


def lookup_ranger_pet (id_, api_storage):
    try:
        return api_storage.from_id(api.entity.RangerPet, id_)
    except KeyError:
        raise parseutil.ParseError(f'unknown ranger pet: {id_}')


def parse_ranger_options (line, api_storage):
    ids = parseutil.parse_words_seq(line, 'ranger pets')
    pets = build.RangerPets(
        [lookup_ranger_pet(id_, api_storage) for id_ in ids])
    return build.RangerOptions(pets)


def parse_prof_options (lines, meta, api_storage):
    if meta.profession.id_ == 'ranger':
        return parse_ranger_options(lines[0], api_storage)
    else:
        return None


def parse_setup (lines, meta, api_storage):
    prof_lines = num_prof_lines[meta.profession.id_]
    min_lines = 4 + prof_lines
    max_lines = 5 + prof_lines
    num_lines = len(lines)
    if num_lines not in list(range(min_lines, max_lines + 1)):
        raise parseutil.ParseError(
            'second intro paragraph has the wrong number of lines: '
            f'got {num_lines}, expected {min_lines}-{max_lines}')
    if num_lines == max_lines and meta.game_mode == build.GameModes.PVP:
        raise parseutil.ParseError('consumables are not allowed for PvP builds')

    stats = parse_stats(lines[1], meta, api_storage)
    if meta.game_mode == build.GameModes.PVP:
        gear = build.PvpGear(
            stats[None],
            parse_weapons(lines[0], stats, meta, api_storage),
            parse_pvp_armour(parse_runes(lines[2]), stats))
    else:
        gear = build.Gear(
            parse_weapons(lines[0], stats, meta, api_storage),
            parse_armour(parse_runes(lines[2]), stats, api_storage),
            parse_trinkets(stats),
            (parse_consumables(lines[4], api_storage)
            if num_lines == max_lines else build.Consumables()))

    return {
        'gear': gear,
        'traits': parse_traits(lines[3], api_storage),
        'profession options':
            parse_prof_options(lines[-prof_lines:], meta, api_storage),
    }


def lookup_revenant_legend (id_, api_storage):
    try:
        return api_storage.from_id(api.entity.RevenantLegend, id_)
    except KeyError:
        raise parseutil.ParseError(f'unknown Revenant legend: {id_}')


def parse_revenant_skills (lines, api_storage):
    if len(lines) != 1:
        raise parseutil.ParseError(
            'third intro paragraph has the wrong number of lines: '
            f'got {len(lines)}, expected 1')

    legends_text = parseutil.parse_words_seq(lines[0], 'legends', 2)
    return build.RevenantSkills([
        lookup_revenant_legend(legend_text, api_storage)
        for legend_text in legends_text])


def lookup_skill (id_, type_, meta, api_storage):
    S = api.entity.Skill
    filters = (S.filter_type(type_) +
               S.filter_profession(meta.profession) +
               S.filter_elite_spec(meta.elite_spec) +
               S.filter_has_build_id())

    try:
        return api_storage.from_id(S, id_, filters)
    except KeyError:
        raise parseutil.ParseError(f'unknown skill: {id_}')


def parse_skills (lines, meta, api_storage):
    if meta.profession.id_ == 'revenant':
        return parse_revenant_skills(lines, api_storage)

    if len(lines) != 3:
        raise parseutil.ParseError(
            'third intro paragraph has the wrong number of lines: '
            f'got {len(lines)}, expected 3')

    heal_skill_id = parseutil.parse_words_seq(lines[0], 'heal skill', 1)[0]
    utility_skill_ids = (
        parseutil.parse_words_seq(lines[1], 'utility skills', 3))
    elite_skill_id = parseutil.parse_words_seq(lines[2], 'elite skill', 1)[0]
    return build.Skills(
        lookup_skill(heal_skill_id, build.SkillTypes.HEAL, meta, api_storage),
        [lookup_skill(s, build.SkillTypes.UTILITY, meta, api_storage)
         for s in utility_skill_ids],
        lookup_skill(elite_skill_id, build.SkillTypes.ELITE, meta, api_storage))


def parse (lines, meta, api_storage):
    paragraphs = list(util.group_paragraphs(
        util.strip_empty_lines(lines, inner='collapse')))
    if len(paragraphs) < 3:
        raise util.ParseError('intro is incomplete')

    setup = parse_setup(paragraphs[-2], meta, api_storage)
    return build.Intro(
        parse_url(paragraphs[0]),
        parse_description(paragraphs[1:-2]),
        setup['gear'],
        setup['traits'],
        parse_skills(paragraphs[-1], meta, api_storage),
        setup['profession options'])
