import enum
from html import escape as html_escape

try:
    import docutils
    import docutils.core
    import docutils.nodes
    import docutils.parsers.rst
except ImportError:
    docutils = None

from . import api, util


def _plain_text_lines (text_body):
    return util.strip_empty_lines(text_body.source.split('\n'),
                                  inner='collapse')


def render_plain_text_plain (text_body):
    return '\n'.join(_plain_text_lines(text_body))


def render_plain_text_html (text_body):
    paragraphs = []
    for paragraph in util.group_paragraphs(_plain_text_lines(text_body)):
        paragraphs.append('<br/>\n'.join(
            html_escape(line) for line in paragraph))
    return ''.join(f'<p>{paragraph}</p>' for paragraph in paragraphs)


_rst_api_role_names = {
    api.entity.Profession: ('prof',),
    api.entity.Specialisation: ('spec',),
    api.entity.RevenantLegend: ('legend',),
    api.entity.RangerPet: ('pet',),
}


def _rst_register_api_role (
    entity_type, class_prefix, lookup, build_meta, api_storage
):
    type_id = entity_type.type_id()

    def role (name, raw_text, text, line_num, inliner, options={}, content=[]):
        try:
            entity = lookup(entity_type, text, build_meta, api_storage)
        except KeyError:
            message = inliner.reporter.error(
                f'unknown {type_id}: {text}')
            node = inliner.problematic(raw_text, raw_text, message)
            return ([node], [message])

        output = ('<span '
                  f'class="{html_escape(class_prefix + type_id, quote=True)}" '
                  f'data-api-id="{html_escape(str(entity.api_id), quote=True)}"'
                  f'>{html_escape(entity.name)}'
                  '</span>')
        node = docutils.nodes.raw(raw_text, output, format='html')
        return ([node], [])

    for name in (type_id,) + _rst_api_role_names.get(entity_type, ()):
        docutils.parsers.rst.roles.register_local_role(name, role)


def _rst_default_role_lookup (entity_type, text, build_meta, api_storage):
    return api_storage.from_id(entity_type, text, api.storage.Filters())


def _rst_skill_role_lookup (entity_type, full_text, build_meta, api_storage):
    words = full_text.split()
    try:
        prof, elite_spec = (
            api.util.lookup_profession(words[0], api_storage))
        text = ' '.join(words[1:])
    except (IndexError, KeyError):
        text = full_text
        prof = build_meta.profession
        elite_spec = build_meta.elite_spec

    S = api.entity.Skill
    filters = (S.filter_is_main +
               S.filter_profession(prof) +
               S.filter_elite_spec(elite_spec) +
               S.filter_has_build_id)

    return api_storage.from_id(entity_type, text, filters)


_rst_api_role_lookup = {
    api.entity.Skill: _rst_skill_role_lookup,
}


# not thread-safe
def render_rst_html (text_body, build_meta, api_storage, class_prefix='gw2-'):
    if docutils is None:
        raise RuntimeError('reStructuredText rendering is not supported: '
                           'Docutils is not installed')

    for entity_type in api.entity.BUILTIN_TYPES:
        lookup = _rst_api_role_lookup.get(entity_type, _rst_default_role_lookup)
        _rst_register_api_role(entity_type, class_prefix,
                               lookup, build_meta, api_storage)

    settings = {
        # throw instead of writing errors to the document (2 means warnings and
        # everything more severe)
        'halt_level': 2,
    }
    doc_parts = docutils.core.publish_parts(text_body.source,
                                            parser_name='restructuredtext',
                                            writer_name='html',
                                            settings_overrides=settings)
    return doc_parts['body']


class Renderer:
    def __init__ (self, render_fn):
        self.render = render_fn


class RenderFormat(enum.Enum):
    PLAIN_TEXT_PLAIN = Renderer(lambda t, m, s: render_plain_text_plain(t))
    PLAIN_TEXT_HTML = Renderer(lambda t, m, s: render_plain_text_html(t))
    # not thread-safe
    RST_HTML = Renderer(lambda t, m, s: render_rst_html(t, m, s))
