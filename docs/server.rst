======
Server
======

You can serve rivr with either the build in development server, or you can use
any WSGI compatible server such as gunicorn.

Development Server
==================

By default, the development server can be used with any rivr callable view,
this includes middleware and views.

.. autofunction:: rivr.serve

The development server automatically returns pretty HTML error pages, this can
be turned off by setting the debug keyword to `False`.

.. code-block:: python

    import rivr

    def example_view(request):
        return rivr.Response('<html><body>Hello world!</body></html>')

    if __name__ == '__main__':
        rivr.serve(example_view)

WSGI Server
===========

It's really simple to use a WSGI server, you can use rivr's WSGIHandler to wrap
your rivr callable view.

.. code-block:: python

    import rivr
    from rivr.wsgi import WSGIHandler

    def example_view(request):
        return rivr.Response('<html><body>Hello world!</body></html>')

    wsgi = WSGIHandler(example_view)

Then you can simply point your WSGI server to the wsgi method. For example, to
do this with gunicorn you can run the following:

.. code-block:: bash

    $ gunicorn example_wsgi:wsgi

