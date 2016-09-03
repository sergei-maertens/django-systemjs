from __future__ import unicode_literals

import json
import os
import shutil
import tempfile
import time

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from systemjs.base import SystemTracer
from .helpers import mock_Popen

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TracerTests(SimpleTestCase):

    def test_env_var(self):
        """
        Test that the NODE_PATH environment variable is handled properly
        """
        ENV_VAR = 'NODE_PATH'

        current_environ = os.environ.copy()
        self.assertNotIn(ENV_VAR, current_environ)

        # not in environ, not passed in explicitly -> tracer doesn't have it
        tracer = SystemTracer()
        self.assertNotIn(ENV_VAR, tracer.env)

        # in environ, not passed in -> tracer has it
        os.environ[ENV_VAR] = 'foo'
        tracer = SystemTracer()
        self.assertEqual(tracer.env[ENV_VAR], 'foo')

        # in environ, and passed it -> should take existing value
        tracer = SystemTracer(node_path='bar')
        self.assertEqual(tracer.env[ENV_VAR], 'foo')

        # not in environ, but passed in -> should take passed in value
        os.environ = current_environ
        tracer = SystemTracer(node_path='bar')
        self.assertEqual(tracer.env[ENV_VAR], 'bar')

    @patch('systemjs.base.subprocess.Popen')
    def test_trace_app(self, mock):
        """
        Test that tracing an app is delegated to the Node script.
        """
        trace_result = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': int(time.time()),
                'path': 'app/dummy.js',
                'skip': False,
            }
        }
        return_value = (json.dumps(trace_result), '')  # no stdout, no stderr
        process_mock = mock_Popen(mock, return_value=return_value)

        tracer = SystemTracer()
        tracer.trace('app/dummy')
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(mock.call_args[0], ('trace-deps.js app/dummy',))
        self.assertEqual(process_mock.communicate.call_count, 1)

        # check the cache functionality - once an app was traced, the result
        # should be stored on the tracer instance
        tracer.trace('app/dummy')
        self.assertEqual(mock.call_count, 1)  # should still be only one
        self.assertEqual(process_mock.communicate.call_count, 1)


