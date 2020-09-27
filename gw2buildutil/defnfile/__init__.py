import io
import re

from .. import api, build
from . import util, section

_SKIP_SECTION = object()


title_pattern = re.compile(r'^'
    '(?P<mode>.+) '
    '(?P<prof>\w+) '
    '\((?P<labels>[ \w]+(, [ \w]+)*)\)'
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
        elite_spec = api_storage.from_id(
            api.entity.Specialisation, fields['prof'])
        if not elite_spec.is_elite:
            raise util.ParseError('title has a missing or incorrect profession '
                                  'identifier: {}'.format(repr(title)))
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
