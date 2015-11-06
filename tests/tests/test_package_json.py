"""
Tests that deal with locating package.json, parsing it and extracting
relevant information.
"""
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from systemjs.jspm import locate_package_json, parse_jspm_from_package_json


overridden_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))


class PackageJsonTests(SimpleTestCase):

    def test_auto_locate(self):
        """
        Test that based on settings.BASE_DIR, the package.json folder
        can be found.
        """
        root = os.path.abspath(settings.PROJECT_DIR)
        path = settings.SYSTEMJS_PACKAGE_JSON_DIR
        self.assertEqual(path, root)
        package_json = locate_package_json()
        self.assertEqual(package_json, os.path.join(root, 'package.json'))

    @override_settings(SYSTEMJS_PACKAGE_JSON_DIR=overridden_path)
    def test_load_overridden_path(self):
        package_json = locate_package_json()
        self.assertEqual(package_json, os.path.join(overridden_path, 'package.json'))

    @override_settings(SYSTEMJS_PACKAGE_JSON_DIR='/false/path')
    def test_invalid_dir(self):
        with self.assertRaises(ImproperlyConfigured):
            locate_package_json()
