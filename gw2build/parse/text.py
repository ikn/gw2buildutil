import re

from .. import build, definitions
from . import util


def _parse_upgrade (text, cls):
    parts = text.lower().split('-')
    if len(parts) == 2:
        tier = definitions.upgrade_tier.get(parts[0])
        if tier is not None:
            raise ValueError('unknown upgrade tier: {}'.format(repr(tier)))
        return cls(parts[1], tier)
    elif len(parts) == 1:
        return cls(parts[0], definitions.upgrade_tier['superior'])
    else:
        raise ValueError('invalid upgrade definition: {}'.format(repr(text)))


def parse_sigil (text):
    return _parse_upgrade(text, build.Sigil)


def parse_rune (text):
    return _parse_upgrade(text, build.Rune)


gear_groups_pattern = re.compile(r'^'
    '[\w ]+( \+ [\w ]+)*'
    '$')

def parse_gear_groups (text):
    if not text:
        return []
    if gear_groups_pattern.match(text) is None:
        raise util.ParseError('gear definition doesn\'t match expected '
                              'format: {}'.format(repr(text)))

    return [
        definitions.gear_group[group_text]
        for group_text in text.split(' + ')
    ]
