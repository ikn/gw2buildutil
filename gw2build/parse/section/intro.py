import re

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


def parse_stats (line):
    # TODO
    return {None: None}


def stats_lookup (names, stats):
    for name in names:
        if name in stats:
            return stats[name]
    return stats[None]


weapons_pattern = re.compile(r'^' \
    '(?P<types1>\w+( \w+)?) \((?P<sigils1>\w+ \w+)\)' \
    '( / (?P<types2>\w+( \w+)?) \((?P<sigils2>\w+ \w+)\))?' \
    '$')

def parse_weapons (line, stats):
    match = weapons_pattern.match(line)
    if match is None:
        raise util.ParseError('weapons definition doesn\'t match expected ' \
                              'format: {}'.format(repr(line)))
    fields = match.groupdict()
    def_hand = definitions.weapon_hand

    def build_weapon (type_, hand, sigils):
        weapon_stats = stats_lookup((type_, 'weapon'), stats)
        return build.Weapon(type_, hand, weapon_stats, sigils)

    def build_weapon_hand (weapons_field, sigils_field):
        types = [definitions.weapon_type[t] for t in weapons_field.split()]
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


def parse_armour (line, stats):
    # TODO
    return None


def parse_trinkets (stats):
    # TODO
    return None


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
    if len(lines) not in (5, 6):
        raise util.ParseError(
            'second intro paragraph has the wrong number of lines: ' \
            '{}, expected 5 or 6'.format(len(lines)))

    profs = definitions.profession
    prof_line = lines[5] if len(lines) == 6 else None
    stats = parse_stats(lines[1])
    return {
        'gear': build.Gear(
            parse_weapons(lines[0], stats),
            parse_armour(lines[2], stats),
            parse_trinkets(stats),
            parse_food(lines[4])),
        'traits': parse_traits(lines[3]),
        'profession options': parse_prof_options(prof_line, meta)
    }


def parse_skills (lines):
    # 1 paragraph: lines heal, utilities, elite
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
