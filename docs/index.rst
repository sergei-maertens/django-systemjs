.. Django-Systemjs documentation master file, created by
   sphinx-quickstart on Thu Apr 7 22:03:38 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


===============
Django-Systemjs
===============

.. rubric:: Modern Javascript in Django.

.. image:: https://travis-ci.org/sergei-maertens/django-systemjs.png
    :target: http://travis-ci.org/sergei-maertens/django-systemjs

.. image:: https://coveralls.io/repos/sergei-maertens/django-systemjs/badge.svg
    :target: https://coveralls.io/github/sergei-maertens/django-systemjs?branch=master

.. image:: https://img.shields.io/pypi/v/django-systemjs.svg
    :target: https://pypi.python.org/pypi/django-systemjs


Overview
========

Django SystemJS brings the Javascript of tomorrow to Django, today.

It leverages JSPM (https://jspm.io) to do the heavy lifting for your
client side code, while keeping development flow easy and deployment
without worries. In DEBUG mode, your Javascript modules are loaded
asynchronously. In production, your app is nicely bundled via JSPM
and ties in perfectly with ``django.contrib.staticfiles``.


Requirements
============

Django-Systemjs runs on Python 2.7, 3.3, 3.4 and 3.5. Django versions 1.8 and
1.9 are supported.



Contents
========

.. toctree::
   :maxdepth: 2

   getting_started
   contributing


License
=======

Licensed under the `MIT License`_.


Souce Code and contributing
===========================

The source code can be found on github_.

Bugs can also be reported on the github_ repository, and pull requests
are welcome. See :ref:`contributing` for more details.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _django: http://www.djangoproject.com/
.. _MIT License: http://en.wikipedia.org/wiki/MIT_License
.. _github: https://github.com/sergei-maertens/django-systemjs
