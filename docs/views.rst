=====
Views
=====

A view is a simple function which takes a request and returns a response. The
response is then sent to the user, it can be a simple HTML page, a request or
anything.


.. code-block:: python

    import rivr

    def example_view(request):
        return rivr.Response('<html><body>Hello world!</body></html>')

Class-based views
=================

A class-based view is a class which is callable, so it acts just like a normal
function based view. rivr provides a base view class which allows you to
implement methods for the different HTTP methods it wants to handle. For
exaple:

.. code-block:: python

    class BasicView(View):
        def get(self, request):
            return rivr.Response('Get request!')

        def post(self, request):
            return rivr.Response('Post request!')

rivr also provides a other views such as `RedirectView`.

.. automodule:: rivr.views

.. autoclass:: View

    .. automethod:: as_view(**kwargs)

.. autoclass:: RedirectView

    :members: url, permanent

    .. automethod:: get_redirect_url(self, **kwargs)

