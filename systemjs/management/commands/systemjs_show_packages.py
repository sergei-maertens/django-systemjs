from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ._mixins import TemplateDiscoveryMixin


class Command(TemplateDiscoveryMixin, BaseCommand):
    help = "Find packages imported in the templates and list them"
    requires_system_checks = False

    def handle(self, **options):
        super(Command, self).handle(**options)

        all_apps = self.find_apps(templates=options.get('templates'))
        for tpl_name, apps in sorted(all_apps.items()):
            self.stdout.write(self.style.MIGRATE_LABEL(tpl_name))
            for app in apps:
                self.stdout.write('  {}'.format(app))
