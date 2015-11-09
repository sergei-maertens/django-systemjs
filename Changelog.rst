Changelog
=========

0.3.4
-----
Fixes some mistakes from 0.3.3. Mondays...

0.3.3
-----
Added post-processing of `jspm_packages/system.js` if it is within
`settings.STATIC_ROOT`.

This introduces a new setting: `SYSTEMJS_PACKAGE_JSON_DIR`. Set this to the path
of the folder containing `package.json`. `package.json` will be inspected to
figure out the install path of jspm - and only post-process if the latter path
is within `settings.STATIC_ROOT`. By default, `settings.BASE_DIR` (provided by
the default `django-admin.py startproject` template) will be chosen for this
directory.

0.3.2
-----
Fixed incorrect passing of the --log option.

0.3.1
-----

No API changes where made - this release is preparation for Django 1.9 and
improves robustness of bundling.

In version 0.16.3 `--log` was added to JSPM. This allows us to properly check
for build errors, where before you would find out the hard way. Build errors
will now show as output from the management command.

An check has been added to figure out the JSPM version. If you get a
`BundleError` saying that the JSPM version could not be determined, check that
`jspm` is available in your path or modify the `SYSTEMJS_JSPM_EXECUTABLE`
setting accordingly.


0.3.0
-----

Changed the templatetag to add the .js extension. Existing code should still
work, possibly you need to set System.defaultJSExtensions to `true`.


.. note::

    Possibly breaking change! This release is required if you use SystemJS >=
    0.17. The default.js extension is no longer added by SystemJS.

