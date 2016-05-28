from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.core.management.utils import handle_extensions

from ._package_discovery import TemplateDiscoveryMixin


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
        for tpl_name, apps in sorted(all_apps.items()):
            self.stdout.write(self.style.MIGRATE_LABEL(tpl_name))
            for app in apps:
                self.stdout.write('  {}'.format(app))
