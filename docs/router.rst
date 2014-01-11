######
Router
######

.. automodule:: rivr.router

rivr comes with a powerful regex based path router similar to the url patterns
system in Django.

Example usage:

.. code-block:: python

    import rivr

    router = rivr.Router()

    @router.register(r'^$')
    def index(request):
        return rivr.Response('Hello world')

    @router.register(r'example/$')
    def example(request):
        return rivr.Response('Example')


Similar to Django, it will also pull out pattern matches from the regex and
feed them as arguments and keyword-arguments to your view. For example:

.. code-block:: python

    @router.register(r'^(?P<username>[-\w]+)/$')
    def index(request, username):
        return rivr.Response('Hello %s' % username)

.. autoclass:: Router
    :members: __init__, register, append_slash
