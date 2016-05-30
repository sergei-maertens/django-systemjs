from __future__ import unicode_literals

import os
import logging
from collections import OrderedDict

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import SuspiciousFileOperation
from django.core.management.base import BaseCommand
from django.core.management.utils import handle_extensions
from django.core.files.storage import FileSystemStorage

from systemjs.base import System, SystemTracer
from systemjs.jspm import find_systemjs_location
from ._package_discovery import TemplateDiscoveryMixin


logger = logging.getLogger(__name__)


class Command(TemplateDiscoveryMixin, BaseCommand):
    help = "Find {% systemjs_import %} tags and bundle the JS apps."
    requires_system_checks = False

    def log(self, msg, level=2):
        """
        Small log helper
        """
        if self.verbosity >= level:
            self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument(
            '--sfx',
            action='store_true', dest='sfx',
            help="Generate self-executing bundles.")

        parser.add_argument(
            '--node-path', default='./node_modules',
            help='Path to the project `node_modules` directory')
        parser.add_argument('--minify', action='store_true', help='Let jspm minify the bundle')
        parser.add_argument('--minimal', action='store_true', help='Only (re)bundle if changes detected')

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
        parser.add_argument(
            '--no-post-process',
            action='store_false', dest='post_process', default=True,
            help="Do NOT post process collected files.")

    def handle(self, **options):
        self.symlinks = options.get('symlinks')
        self.post_process = options['post_process']
        self.minimal = options.get('minimal')

        self.verbosity = 2
        self.storage = staticfiles_storage
        self.storage.systemjs_bundling = True  # set flag to check later

        extensions = options.get('extensions') or ['html']
        self.extensions = handle_extensions(extensions)

        system_options = ['minimal', 'minify', 'sfx']

        # initialize SystemJS specific objects to process the bundles
        tracer = SystemTracer(node_path=options.get('node_path'))
        system = System(**{opt: options.get(opt) for opt in system_options})

        # discover the apps being imported in the templates
        all_apps = self.find_apps(templates=options.get('templates'))
        all_apps = set(sum(all_apps.values(), []))

        bundled_files = OrderedDict()
        # FIXME: this should be configurable, if people use S3BotoStorage for example, it needs to end up there
        storage = FileSystemStorage(settings.STATIC_ROOT, base_url=settings.STATIC_URL)
        for app in all_apps:
            # do we need to generate the bundle for this app?
            if self.minimal and not tracer.check_needs_update(app):
                self.stdout.write('Checked bundle for app \'{app}\', no changes found'.format(app=app))
                continue

            rel_path = system.bundle(app)
            if not self.storage.exists(rel_path):
                self.stderr.write('Could not bundle {app}'.format(app=app))
            else:
                self.stdout.write('Bundled {app} into {out}'.format(app=app, out=rel_path))
            bundled_files[rel_path] = (storage, rel_path)

        if self.minimal and bundled_files:
            self.stdout.write('Generating the new depcache and writing to file...')
            all_deps = {app: tracer.trace(app) for app in all_apps}
            tracer.write_depcache(all_deps)

        if self.post_process and hasattr(self.storage, 'post_process'):
            # post-process system.js if it's within settings.STATIC_ROOT
            systemjs_path = find_systemjs_location()
            try:
                within_static_root = self.storage.exists(systemjs_path)
            except SuspiciousFileOperation:
                within_static_root = False
            if within_static_root:
                relative = os.path.relpath(systemjs_path, settings.STATIC_ROOT)
                bundled_files[relative] = (storage, relative)

            processor = self.storage.post_process(bundled_files, dry_run=False)
            for original_path, processed_path, processed in processor:
                if isinstance(processed, Exception):  # pragma: no cover
                    self.stderr.write("Post-processing '%s' failed!" % original_path)
                    # Add a blank line before the traceback, otherwise it's
                    # too easy to miss the relevant part of the error message.
                    self.stderr.write("")
                    raise processed
                if processed:  # pragma: no cover
                    self.log("Post-processed '%s' as '%s'" %
                             (original_path, processed_path), level=1)
                else:
                    self.log("Skipped post-processing '%s'" % original_path)  # pragma: no cover
