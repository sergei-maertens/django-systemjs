Changelog
=========
1.4.2
-----
* Added a fix for the ``--sfx`` option on jspm 0.17 (thanks @funn)

1.4
---

* ``--template``, ``-t`` option added to management commands. These limit the
  templates that are parsed for ``{% systemjs_import ... %}`` tags.

* Added ``--minimal`` option to ``systemjs_bundle`` management command. This will
  rebundle an app/package only when something has changed in the dependency tree.
  Usefull when you have many bundles and only a small number changed.

* Added two new management commands:

  - ``systemjs_show_packages``: lists all the packages imported in templates
  - ``systemjs_write_depcaches``: writes out the dependency tree for each package

1.3.3
-----

* Optimization: build a bundle only once. Before, if a bundle was used in
  multiple templates, it would be bundled again for every appearance. Thanks to
  **pcompassion** for the report (`#15`_).

.. _#15: https://github.com/sergei-maertens/django-systemjs/issues/15

1.3.2
-----

* let the finder also serve ``SYSTEMJS_OUTPUT_DIR``, next to the ``jspm_packages``
  folder

1.3.1
-----

* Fixed a url path splitting bug

1.3.0
-----
* Fixes in the documentation
* Added the ``--minify`` option for bundling

1.2.0
-----

* Added a staticifles finder: ``systemjs.finders.SystemFinder``. Thanks to
  https://github.com/wkevina for the report that lead to this.

* Added proper documentation on readthedocs.org


1.1.1
-----

Fixes loading of the configuration options in tests.

In previous releases, using ``django.test.utils.override_settings`` in certain
ways happened before the django-systemjs settings were appended. This was
probably only the case for Django < 1.9.


1.1.0
-----
Small feature release with improvements:

* Added ``systemjs.storage.SystemJSManifestStaticFilesStorage``
  staticfiles storage backend. **It is required if you want to use the
  ``django.contrib.staticfiles.storage.ManifestStaticFilesStorage`` with
  django-systemjs.**

  django-systemjs runs the post-process hook, which in turn calls
  ``save_manifest``. The Django shipped version then deletes the old manifest,
  but we don't know anything about the staticfiles in django-systemjs. This
  storage backend makes sure to not delete the staticfiles manifest, it only
  adds to it.

* Better treatment of ``sourceMap`` comments.

  JSPM creates the sourcemap and adds a ``// sourceMap=...`` comment to the
  generated bundle. django-systemjs added the ``System.import(...)`` statement
  to this bundle, causing the sourcemap comment to not be the last line of the
  file. This is fixed in this release.

1.0.2
-----
Too soon on 1.0.1, missed another extension append case.

1.0.1
-----
Bugfix related to ``DEFAULT_JS_EXTENSIONS``: when bundling a file that has the
extension, it would be added again, leading to duplicate extensions.

1.0
---
Added DEFAULT_JS_EXTENSIONS setting, as present in ``jspm``.
Added Django 1.9 to the build matrix.

0.3.4
-----
Fixes some mistakes from 0.3.3. Mondays...

0.3.3
-----
Added post-processing of ``jspm_packages/system.js`` if it is within
``settings.STATIC_ROOT``.

This introduces a new setting: ``SYSTEMJS_PACKAGE_JSON_DIR``. Set this to the path
of the folder containing ``package.json``. ``package.json`` will be inspected to
figure out the install path of jspm - and only post-process if the latter path
is within ``settings.STATIC_ROOT``. By default, ``settings.BASE_DIR`` (provided by
the default ``django-admin.py startproject`` template) will be chosen for this
directory.

0.3.2
-----
Fixed incorrect passing of the --log option.

0.3.1
-----

No API changes where made - this release is preparation for Django 1.9 and
improves robustness of bundling.

In version 0.16.3 ``--log`` was added to JSPM. This allows us to properly check
for build errors, where before you would find out the hard way. Build errors
will now show as output from the management command.

An check has been added to figure out the JSPM version. If you get a
``BundleError`` saying that the JSPM version could not be determined, check that
``jspm`` is available in your path or modify the ``SYSTEMJS_JSPM_EXECUTABLE``
setting accordingly.


0.3.0
-----

Changed the templatetag to add the .js extension. Existing code should still
work, possibly you need to set System.defaultJSExtensions to ``true``.


.. note::

    Possibly breaking change! This release is required if you use SystemJS >=
    0.17. The default.js extension is no longer added by SystemJS.

