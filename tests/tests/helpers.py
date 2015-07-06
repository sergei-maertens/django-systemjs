from __future__ import unicode_literals

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
