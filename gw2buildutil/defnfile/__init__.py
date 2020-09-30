import io
import re

from .. import api, build
from . import util, text as parse_text, section

_SKIP_SECTION = object()


title_pattern = re.compile('^'
    f'(?P<mode>{parse_text.words_pattern}) '
    f'(?P<prof>{parse_text.word_pattern}) '
    '\\((?P<labels>'
         f'{parse_text.sep_pattern(", ", parse_text.words_pattern)}'
         ')\\)'
    '$')

def parse_title (title, api_storage):
    match = title_pattern.match(title)
    if match is None:
        raise util.ParseError('title doesn\'t match expected format: '
                              '{}'.format(repr(title)))
    fields = match.groupdict()

    game_mode = build.GameModes.from_id(fields['mode'])
    if game_mode is None:
        raise util.ParseError('title doesn\'t start with a known '
                              'game modes identifier: {}'.format(repr(title)))

    try:
        profession = api_storage.from_id(api.entity.Profession, fields['prof'])
    except KeyError:
        try:
            elite_spec = api_storage.from_id(
                api.entity.Specialisation, fields['prof'])
        except KeyError:
            elite_spec = None
        if elite_spec is None or not elite_spec.is_elite:
            raise util.ParseError('title has a missing or incorrect profession '
                                  f'identifier: {repr(title)}')
        else:
            profession = elite_spec.profession
    else:
        elite_spec = None

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

    for title, section_lines in util.split_sections(lines, 'intro'):
        section_module = section_parsers.get(title)
        if section_module is None:
            raise util.ParseError('unknown section: {}'.format(repr(title)))
        elif section_module is _SKIP_SECTION:
            for line in section_lines:
                pass
        else:
            build_data[title.replace(' ', '_')] = (
                section_module.parse(section_lines, meta, api_storage))

    return build.Build(meta, **build_data)
