import re


class ParseError (ValueError):
    pass


_title_regex = re.compile(r'(#+)([^#].*)?$')
def _parse_section_title (line):
    match = _title_regex.match(line)

    if match is not None:
        level = len(match[1])
        title = '' if match[2] is None else match[2].strip()
        return (level, title)


# rstrip()s lines
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


def strip_empty_lines (lines, leading=True, trailing=True, inner=None):
    in_leading = True
    empty_count = 0

    for line in lines:
        if not line:
            if not (leading and in_leading):
                empty_count += 1

        else:
            if inner == 'all' and not in_leading:
                pass
            elif inner == 'collapse' and not in_leading:
                if empty_count > 0:
                    yield ''
            else: # inner is None or in_leading
                for i in range(empty_count):
                    yield ''

            empty_count = 0
            in_leading = False
            yield line

    if not trailing:
        for i in range(empty_count):
            yield ''


def group_paragraphs (lines):
    paragraph = []
    for line in lines:
        if line:
            paragraph.append(line)
        else:
            yield paragraph
            paragraph = []
    yield paragraph
