import io
import re

from .. import api, build
from . import parseutil, section

_SKIP_SECTION = object()


title_pattern = re.compile('^'
    f'(?P<mode>{parseutil.words_pattern}) '
    f'(?P<prof>{parseutil.word_pattern}) '
    '\\((?P<labels>'
         f'{parseutil.sep_pattern(", ", parseutil.words_pattern)}'
         ')\\)'
    '$')

def parse_title (title, api_storage):
    match = title_pattern.match(title)
    if match is None:
        raise parseutil.ParseError('title doesn\'t match expected format: '
                                   '{}'.format(repr(title)))
    fields = match.groupdict()

    game_mode = build.GameModes.from_id(fields['mode'])
    if game_mode is None:
        raise parseutil.ParseError('title doesn\'t start with a known '
                                   f'game modes identifier: {repr(title)}')
    try:
        profession, elite_spec = (
            api.util.lookup_profession(fields['prof'], api_storage))
    except KeyError:
        raise parseutil.ParseError('title has a missing or incorrect '
                                   f'profession identifier: {repr(title)}')

    labels = [l.strip() for l in fields['labels'].split(',')]
    return build.BuildMetadata(game_mode, profession, elite_spec, labels)


section_parsers = {
    'intro': section.intro,
    'alternatives': section.alternatives,
    'usage': section.usage,
    'notes': section.notes,
    'boon notes': section.boonnotes,
    'encounters': section.encounters,
    'calculation': _SKIP_SECTION,
}


def parse_body (f, meta, api_storage):
    lines = (line if isinstance(line, str) else line.decode('utf-8')
             for line in f)
    build_data = {}

    for title, section_lines in parseutil.split_sections(lines, 'intro'):
        section_module = section_parsers.get(title)
        if section_module is None:
            raise parseutil.ParseError(
                'unknown section: {}'.format(repr(title)))
        elif section_module is _SKIP_SECTION:
            for line in section_lines:
                pass
        else:
            build_data[title.replace(' ', '_')] = (
                section_module.parse(section_lines, meta, api_storage))

    return build.Build(meta, **build_data)
