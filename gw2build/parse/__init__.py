import io
import re

from .. import build, definitions
from . import util, section


title_pattern = re.compile(r'^'
    '(?P<mode>.+) '
    '(?P<prof>\w+) '
    '\((?P<labels>[ \w]+(, [ \w]+)*)\)'
    '$')

def parse_title (title):
    match = title_pattern.match(title)
    if match is None:
        raise util.ParseError('title doesn\'t match expected format: '
                              '{}'.format(repr(title)))
    fields = match.groupdict()

    game_modes = definitions.game_modes.get(fields['mode'])
    if game_modes is None:
        raise util.ParseError('title doesn\'t start with a known '
                              'game modes identifier: {}'.format(repr(title)))
    profession = definitions.profession.get(fields['prof'])
    if profession is None:
        raise util.ParseError('title has a missing or incorrect profession '
                              'identifier: {}'.format(repr(title)))
    labels = [l.strip() for l in fields['labels'].split(',')]
    return build.BuildMetadata(game_modes, profession, labels)


section_parsers = {
    'intro': section.intro,
    'alternatives': section.alternatives,
    'usage': section.usage,
    'notes': section.notes,
    'boon notes': section.boonnotes,
    'encounters': section.encounters,
    'calculation': False,
}


def parse_body (f, meta):
    lines = (line if isinstance(line, str) else line.decode('utf-8')
             for line in f)
    build_data = {}

    for title, section_lines in util.split_sections(lines, 'intro'):
        section_module = section_parsers.get(title)
        if section_module is None:
            raise util.ParseError('unknown section: {}'.format(repr(title)))
        elif section_module is False:
            for line in section_lines:
                pass
        else:
            build_data[title.replace(' ', '_')] = (
                section_module.parse(section_lines, meta))

    return build.Build(meta, **build_data)
