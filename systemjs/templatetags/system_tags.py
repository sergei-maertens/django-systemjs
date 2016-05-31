from __future__ import unicode_literals

import posixpath

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from systemjs.base import System

register = template.Library()


class SystemImportNode(template.Node):

    def __init__(self, path):
        self.path = path

    def render(self, context):
        """
        Build the filepath by appending the extension.
        """
        module_path = self.path.resolve(context)
        if not settings.SYSTEMJS_ENABLED:
            if settings.SYSTEMJS_DEFAULT_JS_EXTENSIONS:
                name, ext = posixpath.splitext(module_path)
                if not ext:
                    module_path = '{}.js'.format(module_path)
            tpl = """<script type="text/javascript">System.import('{app}');</script>"""
            return tpl.format(app=module_path)

        # else: create a bundle
        rel_path = System.get_bundle_path(module_path)
        url = staticfiles_storage.url(rel_path)
        return """<script type="text/javascript" src="{url}"></script>""".format(url=url)

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()

        if len(bits) != 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (js module, without extension)" % bits[0])

        # for 'as varname' support, check django.templatetags.static
        path = parser.compile_filter(bits[1])
        return cls(path)


@register.tag
def systemjs_import(parser, token):
    """
    Import a Javascript module via SystemJS, bundling the app.

    Syntax::

        {% systemjs_import 'path/to/file' %}

    Example::

        {% systemjs_import 'mydjangoapp/js/myapp' %}

    Which would be rendered like::

        <script type="text/javascript" src="/static/CACHE/mydjangoapp.js.min.myapp.js"></script>

    where /static/CACHE can be configured through settings.

    In DEBUG mode, the result would be

        <script type="text/javascript">System.import('mydjangoapp/js/myapp.js');</script>
    """

    return SystemImportNode.handle_token(parser, token)
