.. _available-settings:

==================
Available settings
==================

``SYSTEMJS_ENABLED``: defaults to ``not settings.DEBUG``. If disabled, the loading
of modules will happen in the 'standard' jspm way (transpiling in browser).

``SYSTEMJS_JSPM_EXECUTABLE``: path to the ``jspm-cli`` executable. Defaults to
``jspm``, which should be available if installed globally with ``npm``.

``SYSTEMJS_OUTPUT_DIR``: name of the subdirectory within ``settings.STATIC_ROOT``.
Bundled files will end up in this directory, and this is the place the
templatetag will point static files to.

``SYSTEMJS_PACKAGE_JSON_DIR``: directory containing your ``package.json`` file.
This is automatically guessed from ``BASE_DIR``. You will get an error in the
shell if you need to set it yourself.

``SYSTEMJS_DEFAULT_JS_EXTENSIONS``: in prior verions of jspm, the ``.js`` extension
for imports was optional. This is being phased out, and matches the
``defaultJSExtensions`` settings in ``config.js``.

``CACHE_DIR``: directory to keep the dependency cache (when generating
:ref:`minimal <minimal>` bundles)


Environment variables
=====================

``NODE_PATH``
-------------

When generating :ref:`minimal <minimal>` bundles, a NodeJS script
(``trace-deps.js``) is called. This script needs to be called from the directory
containing ``package.json``. If Django-SystemJS cannot figure out this directory
by itself, you may need to set the environment variable:

.. code-block:: sh

    export NODE_PATH=/path/to/project/node_modules

