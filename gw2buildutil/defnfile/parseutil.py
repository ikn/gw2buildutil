import re

from .. import build


word_pattern = r'[\w"\'!\-]+'
words_pattern = f'{word_pattern}' r'( ' f'{word_pattern}' r')*'


class ParseError (ValueError):
    pass


def sep_pattern (sep, item_pattern):
    return (f'{item_pattern}'
            r'(' f'{re.escape(sep)}{item_pattern}' r')*')


_gear_groups_pattern = re.compile('^'
    f'{sep_pattern(" + ", words_pattern)}'
    '$')

def parse_gear_groups (text):
    if not text:
        return []
    if _gear_groups_pattern.match(text) is None:
        raise ParseError('gear definition doesn\'t match expected '
                         f'format: {repr(text)}')

    return [
        build.GearGroups.from_id(group_text)
        for group_text in text.split(' + ')
    ]

_words_pattern = re.compile(words_pattern)
def parse_words_seq (text, defn_label, num=None):
    if _words_pattern.match(text) is None:
        raise ParseError(f'{defn_label} definition doesn\'t match '
                         f'expected format: {repr(text)}')

    items = text.split(', ')
    if num is not None and len(items) != num:
        raise ParseError(f'expected {num} values in {defn_label} '
                         f'definition, got {len(items)}')
    return items


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
