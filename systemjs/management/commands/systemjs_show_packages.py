from __future__ import unicode_literals

import io
import os
import re
from collections import OrderedDict

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import SuspiciousFileOperation
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import handle_extensions
from django.core.files.storage import FileSystemStorage
from django.template.base import TOKEN_BLOCK
from django.template import loader, TemplateDoesNotExist
from django.template.loaders.app_directories import get_app_template_dirs

from systemjs.base import System
from systemjs.compat import Lexer
from systemjs.jspm import find_systemjs_location
from systemjs.templatetags.system_tags import SystemImportNode
from ._package_discovery import TemplateDiscoveryMixin


SYSTEMJS_TAG_RE = re.compile(r"""systemjs_import\s+(['\"])(?P<app>.*)\1""")

RESOLVE_CONTEXT = {}


class Command(TemplateDiscoveryMixin, BaseCommand):
    help = "Find packages imported in the templates and list them"
    requires_system_checks = False

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

    def handle(self, **options):
        self.symlinks = options.get('symlinks')
        extensions = options.get('extensions') or ['html']
        self.extensions = handle_extensions(extensions)

        all_apps = self.find_apps(templates=options.get('templates'))
