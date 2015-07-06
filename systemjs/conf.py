from __future__ import unicode_literals

from django.conf import settings

from appconf import AppConf


class SystemJSConf(AppConf):
    # Main switch
    ENABLED = not settings.DEBUG

    # Path to JSPM executable. Must be on the path, or a full path
    JSPM_EXECUTABLE = 'jspm'

    OUTPUT_DIR = 'SYSTEMJS'

    class Meta:
        prefix = 'systemjs'
