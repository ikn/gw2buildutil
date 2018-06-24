from .. import build, definitions


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
