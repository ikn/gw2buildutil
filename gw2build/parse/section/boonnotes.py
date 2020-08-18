import re

from ... import build, definitions
from .. import util


uptimes_pattern = re.compile(r'^'
    '(\d{1,3}% )?(5|10)-[a-z]+(, (\d{1,3}% )?(5|10)-[a-z]+)*'
    '$')

def parse_uptime (line):
    # 85% 5-alacrity, 40% 10-alacrity, 5-quickness, 40% 10-quickness
    uptimes = []
    if uptimes_pattern.match(line) is None:
        raise util.ParseError('boon uptime definition doesn\'t match expected '
                              'format: {}'.format(repr(line)))

    for boon_uptime_text in line.split(', '):
        if ' ' in boon_uptime_text:
            uptime_text, rest = boon_uptime_text.split(' ')
        else:
            uptime_text = None
            rest = boon_uptime_text
        target_text, boon_text = rest.split('-')

        uptime = None if uptime_text is None else int(uptime_text[:-1])
        target = definitions.boon_targets.get(target_text)
        if target is None:
            raise util.ParseError(
                'boon uptime definition has a missing or incorrect target '
                'count identifier: {}'.format(repr(boon_uptime_text)))
        boon = definitions.boons.get(boon_text)
        if boon is None:
            raise util.ParseError(
                'boon uptime definition has a missing or incorrect boon '
                'identifier: {}'.format(repr(boon_uptime_text)))
        uptimes.append(build.BoonUptime(boon, target, uptime))

    uptimes.sort(key = lambda uptime: (uptime.boon.name, uptime.target.name))
    return uptimes


def parse (lines, meta):
    lines = util.strip_empty_lines(lines, inner='all')
    try:
        boon_uptimes = parse_uptime(next(lines))
    except StopIteration:
        raise util.ParseError('boon notes is incomplete')

    # TODO: other lines
    return build.BoonNotes(boon_uptimes)
