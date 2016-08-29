from __future__ import unicode_literals

from copy import deepcopy

from django.conf import settings
from django.test import override_settings

import mock


def mock_Popen(mock_subproc_popen, return_value=None, side_effect=None):
    process_mock = mock.Mock()
    attrs = {}
    if side_effect is None:
        attrs['communicate.return_value'] = return_value or ('output', 'error')
    else:
        attrs['communicate.side_effect'] = side_effect
    process_mock.configure_mock(**attrs)
    mock_subproc_popen.return_value = process_mock
    return process_mock


def add_tpl_dir(path):
    """
    Adds a template dir to the settings.

    Decorator that wraps around `override_settings`.
    """
    templates = deepcopy(settings.TEMPLATES)
    templates[0]['DIRS'].append(path)
    return override_settings(TEMPLATES=templates)
