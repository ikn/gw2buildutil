import re

from .. import build
from . import util


word_pattern = r'[\w"\'!\-]+'
words_pattern = f'{word_pattern}' r'( ' f'{word_pattern}' r')*'


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
        raise util.ParseError('gear definition doesn\'t match expected '
                              f'format: {repr(text)}')

    return [
        build.GearGroups.from_id(group_text)
        for group_text in text.split(' + ')
    ]

_words_pattern = re.compile(words_pattern)
def parse_words_seq (text, defn_label, num=None):
    if _words_pattern.match(text) is None:
        raise util.ParseError(f'{defn_label} definition doesn\'t match '
                              f'expected format: {repr(text)}')

    items = text.split(', ')
    if num is not None and len(items) != num:
        raise util.ParseError(f'expected {num} values in {defn_label} '
                              f'definition, got {len(items)}')

    return items
