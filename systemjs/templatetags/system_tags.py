from __future__ import unicode_literals

import posixpath
import re

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms.utils import flatatt
from django.template.base import token_kwargs

from systemjs.base import System

register = template.Library()


# Regex for token keyword arguments
kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")


class SystemImportNode(template.Node):

    def __init__(self, path, tag_attrs=None):
        self.path = path
        self.tag_attrs = tag_attrs

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

            if settings.SYSTEMJS_SERVER_URL:
                tpl = """<script src="{url}{app}" type="text/javascript"></script>"""
            else:
                tpl = """<script type="text/javascript">System.import('{app}');</script>"""
            return tpl.format(app=module_path, url=settings.SYSTEMJS_SERVER_URL)

        # else: create a bundle
        rel_path = System.get_bundle_path(module_path)
        url = staticfiles_storage.url(rel_path)

        tag_attrs = {'type': 'text/javascript'}
        for key, value in self.tag_attrs.items():
            if not isinstance(value, bool):
                value = value.resolve(context)
            tag_attrs[key] = value

        return """<script{attrs} src="{url}"></script>""".format(
            url=url, attrs=flatatt(tag_attrs)
        )

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()
        attrs = {}

        if len(bits) < 2:
            raise template.TemplateSyntaxError("'%s' takes at least one argument (js module)" % bits[0])

        if len(bits) > 2:
            for bit in bits[2:]:
                # First we try to extract a potential kwarg from the bit
                kwarg = token_kwargs([bit], parser)
                if kwarg:
                    attrs.update(kwarg)
                else:
                    attrs[bit] = True  # for flatatt

        path = parser.compile_filter(bits[1])
        return cls(path, tag_attrs=attrs)


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
