def render_body (build, f):
    import pprint
    f.write(pprint.pformat(build.__dict__))
    f.write('\n')
