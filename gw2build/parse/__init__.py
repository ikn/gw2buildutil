import io

from .. import build, definitions
from . import util, section


class ParseError (ValueError):
    pass


def parse_title (title):
    start_parens = title.find('(')
    if start_parens < 0:
        raise ParseError('title has no labels section: {}'.format(repr(title)))
    title_base = title[:start_parens].strip()
    title_rest = title[start_parens:]

    end_parens = title_rest.find(')')
    if end_parens < 0:
        raise ParseError('title has mismatched parentheses: ' \
                            '{}'.format(repr(title)))
    title_suffix = title_rest[end_parens + 1:].strip()
    if title_suffix:
        raise ParseError('title has trailing characters: ' \
                            '{}'.format(repr(title_suffix)))

    game_modes_ids = [id_ for id_ in definitions.game_modes
                     if title_base.startswith(id_)]
    if not game_modes_ids:
        raise ParseError('title doesn\'t start with a known ' \
                         'game modes identifier: {}'.format(repr(title)))
    game_modes_id = game_modes_ids[0]
    game_modes = definitions.game_modes[game_modes_id]

    profession_id = title_base[len(game_modes_id):].strip()
    profession = definitions.profession.get(profession_id)
    if profession is None:
        raise ParseError('title has a missing or incorrect profession ' \
                         'identifier: {}'.format(repr(profession_id)))

    labels = [l.strip() for l in title_rest[1:end_parens].split(',')]

    return build.BuildMetadata(game_modes, profession, labels)


section_parsers = {
    'intro': section.intro,
    'alternatives': section.alternatives,
    'usage': section.usage,
    'notes': section.notes,
    'encounters': section.encounters,
}


def parse_body (f, meta):
    lines = (line if isinstance(line, str) else line.decode('utf-8')
             for line in f)
    build_data = {}

    for title, section_lines in util.split_sections(lines, 'intro'):
        section_module = section_parsers.get(title)
        if section_module is None:
            raise ParseError('unknown section: {}'.format(repr(title)))
        else:
            build_data[title] = section_module.parse(section_lines, meta)

    return build.Build(**build_data)
