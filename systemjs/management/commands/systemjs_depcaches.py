from __future__ import unicode_literals

import json
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.utils import handle_extensions

from ._package_discovery import TemplateDiscoveryMixin


CACHE_DIR = os.path.join(settings.ROOT_DIR, 'cache', 'systemjs')


class Command(TemplateDiscoveryMixin, BaseCommand):
    help = "Writes the depcache for all discovered modules"
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
        all_apps = set(sum(all_apps.values(), []))

        node_env = os.environ.copy()
        if 'NODE_PATH' not in node_env:
            node_env['NODE_PATH'] = './node_modules'  # FIXME: don't hardcode

        all_deps = {}
        for app in all_apps:
            process = subprocess.Popen(
                "trace-deps.js {}".format(app), shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=node_env
            )
            out, err = process.communicate()
            all_deps.update(json.loads(out))

        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        outfile = os.path.join(CACHE_DIR, 'deps.json')
        with open(outfile, 'w') as outfile:
            json.dump(all_deps, outfile)
