from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SystemJSConfig(AppConfig):
    name = 'systemjs'
    verbose_name = _('Django SystemJS')

    def ready(self):
        from . import conf  # noqa
