from __future__ import unicode_literals

import mock
import os
import shutil
import subprocess

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from systemjs.base import System, BundleError
from .helpers import mock_Popen
from .test_management import _bundle


class BundleTests(SimpleTestCase):

    def setUp(self):
        super(BundleTests, self).setUp()
        self.patcher = mock.patch.object(System, 'get_jspm_version')
        mocked = self.patcher.start()
        mocked.return_value = (0, 15, 0)

    def tearDown(self):
        super(BundleTests, self).tearDown()
        self.patcher.stop()

        try:
            shutil.rmtree(settings.STATIC_ROOT)
        except (OSError, IOError):
            pass

    @override_settings(SYSTEMJS_OUTPUT_DIR='SYSJS')
    def test_bundle_result(self):
        """
        Test that bundling an app returns the correct relative path.
        """
        path = System.bundle('app/dummy')
        expected_path = os.path.join(settings.SYSTEMJS_OUTPUT_DIR, 'app/dummy.js')
        self.assertEqual(path, expected_path)

    @mock.patch('subprocess.Popen')
    def test_bundle_suprocess(self, mock_subproc_popen):
        """
        Test that bundling calls the correct subprocess command
        """
        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            _bundle(app_name)
            return ('output', 'error')

        # mock Popen/communicate
        process_mock = mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        System.bundle(app_name, force=True)
        self.assertEqual(mock_subproc_popen.call_count, 1)
        command = mock_subproc_popen.call_args[0][0]
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/{0}.js'.format(app_name))
        self.assertEqual(command, 'jspm bundle {0} {1}'.format(app_name, outfile))

        with open(outfile, 'r') as of:
            js = of.read()
        self.assertEqual(js, "alert('foo')\nSystem.import('app/dummy.js');\n")

        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_bundlesfx_suprocess(self, mock_subproc_popen):
        """
        Test that bundling calls the correct subprocess command
        """
        # mock Popen/communicate
        process_mock = mock_Popen(mock_subproc_popen)

        # Bundle app/dummy
        System.bundle('app/dummy', sfx=True, force=True)
        self.assertEqual(mock_subproc_popen.call_count, 1)
        command = mock_subproc_popen.call_args[0][0]
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/app/dummy.js')
        self.assertEqual(command, 'jspm bundle-sfx app/dummy {0}'.format(outfile))

        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_oserror_caught(self, mock):
        def oserror():
            raise OSError('Error')

        mock_Popen(mock, side_effect=oserror)
        with self.assertRaises(BundleError):
            System.bundle('app/dummy', force=True)

    @mock.patch('subprocess.Popen')
    def test_ioerror_caught(self, mock):

        def ioerror():
            raise IOError('Error')

        mock_Popen(mock, side_effect=ioerror)
        with self.assertRaises(BundleError):
            System.bundle('app/dummy', force=True)


class JSPMIntegrationTests(SimpleTestCase):

    @mock.patch('subprocess.Popen')
    def test_jspm_version_suprocess(self, mock_subproc_popen):
        """
        Test that JSPM version discovery works.
        """
        # mock Popen/communicate
        return_value = (b'0.15.7\nRunning against global jspm install.\n', '')
        process_mock = mock_Popen(mock_subproc_popen, return_value=return_value)

        system = System('app/dummy')

        # Call version
        version = system.get_jspm_version({'jspm': 'jspm'})
        self.assertEqual(mock_subproc_popen.call_count, 1)
        self.assertEqual(version, (0, 15, 7))

        command = mock_subproc_popen.call_args[0][0]
        self.assertEqual(command, 'jspm --version')
        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_jspm_version_suprocess_error(self, mock_subproc_popen):
        """
        Test that bundling calls the correct subprocess command
        """
        # mock Popen/communicate
        return_value = (b'gibberish', 'a jspm error')
        process_mock = mock_Popen(mock_subproc_popen, return_value=return_value)

        system = System('app/dummy')

        # Call version
        with self.assertRaises(BundleError):
            system.get_jspm_version({'jspm': 'jspm'})

        self.assertEqual(mock_subproc_popen.call_count, 1)

        command = mock_subproc_popen.call_args[0][0]
        self.assertEqual(command, 'jspm --version')
        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    @mock.patch.object(System, 'get_jspm_version')
    def test_jspm_016_log(self, mock_version, mock_subproc_popen):
        """
        Test that bundles are generated with --log=err.

        JSPM > 0.16.0 has the --log option that surpresses levels of
        output.
        """
        mock_version.return_value = (0, 16, 3)

        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            _bundle(app_name)
            return ('', '')  # no stdout, no stderr -> success

        # mock Popen/communicate
        process_mock = mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        System.bundle(app_name, force=True)
        self.assertEqual(mock_subproc_popen.call_count, 1)

        command = mock_subproc_popen.call_args
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/{0}.js'.format(app_name))

        self.assertEqual(
            command,
            mock.call(
                'jspm bundle {0} {1} --log=err'.format(app_name, outfile),
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                shell=True, cwd=None
            )
        )

        with open(outfile, 'r') as of:
            js = of.read()
        self.assertEqual(js, "alert('foo')\nSystem.import('app/dummy.js');\n")

        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    @mock.patch.object(System, 'get_jspm_version')
    def test_jspm_016_log_error(self, mock_version, mock_subproc_popen):
        """
        Test that bundles are generated with --log=err.

        JSPM > 0.16.0 has the --log option that surpresses levels of
        output.
        """
        mock_version.return_value = (0, 16, 3)

        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            _bundle(app_name)
            return ('', 'Something went wrong')  # no stdout, no stderr -> success

        # mock Popen/communicate
        process_mock = mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        with self.assertRaises(BundleError) as ctx:
            System.bundle(app_name, force=True)

        self.assertEqual(ctx.exception.args[0], "Could not bundle \'app/dummy\': \nSomething went wrong")

        self.assertEqual(mock_subproc_popen.call_count, 1)
        self.assertEqual(process_mock.communicate.call_count, 1)
