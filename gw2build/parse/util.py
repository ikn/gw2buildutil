import re


_title_regex = re.compile(r'(#+)([^#].*)?$')
def _parse_section_title (line):
    match = _title_regex.match(line)

    if match is not None:
        level = len(match[1])
        title = '' if match[2] is None else match[2].strip()
        return (level, title)


def split_sections (lines, first_title):
    lines_iter = iter(lines)
    next_title = first_title

    def _iter_section ():
        nonlocal next_title
        next_title = None

        for line in lines_iter:
            title = _parse_section_title(line)
            if title is None:
                yield line.rstrip()
            else:
                title_level, title_string = title
                if title_level == 1:
                    next_title = title_string
                    break
                else:
                    yield '{} {}'.format('#' * title_level, title_string)

    while next_title is not None:
        yield (next_title, _iter_section())


def strip_empty_lines (lines, leading=False, inner=False, trailing=False):
    return lines
