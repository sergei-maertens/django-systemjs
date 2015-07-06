import mock

from django.test import SimpleTestCase


class BundleTests(SimpleTestCase):

    def test_bundle(self):
        """
        Test that bundling and app makes the correct system calls.
        """

