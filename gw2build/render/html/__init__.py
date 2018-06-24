def render_body (build, f):
    import pprint
    f.write(pprint.pformat(build.__dict__))
    f.write('\n')
    f.write(pprint.pformat(build.metadata.__dict__))
    f.write('\n')
    f.write(pprint.pformat(build.intro.__dict__))
    f.write('\n')
    f.write(pprint.pformat(build.intro.gear.__dict__))
    f.write('\n')
