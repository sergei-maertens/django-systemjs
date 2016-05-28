"""
Mixin for various command to retreive locations of systemjs_import calls.
"""
from __future__ import unicode_literals

import io
import os
import re

from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.utils import handle_extensions
from django.template import loader, TemplateDoesNotExist
from django.template.base import TOKEN_BLOCK
from django.template.loaders.app_directories import get_app_template_dirs

from systemjs.compat import Lexer
from systemjs.templatetags.system_tags import SystemImportNode


SYSTEMJS_TAG_RE = re.compile(r"""systemjs_import\s+(['\"])(?P<app>.*)\1""")

RESOLVE_CONTEXT = {}


class TemplateDiscoveryMixin(object):

    def discover_templates(self):
        template_dirs = list(get_app_template_dirs('templates'))
        for config in settings.TEMPLATES:
            # only support vanilla Django templates
            if config['BACKEND'] != 'django.template.backends.django.DjangoTemplates':
                continue
            template_dirs += list(config['DIRS'])

        all_files = []
        for template_dir in template_dirs:
            for dirpath, dirnames, filenames in os.walk(template_dir, topdown=True, followlinks=self.symlinks):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in self.extensions:
                        continue
                    all_files.append(filepath)

        return all_files

    def find_apps(self, templates=None):
        """
        Crawls the (specified) template files and extracts the apps.

        If `templates` is specified, the template loader is used and the template
        is tokenized to extract the SystemImportNode. An empty context is used
        to resolve the node variables.
        """
        all_apps = []
        if not templates:

            all_files = self.discover_templates()
            for fp in all_files:
                with io.open(fp, 'r', encoding=settings.FILE_CHARSET) as template_file:
                    src_data = template_file.read()

                for t in Lexer(src_data).tokenize():
                    if t.token_type == TOKEN_BLOCK:
                        imatch = SYSTEMJS_TAG_RE.match(t.contents)
                        if imatch:
                            all_apps.append(imatch.group('app'))
        else:
            for tpl in templates:
                try:
                    template = loader.get_template(tpl)
                except TemplateDoesNotExist:
                    raise CommandError('Template \'%s\' does not exist' % tpl)
                import_nodes = template.template.nodelist.get_nodes_by_type(SystemImportNode)
                for node in import_nodes:
                    app = node.path.resolve(RESOLVE_CONTEXT)
                    if not app:
                        self.stdout.write(self.style.WARNING(
                            '{tpl}: Could not resolve path with context {ctx}, skipping.'.format(
                                tpl=tpl, ctx=RESOLVE_CONTEXT)
                        ))
                        continue
                    all_apps.append(app)

        return all_apps
