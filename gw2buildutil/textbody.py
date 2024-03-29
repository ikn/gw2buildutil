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


def render_plain_text_plain (text_body, build_meta, api_storage, options):
    return '\n'.join(_plain_text_lines(text_body))


def render_plain_text_html (text_body, build_meta, api_storage, options):
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


def _lookup_entity (entity_types, full_text, build_meta, api_storage):
    def lookup (text, prof, elite_spec):
        S = api.entity.Skill
        filters = (S.filter_is_main() +
                   S.filter_profession(prof) +
                   S.filter_elite_spec(elite_spec) +
                   S.filter_has_build_id())
        return api_storage.from_id(entity_types, text, filters)

    words = full_text.split()
    if len(words) >= 2:
        try:
            prof, elite_spec = (
                api.util.lookup_profession(words[0], api_storage))
            return lookup(' '.join(words[1:]), prof, elite_spec)
        except KeyError:
            pass

    return lookup(full_text, build_meta.profession, build_meta.elite_spec)


def _rst_register_api_role (role_names, entity_types, class_prefix, build_meta,
                            api_storage):
    def role (name, raw_text, text, line_num, inliner, options={}, content=[]):
        try:
            entity = _lookup_entity(entity_types, text, build_meta, api_storage)
        except KeyError:
            message = inliner.reporter.error(
                f'unknown {role_names[0]}: {text}')
            node = inliner.problematic(raw_text, raw_text, message)
            return ([node], [message])

        class_name = class_prefix + type(entity).type_id()
        output = ('<span '
                  f'class="{html_escape(class_name, quote=True)}" '
                  f'data-api-id="{html_escape(str(entity.api_id), quote=True)}"'
                  f'>{html_escape(str(entity))}'
                  '</span>')
        node = docutils.nodes.raw(raw_text, output, format='html')
        return ([node], [])

    for name in role_names:
        docutils.parsers.rst.roles.register_local_role(name, role)


# not thread-safe
def render_rst_html (text_body, build_meta, api_storage, options):
    class_prefix = options.get('class prefix', 'gw2-')
    entity_types = options.get('entity types', api.entity.BUILTIN_TYPES)
    heading_level = max(1, options.get('heading level', 1))

    if docutils is None:
        raise RuntimeError('reStructuredText rendering is not supported: '
                           'Docutils is not installed')

    for entity_type in api.entity.BUILTIN_TYPES:
        role_names = ((entity_type.type_id(),) +
                      _rst_api_role_names.get(entity_type, ()))
        _rst_register_api_role(role_names, (entity_type,),
                               class_prefix, build_meta, api_storage)
    _rst_register_api_role(('entity',), entity_types,
                           class_prefix, build_meta, api_storage)

    settings = {
        # throw instead of writing errors to the document (2 means warnings and
        # everything more severe)
        'halt_level': 2,
    }
    lines = util.strip_empty_lines(text_body.source.split('\n'))
    source = '.. default-role:: entity\n\n' + '\n'.join(lines)
    doc_parts = docutils.core.publish_parts(source,
                                            parser_name='restructuredtext',
                                            writer_name='html',
                                            settings_overrides=settings)
    body = doc_parts['body']

    if heading_level != 1:
        for i in range(6, 0, -1):
            target = min(6, heading_level - 1 + i)
            body = body.replace(f'<h{i}', f'<h{target}')
            body = body.replace(f'</h{i}', f'</h{target}')

    return body


class Renderer:
    def __init__ (self, render_fn, options={}):
        self._render = render_fn
        self.options = options

    def render (self, text_body, build_meta, api_storage):
        return self._render(text_body, build_meta, api_storage, self.options)


class RenderFormat(enum.Enum):
    PLAIN_TEXT_PLAIN = render_plain_text_plain
    PLAIN_TEXT_HTML = render_plain_text_html
    # not thread-safe
    RST_HTML = render_rst_html
