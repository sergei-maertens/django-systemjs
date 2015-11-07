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


def find_systemjs_location():
    """
    Figure out where `jspm_packages/system.js` will be put by JSPM.
    """
    location = os.path.abspath(os.path.dirname(locate_package_json()))
    conf = parse_package_json()
    if 'jspm' in conf:
        conf = conf['jspm']

    try:
        conf = conf['directories']
    except KeyError:
        raise KeyError("The `directories` configuarion was not found in package.json. "
                       "Please check your jspm install and/or configuarion.")

    # check for explicit location, else fall back to the default as jspm does
    jspm_packages = conf['packages'] if 'packages' in conf else 'jspm_packages'
    return os.path.join(location, jspm_packages, 'system.js')
