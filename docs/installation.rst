============
Installation
============

Django
======

Install by running:

.. code-block:: sh

   pip install django-systemjs

Then, add ``systemjs`` to your ``settings.INSTALLED_APPS``, and add the custom
staticfiles finder:

.. code-block:: python

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'systemjs.finders.SystemFinder',
    ]

The custom finder looks up files in ``STATIC_ROOT`` directly. It is not needed
if you use ``django-compressor`` and have ``COMPRESS_ROOT`` set to
``STATIC_ROOT`` (which is the default).

If you want to use
``django.contrib.staticfiles.storage.ManifestStaticFilesStorage`` as
staticfiles storage backend, you need to use the systemjs-version:
``systemjs.storage.SystemJSManifestStaticFilesStorage``. This storage ensures
two things:
  * during bundling the collected staticfiles (from ``collectstatic``) aren't
    removed from the manifest file.
  * during collectstatic the bundled files are kept in the manifest.

There are some :ref:`application settings <available-settings>` to customize
behaviour. Usually you shouldn't need to change these, since they have sane
defaults.


JSPM
====

Since you found this django app, you probably already know what jspm is and how
to install it. There is some django-specific configuration to be done to make
everything play nicely together.

.. note::
  Currently there are two jspm branches active: 0.16.x and 0.17.x (beta). The
  beta has some backwards incompatibilities with 0.16, and most of all, some
  great features to speed up development. In general, I recommend using 0.17.x,
  even more so if you're going to do React.js stuff.

Setting up jspm for the first time
----------------------------------

If you have worked with jspm before, you can skip this.

To install ``jspm`` (http://jspm.io), you'll need some front-end tooling.
Make sure you have ``nodejs`` and ``npm`` installed on your system. See the
`nodejs installation instructions`_.

If you never installed ``jspm`` before, install it globally for the first time:

.. code-block:: sh

   sudo npm install -g jspm

This ensures that the ``jspm`` cli is available in your ``$PATH``.

.. _nodejs installation instructions: https://nodejs.org/en/download/package-manager/


jspm 0.17.x (beta) instructions
-------------------------------

There is an `example project`_ with detailed installation and configuration
information, aimed at the 0.17 beta version of jspm. The README.md contains a
step-by-step history to get to a working setup with the standard Django project
layout.

.. _example project: https://github.com/sergei-maertens/django-systemjs/tree/develop/example/jspm_0_17


jspm 0.16.x (stable) instructions
---------------------------------

jspm uses the ``package.json`` from NodeJS, so get that set-up first:

.. code-block:: sh

    npm init

This will bring up an interactive prompt to ask for some package information.

Next, install ``jspm`` locally in your project, and pin its version:

.. code-block:: sh

   npm install --save-dev jspm

It's now time to initialize your ``jspm`` project. This is an interactive prompt
again, but we'll need to deviate from the defaults a bit to make it play nice
with Django.

.. code-block:: sh

    jspm init

    Would you like jspm to prefix the jspm package.json properties under jspm? [yes]: yes  # easier to keep track of jspm-specific settings/packages

    Enter server baseURL (public folder path) [/]: static  # same as settings.STATIC_ROOT, relative to package.json

    Enter jspm packages folder [static/jspm_packages]:  # keep it within settings.STATIC_ROOT

    Enter config file path [static/config.js]: my-project/static/config.js  # must be kept in version control, so somewhere where collectstatic can find it

    Enter client baseURL (public folder URL) [/]: /static/ # set to settings.STATIC_URL

    Do you wish to use a transpiler? [yes]: # current browsers don't have full support for ES6 yet

    Which ES6 transpiler would you like to use, Traceur or Babel? [traceur]: babel  # better tracebacks


Take some time to read the `jspm docs`_ if you're not familiar with it yet.

.. note::
  A few settings are remarkable. We put ``jspm_packages`` in ``settings.STATIC_ROOT``.
  This means that collectstatic will not post-process the files in here, which
  can be a problem. Django-SystemJS deals with this specific use case as it is
  intended for ``jspm``-users. There is an inherent limitation within jspm
  which should be lifted with the 0.18 release.

.. _jspm docs: https://github.com/jspm/jspm-cli/tree/master/docs

