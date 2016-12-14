"""
Mixin for various command to retreive locations of systemjs_import calls.
"""
from __future__ import unicode_literals

import io
import os
import re
from collections import OrderedDict

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

    def add_arguments(self, parser):
        tpl_group = parser.add_mutually_exclusive_group()
        tpl_group.add_argument(
            '--extension', '-e', dest='extensions',
            help='The file extension(s) to examine (default: "html"). Separate '
                 'multiple extensions with commas, or use -e multiple times.',
            action='append')
        tpl_group.add_argument(
            '--template', '-t', dest='templates',
            help='The templates to examine. Separate multiple template names with'
                 'commas, or use -t multiple times',
            action='append')

        parser.add_argument(
            '--symlinks', '-s', action='store_true', dest='symlinks',
            default=False, help='Follows symlinks to directories when examining '
                                'source code and templates for SystemJS imports.')

        super(TemplateDiscoveryMixin, self).add_arguments(parser)

    def handle(self, **options):
        self.symlinks = options.get('symlinks')
        extensions = options.get('extensions') or ['html']
        self.extensions = handle_extensions(extensions)

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
                    template_name = os.path.relpath(filepath, template_dir)
                    all_files.append((template_name, filepath))

        return all_files

    def find_apps(self, templates=None):
        """
        Crawls the (specified) template files and extracts the apps.

        If `templates` is specified, the template loader is used and the template
        is tokenized to extract the SystemImportNode. An empty context is used
        to resolve the node variables.
        """

        all_apps = OrderedDict()

        if not templates:
            all_files = self.discover_templates()
            for tpl_name, fp in all_files:
                # this is the most performant - a testcase that used the loader with tpl_name
                # was about 8x slower for a project with ~5 apps in different templates :(
                with io.open(fp, 'r', encoding=settings.FILE_CHARSET) as template_file:
                    src_data = template_file.read()

                for t in Lexer(src_data).tokenize():
                    if t.token_type == TOKEN_BLOCK:
                        imatch = SYSTEMJS_TAG_RE.match(t.contents)
                        if imatch:
                            all_apps.setdefault(tpl_name, [])
                            all_apps[tpl_name].append(imatch.group('app'))
        else:
            for tpl_name in templates:
                try:
                    template = loader.get_template(tpl_name)
                except TemplateDoesNotExist:
                    raise CommandError('Template \'%s\' does not exist' % tpl_name)
                import_nodes = template.template.nodelist.get_nodes_by_type(SystemImportNode)
                for node in import_nodes:
                    app = node.path.resolve(RESOLVE_CONTEXT)
                    if not app:
                        self.stdout.write(self.style.WARNING(
                            '{tpl}: Could not resolve path with context {ctx}, skipping.'.format(
                                tpl=tpl_name, ctx=RESOLVE_CONTEXT)
                        ))
                        continue
                    all_apps.setdefault(tpl_name, [])
                    all_apps[tpl_name].append(app)

        return all_apps


class BundleOptionsMixin(object):

    def add_arguments(self, parser):
        super(BundleOptionsMixin, self).add_arguments(parser)

        parser.add_argument(
            '--sfx',
            action='store_true', dest='sfx',
            help="Generate self-executing bundles.")

        parser.add_argument('--node-path', help='Path to the project `node_modules` directory')
        parser.add_argument('--minify', action='store_true', help='Let jspm minify the bundle')
        parser.add_argument('--minimal', action='store_true', help='Only (re)bundle if changes detected')
        parser.add_argument('--skip-source-maps', action='store_true', help='Skip source maps generation')

    def get_system_opts(self, options):
        system_options = ['minimal', 'minify', 'sfx', 'skip_source_maps']
        return {opt: options.get(opt) for opt in system_options}
