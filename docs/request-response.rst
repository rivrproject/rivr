============================
Request and Response objects
============================

.. automodule:: rivr.http

Request
=======

.. autoclass:: Request

    :members: method, path, query, headers, cookies, body

Response
========

.. autoclass:: Response
    :members:

.. autoclass:: ResponseNoContent
.. autoclass:: ResponseRedirect
    :members:

.. autoclass:: ResponsePermanentRedirect
.. autoclass:: ResponseNotFound
.. autoclass:: ResponseNotModified
.. autoclass:: ResponseNotAllowed

