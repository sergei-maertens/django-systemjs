import os
import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def locate_package_json():
    """
    Find and return the location of package.json.
    """
    directory = settings.SYSTEMJS_PACKAGE_JSON_DIR
    if not directory:
        raise ImproperlyConfigured(
            "Could not locate 'package.json'. Set SYSTEMJS_PACKAGE_JSON_DIR "
            "to the directory that holds 'package.json'."
        )
    path = os.path.join(directory, 'package.json')
    if not os.path.isfile(path):
        raise ImproperlyConfigured("'package.json' does not exist, tried looking in %s" % path)
    return path


def parse_package_json():
    """
    Extract the JSPM configuration from package.json.
    """
    with open(locate_package_json()) as pjson:
        data = json.loads(pjson.read())
    return data
