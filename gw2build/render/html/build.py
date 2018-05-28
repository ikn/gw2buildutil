import io


def render_to_fileobj (build, f):
    import pprint
    f.write(pprint.pformat(build.__dict__))
    f.write('\n')


def render_to_str (build):
    f = io.StringIO()
    render_to_fileobj(build, f)
    return f.getvalue()
