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
    except TypeError:
        raise ImproperlyConfigured("`package.json` doesn't appear to be a valid json object. "
                                   "Location: %s" % location)
    except KeyError:
        raise ImproperlyConfigured("The `directories` configuarion was not found in package.json. "
                                   "Please check your jspm install and/or configuarion. `package.json` "
                                   "location: %s" % location)

    # check for explicit location, else fall back to the default as jspm does
    jspm_packages = conf['packages'] if 'packages' in conf else 'jspm_packages'
    base = conf['baseURL'] if 'baseURL' in conf else '.'
    return os.path.join(location, base, jspm_packages, 'system.js')
