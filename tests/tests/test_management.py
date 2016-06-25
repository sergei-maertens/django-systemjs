from __future__ import unicode_literals

import io
import json
import mock
import os
import shutil
import tempfile
import time
try:  # Py2
    from StringIO import StringIO
except ImportError:  # Py3
    from io import StringIO

from django.conf import settings
from django.core.management import call_command, CommandError
from django.test import SimpleTestCase, override_settings

from semantic_version import Version


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
        content = opts.get('content', 'alert(\'foo\')')
        f.write(content)
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


class MockFindSystemJSLocation(object):

    def setUp(self):
        super(MockFindSystemJSLocation, self).setUp()
        self.patcher = mock.patch('systemjs.management.commands.systemjs_bundle.find_systemjs_location')
        self.mock = self.patcher.start()
        self.mock.return_value = '/dummy/path/system.js'

    def tearDown(self):
        super(MockFindSystemJSLocation, self).tearDown()
        self.patcher.stop()


@override_settings(STATIC_ROOT=tempfile.mkdtemp())
@mock.patch('systemjs.base.System.bundle')
class ManagementCommandTests(MockFindSystemJSLocation, ClearStaticMixin, SimpleTestCase):

    def setUp(self):
        super(ManagementCommandTests, self).setUp()
        self.out = StringIO()
        self.err = StringIO()
        self._clear_static()

        self.now = int(time.time())

    def _create_deps_json(self, deps=None, **overrides):
        deps = deps or {
            'version': 1,
            'packages': {
                'app/dummy': {
                    'app/dummy.js': {
                        'name': 'app/dummy.js',
                        'timestamp': self.now,
                        'path': 'app/dummy.js',
                    }
                }
            },
            'hashes': {
                'app/dummy.js': '65d75b61cae058018d3de1fa433a43da',
            },
            'options': {
                'minimal': True,
                'sfx': False,
                'minify': False,
            }
        }
        deps.update(**overrides)
        with open(os.path.join(settings.SYSTEMJS_CACHE_DIR, 'deps.json'), 'w') as _file:
            json.dump(deps, _file)

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
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy',))

    def test_sfx_option(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--sfx', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # only one app should be found
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy',))

    def test_minify_option(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--minify', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # only one app should be found
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy',))

    @override_settings(TEMPLATES=JINJA_TEMPLATES)
    def test_different_backend(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # we only support vanilla templates
        # as opposed to app/dummy2
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy',))

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

    def test_templates_option(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--template', 'base.html', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)

        self.assertEqual(bundle_mock.call_count, 1)  # only one app should be found
        self.assertEqual(bundle_mock.call_args, mock.call('app/dummy',))

    def test_templates_option_wrong_tpl(self, bundle_mock):
        bundle_mock.side_effect = _bundle

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        with self.assertRaises(CommandError):
            call_command('systemjs_bundle', '--template', 'nothere.html', stdout=self.out, stderr=self.err)
        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        self.assertEqual(bundle_mock.call_count, 0)

    @override_settings(SYSTEMJS_CACHE_DIR=tempfile.mkdtemp())
    @mock.patch('systemjs.base.SystemTracer.trace')
    def test_minimal_bundle(self, trace_mock, bundle_mock):
        """
        Assert that minimal bundles are generated only if needed
        """
        trace_mock.return_value = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': self.now,
                'path': 'app/dummy.js',
            }
        }
        self._create_deps_json()

        call_command('collectstatic', link=True, interactive=False, stdout=self.out, sterr=self.err)
        call_command('systemjs_bundle', '--minimal', stdout=self.out, stderr=self.err)
        # no new bundles should have been created
        self.assertEqual(bundle_mock.call_count, 0)

    @override_settings(SYSTEMJS_CACHE_DIR=tempfile.mkdtemp())
    @mock.patch('systemjs.base.SystemTracer.trace')
    def test_minimal_bundle_different_options(self, trace_mock, bundle_mock):
        """
        Assert that minimal bundles are generated only if needed
        """
        trace_mock.return_value = {
            'app/dummy.js': {
                'name': 'app/dummy.js',
                'timestamp': self.now,
                'path': 'app/dummy.js',
            }
        }
        self._create_deps_json()

        call_command('collectstatic', link=True, interactive=False, stdout=self.out, sterr=self.err)
        call_command('systemjs_bundle', '--minimal', '--sfx', stdout=self.out, stderr=self.err)
        # no new bundles should have been created
        self.assertEqual(bundle_mock.call_count, 1)


@override_settings(STATIC_ROOT=tempfile.mkdtemp())
class FailedBundleTests(MockFindSystemJSLocation, ClearStaticMixin, SimpleTestCase):

    def setUp(self):
        super(FailedBundleTests, self).setUp()
        self.out = StringIO()
        self.err = StringIO()

        self._clear_static()

    @override_settings(SYSTEMJS_JSPM_EXECUTABLE='gibberish')
    @mock.patch('systemjs.base.System.get_jspm_version')
    def test_bundle_failed(self, mock):
        mock.return_value = Version('0.15.0')

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', '--sfx', stdout=self.out, stderr=self.err)

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)

        self.err.seek(0)
        self.assertEqual(self.err.read(), 'Could not bundle app/dummy\n')


@override_settings(
    STATIC_ROOT=tempfile.mkdtemp(),
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.CachedStaticFilesStorage')
@mock.patch('systemjs.base.System.bundle')
class PostProcessSystemJSTests(ClearStaticMixin, SimpleTestCase):

    """
    Test that `system.js` is post processed as well if it resides
    inside settings.STATIC_ROOT.
    """

    def setUp(self):
        super(PostProcessSystemJSTests, self).setUp()

        self.out = StringIO()
        self.err = StringIO()
        self._clear_static()

    def write_systemjs(self):
        basedir = os.path.abspath(os.path.join(settings.STATIC_ROOT, 'jspm_packages'))
        self.systemjs_location = os.path.join(basedir, 'system.js')
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        # put a dummy system.js in place
        with open(self.systemjs_location, 'w') as of:
            of.write('alert("I am system.js");')

    @mock.patch('systemjs.management.commands.systemjs_bundle.find_systemjs_location')
    def test_systemjs_outside_of_static_root(self, systemjs_mock, bundle_mock):
        """
        If `system.js` is not inside of settings.STATIC_ROOT, it
        should not get post-processed explicitly as collectstatic does this.
        """
        bundle_mock.side_effect = _bundle
        # patch the location to outside of settings.STATIC_ROOT
        systemjs_mock.return_value = '/non/existant/path'

        self.assertEqual(_num_files(settings.STATIC_ROOT), 0)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        # created one file + did post processing
        self.assertEqual(_num_files(settings.STATIC_ROOT), 2)
        self.assertEqual(bundle_mock.call_count, 1)  # only one bundle call made

    @mock.patch('systemjs.management.commands.systemjs_bundle.find_systemjs_location')
    def test_systemjs_inside_static_root(self, systemjs_mock, bundle_mock):
        """
        See issue #5: if jspm installs directly into settings.STATIC_ROOT,
        with the CachedStaticFilesStorage, the `system.js` file is not post-processed.
        """
        bundle_mock.side_effect = _bundle
        self.write_systemjs()
        systemjs_mock.return_value = self.systemjs_location

        self.assertEqual(_num_files(settings.STATIC_ROOT), 1)
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)
        # system.js exists + created one file + did post processing for both
        self.assertEqual(_num_files(settings.STATIC_ROOT), 4)
        self.assertEqual(bundle_mock.call_count, 1)  # only one bundle call made


@override_settings(
    STATIC_ROOT=tempfile.mkdtemp(),
    STATICFILES_STORAGE='systemjs.storage.SystemJSManifestStaticFilesStorage')
@mock.patch('systemjs.base.System.bundle')
class ManifestStorageTests(ClearStaticMixin, SimpleTestCase):

    """
    Test that the storage works as expected - do not wipe collectstatic results
    """

    def setUp(self):
        super(ManifestStorageTests, self).setUp()

        self.out = StringIO()
        self.err = StringIO()
        self._clear_static()

    @mock.patch('systemjs.management.commands.systemjs_bundle.find_systemjs_location')
    def test_collectstatic_not_broken(self, systemjs_mock, bundle_mock):
        bundle_mock.side_effect = _bundle
        systemjs_mock.return_value = '/non/existant/path/'

        base = os.path.abspath(settings.STATIC_ROOT)
        self.assertEqual(_num_files(base), 0)

        call_command('collectstatic', link=True, interactive=False, stdout=self.out, sterr=self.err)
        # dummy.js + dummy.hash.js + staticfiles.json + dependency.js + dependency.hash.js
        self.assertEqual(_num_files(base), 5)
        with open(os.path.join(base, 'staticfiles.json')) as infile:
            manifest = json.loads(infile.read())
        self.assertEqual(manifest['paths'], {
            'app/dummy.js': 'app/dummy.65d75b61cae0.js',
            'app/dependency.js': 'app/dependency.d41d8cd98f00.js'
        })

        # bundle the files and check that the bundled file is post-processed
        call_command('systemjs_bundle', stdout=self.out, stderr=self.err)

        # + bundled file + post-processed file (not staticfiles.json!)
        self.assertEqual(_num_files(base), 7)
        with open(os.path.join(base, 'staticfiles.json')) as infile:
            manifest = json.loads(infile.read())
        self.assertEqual(manifest['paths'], {
            'app/dummy.js': 'app/dummy.65d75b61cae0.js',
            'app/dependency.js': 'app/dependency.d41d8cd98f00.js',
            'SYSTEMJS/app/dummy.js': 'SYSTEMJS/app/dummy.5d1dad25dae3.js'
        })

    @mock.patch('systemjs.management.commands.systemjs_bundle.find_systemjs_location')
    def test_no_collectstatic(self, m1, m2):
        m1.return_value = '/fake/path/'
        m2.side_effect = _bundle

        with self.assertRaises(CommandError):
            call_command('systemjs_bundle')


class ShowPackagesTests(SimpleTestCase):

    def test_command(self):
        """
        Check that listing the packages works as expected.
        """
        stdout = StringIO()
        stderr = StringIO()
        call_command('systemjs_show_packages', stdout=stdout, sterr=stderr)
        stderr.seek(0)
        stdout.seek(0)
        self.assertEqual(stderr.read(), '')  # no errors
        output = stdout.read()
        self.assertIn('base.html', output)
        self.assertIn('app/dummy', output)


class WriteDepCachesTests(SimpleTestCase):

    @mock.patch('systemjs.base.SystemTracer.write_depcache')
    @mock.patch('systemjs.base.SystemTracer.trace')
    def test_command(self, mock_trace, mock_write_depcache):
        """
        Check that writing the depcaches works as expected.
        """
        mock_trace.return_value = {}
        stdout = StringIO()
        stderr = StringIO()
        call_command('systemjs_write_depcaches', stdout=stdout, sterr=stderr)
        stderr.seek(0)
        stdout.seek(0)
        self.assertEqual(stderr.read(), '')  # no errors
        self.assertEqual(stdout.read(), '')  # no output either

        mock_trace.assert_called_once_with('app/dummy')
        mock_write_depcache.assert_called_once_with(
            {'app/dummy': {}},
            {'minimal': False, 'sfx': False, 'minify': False}
        )
