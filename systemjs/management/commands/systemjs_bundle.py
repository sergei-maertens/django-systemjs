from __future__ import unicode_literals

import io
import os
import re
from collections import OrderedDict

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand
from django.core.management.utils import handle_extensions
from django.core.files.storage import FileSystemStorage
from django.template.base import TOKEN_BLOCK
from django.template.loaders.app_directories import get_app_template_dirs

from systemjs.base import System
from systemjs.compat import Lexer


SYSTEMJS_TAG_RE = re.compile(r"""systemjs_import\s+(['\"])(?P<app>.*)\1""")


class Command(BaseCommand):
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
            '--extension', '-e', dest='extensions',
            help='The file extension(s) to examine (default: "html"). Separate '
                 'multiple extensions with commas, or use -e multiple times.',
            action='append')
        parser.add_argument(
            '--symlinks', '-s', action='store_true', dest='symlinks',
            default=False, help='Follows symlinks to directories when examining '
                                'source code and templates for translation strings.')
        parser.add_argument(
            '--no-post-process',
            action='store_false', dest='post_process', default=True,
            help="Do NOT post process collected files.")

    def handle(self, **options):
        self.verbosity = 2
        self.storage = staticfiles_storage
        extensions = options.get('extensions') or ['html']
        self.symlinks = options.get('symlinks')
        self.post_process = options['post_process']
        # self.post_processed_files = []

        self.extensions = handle_extensions(extensions)

        template_dirs = list(get_app_template_dirs('templates'))
        for config in settings.TEMPLATES:
            # only support vanilla Django templates
            if config['BACKEND'] != 'django.template.backends.django.DjangoTemplates':
                continue
            template_dirs += list(config['DIRS'])

        # find all template files

        all_files = []
        for template_dir in template_dirs:
            for dirpath, dirnames, filenames in os.walk(template_dir, topdown=True, followlinks=self.symlinks):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext not in self.extensions:
                        continue
                    all_files.append(filepath)

        all_apps = []
        for fp in all_files:
            with io.open(fp, 'r', encoding=settings.FILE_CHARSET) as template_file:
                src_data = template_file.read()

            for t in Lexer(src_data).tokenize():
                if t.token_type == TOKEN_BLOCK:
                    imatch = SYSTEMJS_TAG_RE.match(t.contents)
                    if imatch:
                        all_apps.append(imatch.group('app'))

        bundled_files = OrderedDict()
        storage = FileSystemStorage(settings.STATIC_ROOT, base_url=settings.STATIC_URL)
        for app in all_apps:
            rel_path = System.bundle(app, force=True, sfx=options.get('sfx'))
            if not self.storage.exists(rel_path):
                self.stderr.write('Could not bundle {app}'.format(app=app))
            else:
                self.stdout.write('Bundled {app} into {out}'.format(app=app, out=rel_path))
            bundled_files[rel_path] = (storage, rel_path)

        if self.post_process and hasattr(self.storage, 'post_process'):
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
