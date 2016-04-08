"""
Tests related to staticfiles finders.
"""
import os

from django.conf import settings
from django.test import override_settings, SimpleTestCase
from django.contrib.staticfiles import finders


class FinderTests(SimpleTestCase):

    def test_jspm_packages_in_static_root(self):
        """
        Test that the files in jspm_packages are found when jspm
        installs directly in settings.STATIC_ROOT.

        Regression test for #9 where django-compressor turns out to
        be a hidden dependency.
        """
        # assert that it's not found with the standard finders
        location = finders.find('jspm_packages/system.js', all=False)
        self.assertIsNone(location)

        # but it is found with the custom finder...
        with override_settings(STATICFILES_FINDERS=('systemjs.finders.SystemFinder',)):
            location = finders.find('jspm_packages/system.js', all=False)
        self.assertEqual(
            location,
            os.path.abspath(os.path.join(settings.STATIC_ROOT, 'jspm_packages', 'system.js'))
        )

    def test_finder_non_jspm_package_file(self):
        # assert that it's not found with the standard finders
        location = finders.find('node_modules/system.js', all=False)
        self.assertIsNone(location)

        # but it is found with the custom finder...
        with override_settings(STATICFILES_FINDERS=('systemjs.finders.SystemFinder',)):
            location = finders.find('node_modules/system.js', all=False)
        self.assertIsNone(location)
