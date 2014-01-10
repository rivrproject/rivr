.. rivr documentation master file, created by
   sphinx-quickstart on Fri May 11 10:26:28 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to rivr's documentation!
================================

rivr is a BSD Licensed WSGI web framework, written in Python.

.. code-block:: python

    import rivr

    def hello_world(request):
        return rivr.Response('<html><body>Hello world!</body></html>')

    if __name__ == '__main__':
        rivr.serve(hello_world)

Contents:

.. toctree::
   :maxdepth: 2

   views
   request-response
   middleware
   server

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

