from __future__ import unicode_literals

import mock
import os
import io
import shutil
try:  # Py2
    from StringIO import StringIO
except ImportError:  # Py3
    from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


JINJA_TEMPLATES = [{
    'BACKEND': 'django.template.backends.jinja2.Jinja2',
    'DIRS': [
        os.path.join(settings.PROJECT_DIR, 'app', 'jinja2')
    ]
}]


def _bundle(app, **opts):
    path = os.path.join(settings.SYSTEMJS_OUTPUT_DIR, '{0}.js'.format(app))
    outfile = os.path.join(settings.STATIC_ROOT, path)
    if not os.path.isdir(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))
    with io.open(outfile, 'w') as f:
        f.write('alert(\'foo\')')
    return path


def _num_files(dir):
    return sum([len(files) for r, d, files in os.walk(dir)])


class ClearStaticMixin(object):

    def tearDown(self):
        self._clear_static()

    def _clear_static(self):
        try:
            shutil.rmtree(settings.STATIC_ROOT)
        except (OSError, IOError):
            pass


@mock.patch('systemjs.base.System.bundle')
class ManagementCommandTests(ClearStaticMixin, SimpleTestCase):

    def setUp(self):
        self.out = StringIO()
        self.err = StringIO()
        self._clear_static()

    def test_no_arguments(self, bundle_mock):
        """
        Test the correct functioning of calling 'systemjs_bundle' with
        no additional arguments.
        """
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # only one app should be found
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy', force=True, sfx=False))

    def test_sfx_option(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--sfx', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # only one app should be found
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy', force=True, sfx=True))

    @override_settings(TEMPLATES=JINJA_TEMPLATES)
    def test_different_backend(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # we only support vanilla templates
        # as opposed to app/dummy2
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy', force=True, sfx=False))

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.CachedStaticFilesStorage')
    def test_post_process(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        # created one file + the file with hashed filename
        self.assertEqual(_num_files(settings.STATIC_ROOT), 2)

        self.assertEqual(bundle_mock.call_count, 1)  # only one bundle call made

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.CachedStaticFilesStorage')
    def test_skip_post_process(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--no-post-process', stdout=self.out, stderr=self.err)
        # created one file + skipped post processing
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)
        self.assertEqual(bundle_mock.call_count, 1)  # only one bundle call made


class FailedBundleTests(SimpleTestCase):

    def setUp(self):
        self.out = StringIO()
        self.err = StringIO()

        try:
            shutil.rmtree(settings.STATIC_ROOT)
        except (OSError, IOError):
            pass

    @override_settings(SYSTEMJS_JSPM_EXECUTABLE='gibberish')
    @mock.patch('systemjs.base.System.get_jspm_version')
    def test_bundle_failed(self, mock):
        mock.return_value = (0, 15, 0)

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--sfx', stdout=self.out, stderr=self.err)

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)

        self.err.seek(0)
        self.assertEqual(self.err.read(), 'Could not bundle app/dummy\n')


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.CachedStaticFilesStorage')
@mock.patch('systemjs.base.System.bundle')
class PostProcessSystemJSTests(ClearStaticMixin, SimpleTestCase):

    """
    Test that `system.js` is post processed as well if it resides
    inside settings.STATIC_ROOT.
    """

    def setUp(self):
        self.out = StringIO()
        self.err = StringIO()
        self._clear_static()

        basedir = os.path.abspath(os.path.join(settings.STATIC_ROOT, 'jspm_packages'))
        self.systemjs_location = os.path.join(basedir, 'system.js')
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        # put a dummy system.js in place
        with open(self.systemjs_location, 'w') as of:
            of.write('alert("I am system.js");')

        self.patcher = mock.patch('systemjs.jspm.find_systemjs_location')
        self.mocked = self.patcher.start()
        self.mocked.return_value = self.systemjs_location

    def tearDown(self):
        super(PostProcessSystemJSTests, self).tearDown()
        self.patcher.stop()

    def test_systemjs_outside_of_static_root(self, bundle_mock):
        """
        If `system.js` is not inside of settings.STATIC_ROOT, it
        should not get post-processed explicitly as collectstatic does this.
        """
        bundle_mock.side_effect = _bundle
        # patch the location to outside of settings.STATIC_ROOT
        self.mocked.return_value = '/non/existant/path'

        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        # system.js exists + created one file + did post processing
        self.assertEqual(_num_files(settings.STATIC_ROOT), 3)
        self.assertEqual(bundle_mock.call_count, 1)  # only one bundle call made

    def test_systemjs_inside_static_root(self, bundle_mock):
        """
        See issue #5: if jspm installs directly into settings.STATIC_ROOT,
        with the CachedStaticFilesStorage, the `system.js` file is not post-processed.
        """
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        # system.js exists + created one file + did post processing for both
        self.assertEqual(_num_files(settings.STATIC_ROOT), 4)
        self.assertEqual(bundle_mock.call_count, 1)  # only one bundle call made
