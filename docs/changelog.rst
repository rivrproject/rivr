Release History
###############

Master
======

Breaking
--------

* `rivr.templates` has been removed, please migrate to `rivr-jinja`.
* `RESTView` has been removed. Either vendor the old RESTView, or migrate to
  `rivr-rest`.


0.6.0
=====

Views
-----

* Generic View class now has a default implementation of `HEAD`.
* Generic View class now has a default implementation of `OPTIONS`, which
  simply returns the supported HTTP methods.

Contrib
-------

* Completely removed the MongoDB module. This hasn't been maintained in a
  while, if anyone still uses it or is interested in maintaining it. It should
  be moved to a separate module.
* Moved jinja support out into a separate project `rivr-jinja`.
* Removed the BrowserID module.

