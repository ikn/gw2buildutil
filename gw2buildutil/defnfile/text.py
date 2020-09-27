import re

from .. import build
from . import util


words_pattern = r'(\w[\w\'!\- ]*[\w!]|\w)'


_gear_groups_pattern = re.compile(r'^'
    '[\w ]+( \+ [\w ]+)*'
    '$')

def parse_gear_groups (text):
    if not text:
        return []
    if _gear_groups_pattern.match(text) is None:
        raise util.ParseError('gear definition doesn\'t match expected '
                              'format: {}'.format(repr(text)))

    return [
        build.GearGroups.from_id(group_text)
        for group_text in text.split(' + ')
    ]

_words_seq_pattern = re.compile(r'^'
    f'{words_pattern}'
    r'(, ' f'{words_pattern}' r')*'
    r'$')
def parse_words_seq (text, defn_label, num=None):
    if _words_seq_pattern.match(text) is None:
        raise util.ParseError(f'{defn_label} definition doesn\'t match '
                              f'expected format: {repr(text)}')

    items = text.split(', ')
    if num is not None and len(items) != num:
        raise util.ParseError(f'expected {num} values in {defn_label} '
                              f'definition, got {len(items)}')

    return items
