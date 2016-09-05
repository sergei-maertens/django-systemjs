"""
Taken from djangoproject/django docs.
"""

"""
Sphinx plugins for Django documentation.
"""
import json
import os
import re

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.domains.std import Cmdoption
from sphinx.util.compat import Directive
from sphinx.util.console import bold
from sphinx.util.nodes import set_source_info
from sphinx.writers.html import SmartyPantsHTMLTranslator

# RE for option descriptions without a '--' prefix
simple_option_desc_re = re.compile(
    r'([-_a-zA-Z0-9]+)(\s*.*?)(?=,\s+(?:/|-|--)|$)')


def setup(app):
    app.add_directive('versionadded', VersionDirective)
    app.add_directive('versionchanged', VersionDirective)
    return {'parallel_read_safe': True}


class VersionDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        if len(self.arguments) > 1:
            msg = """Only one argument accepted for directive '{directive_name}::'.
            Comments should be provided as content,
            not as an extra argument.""".format(directive_name=self.name)
            raise self.error(msg)

        env = self.state.document.settings.env
        ret = []
        node = addnodes.versionmodified()
        ret.append(node)
        node['version'] = self.arguments[0]
        node['type'] = self.name
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        env.note_versionchange(node['type'], node['version'], node, self.lineno)
        return ret


class DjangoHTMLTranslator(SmartyPantsHTMLTranslator):

    version_text = {
        'versionchanged': 'Changed in %s',
        'versionadded': 'Added in %s',
    }

    def visit_versionmodified(self, node):
        self.body.append(
            self.starttag(node, 'div', CLASS=node['type'])
        )
        version_text = self.version_text.get(node['type'])
        if version_text:
            title = "%s%s" % (
                version_text % node['version'],
                ":" if len(node) else "."
            )
            self.body.append('<span class="title">%s</span> ' % title)

    def depart_versionmodified(self, node):
        self.body.append("</div>\n")
