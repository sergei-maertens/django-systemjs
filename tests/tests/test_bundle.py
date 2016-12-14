from __future__ import unicode_literals

import mock
import os
import shutil
import subprocess
import tempfile

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from semantic_version import Version

from systemjs.base import System, BundleError
from .helpers import mock_Popen
from .test_management import _bundle


@override_settings(STATIC_ROOT=tempfile.mkdtemp())
class BundleTests(SimpleTestCase):

    def setUp(self):
        super(BundleTests, self).setUp()
        self.patcher = mock.patch.object(System, 'get_jspm_version')
        mocked = self.patcher.start()
        mocked.return_value = Version('0.15.0')

    def tearDown(self):
        super(BundleTests, self).tearDown()
        self.patcher.stop()

        try:
            shutil.rmtree(settings.STATIC_ROOT)
        except (OSError, IOError):
            pass

    @override_settings(SYSTEMJS_OUTPUT_DIR='SYSJS')
    @mock.patch('subprocess.Popen')
    def test_bundle_result(self, mock_subproc_popen):
        """
        Test that bundling an app returns the correct relative path.
        """
        system = System()

        def side_effect(*args, **kwargs):
            _bundle('app/dummy')
            return ('output', 'error')

        # mock Popen/communicate
        mock_Popen(mock_subproc_popen, side_effect=side_effect)

        path = system.bundle('app/dummy')
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
        system = System()
        system.bundle(app_name)
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
        system = System(sfx=True)
        system.bundle('app/dummy')
        self.assertEqual(mock_subproc_popen.call_count, 1)
        command = mock_subproc_popen.call_args[0][0]
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/app/dummy.js')
        self.assertEqual(command, 'jspm bundle-sfx app/dummy {0}'.format(outfile))

        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_bundle_minify_suprocess(self, mock_subproc_popen):
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
        system = System(minify=True)
        system.bundle('app/dummy')
        self.assertEqual(mock_subproc_popen.call_count, 1)
        command = mock_subproc_popen.call_args[0][0]
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/app/dummy.js')
        self.assertEqual(command, 'jspm bundle app/dummy {0} --minify'.format(outfile))

        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_bundle_skip_source_maps_suprocess(self, mock_subproc_popen):
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
        system = System(skip_source_maps=True)
        system.bundle('app/dummy')
        self.assertEqual(mock_subproc_popen.call_count, 1)
        command = mock_subproc_popen.call_args[0][0]
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/app/dummy.js')
        self.assertEqual(command,
                         'jspm bundle app/dummy {0} --skip-source-maps'.format(outfile))

        outfile = os.path.join(settings.STATIC_ROOT,
                               'SYSTEMJS/{0}.js'.format(app_name))
        with open(outfile, 'r') as of:
            js = of.read()
        self.assertEqual(js, "alert('foo')\nSystem.import('app/dummy.js');\n")

        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_oserror_caught(self, mock):
        def oserror():
            raise OSError('Error')

        mock_Popen(mock, side_effect=oserror)
        with self.assertRaises(BundleError):
            system = System()
            system.bundle('app/dummy')

    @mock.patch('subprocess.Popen')
    def test_ioerror_caught(self, mock):

        def ioerror():
            raise IOError('Error')

        mock_Popen(mock, side_effect=ioerror)
        with self.assertRaises(BundleError):
            system = System()
            system.bundle('app/dummy')


