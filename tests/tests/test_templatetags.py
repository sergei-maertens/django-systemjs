from __future__ import unicode_literals

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.template import Context, engines, TemplateSyntaxError
from django.utils.six.moves.urllib.parse import urljoin


django_engine = engines['django']


class TemplateTagTests(SimpleTestCase):

    TEMPLATE = """{% load system_tags %}{% systemjs_import 'myapp/main' %}"""

    def setUp(self):
        self.template = django_engine.from_string(self.TEMPLATE)
        self.context = Context()

    def _render(self):
        return self.template.render(self.context)

    @override_settings(SYSTEMJS_ENABLED=False)
    def test_debug(self):
        rendered = self._render()
        self.assertEqual(rendered, """<script type="text/javascript">System.import('myapp/main.js');</script>""")

    @override_settings(SYSTEMJS_ENABLED=True, SYSTEMJS_OUTPUT_DIR='SJ')
    def test_normal(self):
        rendered = self._render()
        expected_url = urljoin(settings.STATIC_URL, 'SJ/myapp/main.js')
        self.assertEqual(rendered, """<script type="text/javascript" src="{0}"></script>""".format(expected_url))

    def test_incorrect_number_arguments(self):
        with self.assertRaises(TemplateSyntaxError):
            django_engine.from_string("""{% load system_tags %}{% systemjs_import %}""")

    @override_settings(SYSTEMJS_ENABLED=False, SYSTEMJS_DEFAULT_JS_EXTENSIONS=False)
    def test_debug_module_without_extension_no_default(self):
        rendered = self._render()
        self.assertEqual(rendered, """<script type="text/javascript">System.import('myapp/main');</script>""")

        self.template = django_engine.from_string("""{% load system_tags %}{% systemjs_import 'myapp/main.js' %}""")
        rendered = self._render()
        self.assertEqual(rendered, """<script type="text/javascript">System.import('myapp/main.js');</script>""")

    @override_settings(SYSTEMJS_ENABLED=False, SYSTEMJS_DEFAULT_JS_EXTENSIONS=True)
    def test_debug_module_without_extension_default_js(self):
        rendered = self._render()
        self.assertEqual(rendered, """<script type="text/javascript">System.import('myapp/main.js');</script>""")

        self.template = django_engine.from_string("""{% load system_tags %}{% systemjs_import 'myapp/main.js' %}""")
        rendered = self._render()
        self.assertEqual(rendered, """<script type="text/javascript">System.import('myapp/main.js');</script>""")

    @override_settings(SYSTEMJS_ENABLED=True, SYSTEMJS_OUTPUT_DIR='SJ')
    def test_script_tag_attributes(self):
        template = """{% load system_tags %}{% systemjs_import 'myapp/main' async foo="bar" %}"""
        template = django_engine.from_string(template)
        rendered = template.render(self.context)
        expected_url = urljoin(settings.STATIC_URL, 'SJ/myapp/main.js')
        self.assertHTMLEqual(
            rendered,
            """<script async foo="bar" type="text/javascript" src="{0}"></script>""".format(expected_url)
        )
