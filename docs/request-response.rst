============================
Request and Response objects
============================

.. automodule:: rivr.http

HTTP Message
============

.. autoclass:: rivr.http.message.HTTPMessage

   :members: headers, content_type, content_length

Request
=======

.. autoclass:: rivr.http.request.Query

   .. automethod:: __str__
   .. automethod:: __len__
   .. automethod:: __contains__
   .. automethod:: __getitem__

.. autoclass:: Request

    :members: method, path, query, headers, cookies, body

Response
========

.. autoclass:: Response
    :members: status_code

.. autoclass:: ResponseNoContent
.. autoclass:: ResponseRedirect
    :members: url

.. autoclass:: ResponsePermanentRedirect
.. autoclass:: ResponseNotFound
.. autoclass:: ResponseNotModified
.. autoclass:: ResponseNotAllowed
