import re

from ... import build, util
from .. import parseutil


uptimes_pattern = re.compile('^'
    '(\d{1,3}% )?(5|10)-[a-z]+(, (\d{1,3}% )?(5|10)-[a-z]+)*'
    '$')

def parse_uptime (line):
    uptimes = []
    if uptimes_pattern.match(line) is None:
        raise parseutil.ParseError('boon uptime definition doesn\'t match '
                                   f'expected format: {repr(line)}')

    for boon_uptime_text in line.split(', '):
        if ' ' in boon_uptime_text:
            uptime_text, rest = boon_uptime_text.split(' ')
        else:
            uptime_text = None
            rest = boon_uptime_text
        target_text, boon_text = rest.split('-')

        uptime = None if uptime_text is None else int(uptime_text[:-1])
        target = build.BoonTargets.from_id(target_text)
        if target is None:
            raise parseutil.ParseError(
                'boon uptime definition has a missing or incorrect target '
                'count identifier: {}'.format(repr(boon_uptime_text)))
        boon = build.Boons.from_id(boon_text)
        if boon is None:
            raise parseutil.ParseError(
                'boon uptime definition has a missing or incorrect boon '
                'identifier: {}'.format(repr(boon_uptime_text)))
        uptimes.append(build.BoonUptime(boon, target, uptime))

    uptimes.sort(key = lambda uptime: (uptime.boon.name, uptime.target.name))
    return uptimes


def parse (lines, meta, api_storage):
    paragraphs = list(util.group_paragraphs(
        util.strip_empty_lines(lines, inner='collapse')))
    if len(paragraphs) < 1:
        raise parseutil.ParseError('boon notes is incomplete')

    boon_variants = [build.BoonUptimeVariant(parse_uptime(line))
                     for line in paragraphs[0]]

    # TODO: other lines - variants can change build and usage/rotation
    return build.BoonNotes(boon_variants)
