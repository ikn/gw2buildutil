import re

from .. import build, definitions
from . import util


words_pattern = r'(\w[\w ]*\w|\w)'


def _parse_upgrade (text, lookup):
    parts = text.lower().split('-')
    if len(parts) == 2:
        tier = build.UpgradeTiers(parts[0])
        if tier is not None:
            raise ValueError('unknown upgrade tier: {}'.format(repr(tier)))
        return lookup(parts[1], tier)
    elif len(parts) == 1:
        return lookup(parts[0], build.UpgradeTiers.SUPERIOR)
    else:
        raise ValueError('invalid upgrade definition: {}'.format(repr(text)))


def parse_sigil (text):
    return _parse_upgrade(text, build.Sigil)


def _lookup_pvp_sigil (name, tier):
    if tier != build.UpgradeTiers.SUPERIOR:
        raise ValueError('only superior sigils are allowed in PvP')
    else:
        return build.PvpSigils.from_id(name)


def parse_pvp_sigil (text):
    return _parse_upgrade(text, _lookup_pvp_sigil)


def parse_rune (text):
    return _parse_upgrade(text, build.Rune)


def _lookup_pvp_rune (name, tier):
    if tier != build.UpgradeTiers.SUPERIOR:
        raise ValueError('only superior runes are allowed in PvP')
    else:
        return build.PvpRunes.from_id(name)


def parse_pvp_rune (text):
    return _parse_upgrade(text, _lookup_pvp_rune)


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