class JSPMIntegrationTests(SimpleTestCase):

    @mock.patch('subprocess.Popen')
    def test_jspm_version_suprocess(self, mock_subproc_popen):
        """
        Test that JSPM version discovery works.
        """
        # mock Popen/communicate
        return_value = (b'0.15.7\nRunning against global jspm install.\n', '')
        process_mock = mock_Popen(mock_subproc_popen, return_value=return_value)

        system = System()

        # Call version
        version = system.get_jspm_version({'jspm': 'jspm'})
        self.assertEqual(mock_subproc_popen.call_count, 1)
        self.assertEqual(version, Version('0.15.7'))

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

        system = System()

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
        mock_version.return_value = Version('0.16.3')

        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            _bundle(app_name)
            return ('', '')  # no stdout, no stderr -> success

        # mock Popen/communicate
        process_mock = mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        system = System()
        system.bundle(app_name)
        self.assertEqual(mock_subproc_popen.call_count, 1)

        command = mock_subproc_popen.call_args
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/{0}.js'.format(app_name))

        self.assertEqual(
            command,
            mock.call(
                'jspm bundle {0} {1} --log err'.format(app_name, outfile),
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
        mock_version.return_value = Version('0.16.3')

        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            _bundle(app_name)
            return ('', 'Something went wrong')  # no stdout, no stderr -> success

        # mock Popen/communicate
        process_mock = mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        with self.assertRaises(BundleError) as ctx:
            system = System()
            system.bundle(app_name)

        self.assertEqual(ctx.exception.args[0], "Could not bundle \'app/dummy\': \nSomething went wrong")

        self.assertEqual(mock_subproc_popen.call_count, 1)
        self.assertEqual(process_mock.communicate.call_count, 1)

    @mock.patch('subprocess.Popen')
    @mock.patch.object(System, 'get_jspm_version')
    def test_sourcemap_comment(self, mock_version, mock_subproc_popen):
        """
        Asserts that the sourcemap comment is still at the end.
        """
        mock_version.return_value = Version('0.15.7')
        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            content = 'alert(\'foo\')\n//# sourceMappingURL=dummy.js.map'
            _bundle(app_name, content=content)
            return ('output', 'error')

        # mock Popen/communicate
        mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        system = System()
        system.bundle(app_name)
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/{0}.js'.format(app_name))
        with open(outfile, 'r') as of:
            js = of.read()
        self.assertEqual(js, "alert('foo')\nSystem.import('app/dummy.js');\n"
                             "//# sourceMappingURL=dummy.js.map")

    @mock.patch('subprocess.Popen')
    @mock.patch.object(System, 'get_jspm_version')
    def test_sourcemap_comment_end_newline(self, mock_version, mock_subproc_popen):
        """
        Asserts that the sourcemap comment is still at the end - with ending newline
        """
        mock_version.return_value = Version('0.15.7')
        app_name = 'app/dummy'

        def side_effect(*args, **kwargs):
            content = 'alert(\'foo\')\n//# sourceMappingURL=dummy.js.map\n'
            _bundle(app_name, content=content)
            return ('output', 'error')

        # mock Popen/communicate
        mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        system = System()
        system.bundle(app_name)
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/{0}.js'.format(app_name))
        with open(outfile, 'r') as of:
            js = of.read()
        self.assertEqual(js, "alert('foo')\nSystem.import('app/dummy.js');\n"
                             "//# sourceMappingURL=dummy.js.map")

    @mock.patch('subprocess.Popen')
    @mock.patch.object(System, 'get_jspm_version')
    def test_sourcemap_comment_large_file(self, mock_version, mock_subproc_popen):
        """
        Same test as test_sourcemap_comment, except with a 'file' that's more
        than 100 bytes (to read multiple blocks).
        """
        mock_version.return_value = Version('0.15.7')
        app_name = 'app/dummy'

        lorem = '''
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
'''

        def side_effect(*args, **kwargs):
            content = 'alert(\'{}\')\n//# sourceMappingURL=dummy.js.map'.format(lorem)
            _bundle(app_name, content=content)
            return ('output', 'error')

        # mock Popen/communicate
        mock_Popen(mock_subproc_popen, side_effect=side_effect)

        # Bundle app/dummy
        system = System()
        system.bundle(app_name)
        outfile = os.path.join(settings.STATIC_ROOT, 'SYSTEMJS/{0}.js'.format(app_name))
        with open(outfile, 'r') as of:
            js = of.read()
        self.assertEqual(js, "alert('{}')\nSystem.import('app/dummy.js');\n"
                             "//# sourceMappingURL=dummy.js.map".format(lorem))
