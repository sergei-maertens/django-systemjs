"""
Tests that deal with locating package.json, parsing it and extracting
relevant information.
"""
from __future__ import unicode_literals

import mock
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from systemjs.jspm import find_systemjs_location, locate_package_json, parse_package_json


overridden_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))

simple = os.path.join(overridden_path, 'simple_package.json')
nested = os.path.join(overridden_path, 'jspm_nested_package.json')


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

    @mock.patch('systemjs.jspm.locate_package_json')
    def test_read_package_json(self, mock):
        """
        Test that package.json correctly gets loaded as JSON into a dict.
        """
        # return a simple json blob path
        mock.return_value = simple

        data = parse_package_json()
        self.assertEqual(data, {
            "name": "dummy",
            "directories": {
                "baseURL": "static",
            }
        })

    @override_settings(STATIC_ROOT=overridden_path)
    @mock.patch('systemjs.jspm.locate_package_json')
    def test_nested_jspm_extract(self, mock):
        """
        JSPM has an option to nest all configuration in package.json in some
        sort of 'jspm' namespace. Test that is dealt with accordingly.
        """
        mock.return_value = nested

        location = find_systemjs_location()
        expected_location = os.path.join(settings.STATIC_ROOT, 'jspm', 'system.js')
        self.assertEqual(location, expected_location)

    @override_settings(STATIC_ROOT=overridden_path)
    @mock.patch('systemjs.jspm.locate_package_json')
    def test_non_nested_jspm_extract(self, mock):
        """
        JSPM has an option to nest all configuration in package.json in some
        sort of 'jspm' namespace. Test that is dealt with accordingly if the
        config is not namespaced.
        """
        mock.return_value = simple

        location = find_systemjs_location()
        expected_location = os.path.join(settings.STATIC_ROOT, 'jspm_packages', 'system.js')
        self.assertEqual(location, expected_location)

    @mock.patch('systemjs.jspm.parse_package_json')
    def test_invalid_package_json(self, mock):
        mock.return_value = 'I am invalid'

        with self.assertRaises(ImproperlyConfigured):
            find_systemjs_location()

    @mock.patch('systemjs.jspm.parse_package_json')
    def test_invalid_package_json2(self, mock):
        mock.return_value = {
            "name": "I am invalid"
        }

        with self.assertRaises(ImproperlyConfigured):
            find_systemjs_location()

    @override_settings(BASE_DIR=None)
    def test_missing_package_json_dir_setting(self):
        from systemjs.conf import SystemJSConf

        with self.assertRaises(ImproperlyConfigured):
            SystemJSConf().configure_package_json_dir(None)
