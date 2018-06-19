from .. import util


def parse (lines, meta):
    for title, section_lines in util.split_sections(lines, None):
        for line in util.strip_empty_lines(inner='all'):
            pass
