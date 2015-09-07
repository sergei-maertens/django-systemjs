Changelog
=========

0.3.0
-----

Changed the templatetag to add the .js extension. Existing code should still
work, possibly you need to set System.defaultJSExtensions to `true`.


.. note::

    Possibly breaking change! This release is required if you use SystemJS >=
    0.17. The default.js extension is no longer added by SystemJS.

