=====================
Django SystemJS
=====================

.. image:: https://travis-ci.org/sergei-maertens/django-systemjs.svg?branch=master
    :target: https://travis-ci.org/sergei-maertens/django-systemjs


.. image:: https://coveralls.io/repos/sergei-maertens/django-systemjs/badge.svg
  :target: https://coveralls.io/r/sergei-maertens/django-systemjs

.. image:: https://img.shields.io/pypi/v/django-systemjs.svg
  :target: https://pypi.python.org/pypi/django-systemjs


.. image:: https://readthedocs.org/projects/django-systemjs/badge/?version=latest
    :target: http://django-systemjs.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status


Django SystemJS brings the Javascript of tomorrow to Django, today.

It leverages JSPM (https://jspm.io) to do the heavy lifting for your
client side code, while keeping development flow easy and deployment
without worries. In DEBUG mode, your Javascript modules are loaded
asynchronously. In production, your app is nicely bundled via JSPM
and ties in perfectly with `django.contrib.staticfiles`.


Installation
============

Follow the documentation on http://django-systemjs.readthedocs.org/en/latest/.
