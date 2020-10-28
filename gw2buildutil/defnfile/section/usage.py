from ... import build


def parse (lines, meta, api_storage):
    return build.TextBody('\n'.join(lines))
