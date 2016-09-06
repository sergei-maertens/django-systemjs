from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from systemjs.base import SystemTracer
from ._mixins import BundleOptionsMixin, TemplateDiscoveryMixin


class Command(BundleOptionsMixin, TemplateDiscoveryMixin, BaseCommand):
    help = "Writes the depcache for all discovered JS apps"
    requires_system_checks = False

    def handle(self, **options):
        super(Command, self).handle(**options)

        system_opts = self.get_system_opts(options)

        all_apps = self.find_apps(templates=options.get('templates'))
        all_apps = set(sum(all_apps.values(), []))

        tracer = SystemTracer(node_path=options.get('node_path'))

        all_deps = {
            app: tracer.trace(app) for app in all_apps
        }
        tracer.write_depcache(all_deps, system_opts)
