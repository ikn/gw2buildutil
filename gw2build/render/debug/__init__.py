import json
import pprint

import jsonpickle


def render_body (build, f):
    simple_build = json.loads(jsonpickle.encode(build, unpicklable=False))
    pprint.pprint(simple_build, stream=f, width=100)