@override_settings(SYSTEMJS_CACHE_DIR=tempfile.mkdtemp())
class TracerFileTests(SimpleTestCase):
    """
    Tracer tests that write/read files/directories
    """

    def setUp(self):
        super(TracerFileTests, self).setUp()
        call_command('collectstatic', interactive=False)

        self.now = int(time.time())
        self._depcache = {
            'version': 1,
            'packages': {
                'app/dummy': {
                    'app/dummy.js': {
                        'name': 'app/dummy.js',
                        'timestamp': self.now,
                        'path': 'app/dummy.js',
                        'skip': False,
                    },
                    'app/dependency.js': {
                        'name': 'app/dependency.js',
                        'timestamp': self.now,
                        'path': 'app/dependency.js',
                        'skip': False,
                    }
                }
            },
            'hashes': {
                'app/dummy.js': '65d75b61cae058018d3de1fa433a43da',
                'app/dependency.js': 'd41d8cd98f00b204e9800998ecf8427e'
            },
            'options': {
                'option1': True,
                'option2': False,
            }
        }

        def empty_cache_dir():
            for root, dirs, files in os.walk(settings.SYSTEMJS_CACHE_DIR):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

        self.addCleanup(empty_cache_dir)

    @patch('systemjs.base.os.makedirs', return_value=None)
    def test_create_cache_dir(self, mock_makedirs):
        tracer = SystemTracer()
        with self.settings(SYSTEMJS_CACHE_DIR='non-existent'):
            self.assertEqual(tracer.cache_file_path, os.path.join('non-existent', 'deps.json'))
        mock_makedirs.assert_called_once_with('non-existent')

    @patch('systemjs.base.subprocess.Popen')
    def test_write_deps(self, mock):
        """
        Trace an app and write the depcache for it.
        """
        now = int(time.time())
        trace_result = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': now,
                'path': 'app/dummy.js',
                'skip': False,
            },
            'app/dependency.js': {
                'name': 'app/dependency.js',
                'timestamp': now,
                'path': 'app/dependency.js',
                'skip': False,
            }
        }

        return_value = (json.dumps(trace_result), '')  # no stdout, no stderr
        mock_Popen(mock, return_value=return_value)

        tracer = SystemTracer()
        all_deps = {'app/dummy': tracer.trace('app/dummy')}

        path = os.path.join(settings.SYSTEMJS_CACHE_DIR, 'deps.json')
        self.assertFalse(os.path.exists(path))
        tracer.write_depcache(all_deps, {})
        self.assertTrue(os.path.exists(path))

    @patch('systemjs.base.subprocess.Popen')
    def test_write_deps_external_resource(self, mock):
        """
        Issue #13: google maps is scriptLoaded and has no physical file on disk.
        As such, there is no `info['path']` to read.
        """
        now = int(time.time())
        trace_result = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': now,
                'path': 'app/dummy.js',
                'skip': False,
            },
            'google-maps': {
                'name': 'google-maps',
                'path': None,
                'timestamp': None,
                'skip': True,
            },
        }

        return_value = (json.dumps(trace_result), '')  # no stdout, no stderr
        mock_Popen(mock, return_value=return_value)

        tracer = SystemTracer()
        all_deps = {'app/dummy': tracer.trace('app/dummy')}

        path = os.path.join(settings.SYSTEMJS_CACHE_DIR, 'deps.json')
        self.assertFalse(os.path.exists(path))
        tracer.write_depcache(all_deps, {})
        self.assertTrue(os.path.exists(path))
        with open(path) as infile:
            depcache = json.load(infile)
        # google maps may not be included
        self.assertEqual(list(depcache['packages'].keys()), ['app/dummy'])

    @patch('systemjs.base.json.load')
    def test_read_deps(self, mock_json_load):
        _file = open(os.path.join(settings.SYSTEMJS_CACHE_DIR, 'deps.json'), 'w')
        _file.write(json.dumps(self._depcache))
        self.addCleanup(_file.close)
        self.addCleanup(lambda: os.remove(_file.name))

        mock_json_load.return_value = self._depcache
        tracer = SystemTracer()

        # checking reading the hashes
        hashes = tracer.get_hashes()
        self.assertEqual(hashes, {
            'app/dummy.js': '65d75b61cae058018d3de1fa433a43da',
            'app/dependency.js': 'd41d8cd98f00b204e9800998ecf8427e'
        })

        # check reading the depcache for an app
        depcache = tracer.get_depcache('app/dummy')
        self.assertEqual(depcache, {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': self.now,
                'path': 'app/dummy.js',
                'skip': False,
            },
            'app/dependency.js': {
                'name': 'app/dependency.js',
                'timestamp': self.now,
                'path': 'app/dependency.js',
                'skip': False,
            }
        })

        # check retrieving bundle options
        bundle_options = tracer.get_bundle_options()
        self.assertEqual(bundle_options, {
            'option1': True,
            'option2': False,
        })

        self.assertEqual(mock_json_load.call_count, 1)

    @patch('systemjs.base.json.load')
    def test_hashes_match(self, mock_json_load):
        _file = open(os.path.join(settings.SYSTEMJS_CACHE_DIR, 'deps.json'), 'w')
        self.addCleanup(_file.close)
        self.addCleanup(lambda: os.remove(_file.name))

        mock_json_load.return_value = self._depcache
        tracer = SystemTracer()

        dep_tree = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': self.now,
                'path': 'app/dummy.js',
            },
            'app/dependency.js': {
                'name': 'app/dependency.js',
                'timestamp': self.now,
                'path': 'app/dependency.js',
            }
        }

        self.assertTrue(tracer.hashes_match(dep_tree))

        # mock the hashes to return different result
        with patch.object(tracer, 'get_hashes') as mocked_hashes:
            mocked_hashes.return_value = {
                'app/dummy.js': 'hash.app.dummy.js',
                'app/dependency.js': 'hash.app.dependency.js',
            }
            self.assertFalse(tracer.hashes_match(dep_tree))

    @patch('systemjs.base.json.load')
    def test_needs_update(self, mock_json_load):
        """
        Assert that the check correctly reports if a module needs re-bundling or not
        """
        tracer = SystemTracer()

        _file = open(os.path.join(settings.SYSTEMJS_CACHE_DIR, 'deps.json'), 'w')
        self.addCleanup(_file.close)
        self.addCleanup(lambda: os.remove(_file.name))

        _depcache = self._depcache.copy()
        del _depcache['packages']['app/dummy']['app/dependency.js']
        mock_json_load.return_value = _depcache

        # matching depcaches and hashes
        trace_result1 = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': self.now,
                'path': 'app/dummy.js',
                'skip': False,
            }
        }
        with patch.object(tracer, 'trace', return_value=trace_result1):
            self.assertFalse(tracer.check_needs_update('app/dummy'))

        # now try a different trace result, which should trigger the need for an update
        trace_result2 = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': self.now,
                'path': 'app/dummy.js',
                'skip': False,
            },
            'app/another_module.js': {
                'name': 'app/another_module.js',
                'timestamp': self.now,
                'path': 'app/another_module.js',
                'skip': False,
            }
        }
        with patch.object(tracer, 'trace', return_value=trace_result2):
            self.assertTrue(tracer.check_needs_update('app/dummy'))
