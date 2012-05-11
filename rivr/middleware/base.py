class Middleware(object):
    @classmethod
    def wrap(cls, view, *initargs, **initkwargs):
        """
        The wrap method allows you to wrap a view calling the middleware's
        process_request and process_response before and after the view.

        If the view raises an exception, the process_exception method will be
        called.

        Example::

            view = Middleware.wrap(view)
            response = view(request)

        """
        def func(*args, **kwargs):
            return cls(*initargs, **initkwargs).dispatch(view, *args, **kwargs)
        return func

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def dispatch(self, view, request, *args, **kwargs):
        response = self.process_request(request)

        if not response:
            try:
                response = view(request, *args, **kwargs)
            except Exception, e:
                if hasattr(self, 'process_exception'):
                    response = self.process_exception(request, e)
                else:
                    raise e

        return self.process_response(request, response)

    def process_request(self, request):
        """
        This method is called before the view on each request. This method
        should either return a response or None. If it returns a response, then
        the middleware will not call the view. If it returns None, then we will
        call the view.
        """
        return

    def process_response(self, request, response):
        """
        This method will take the response, either from process_request or the
        view. This method will always be called for each request unless there
        is an exception.

        This method must return a response, this can either be the response
        passed to it, or a completely new response.
        """
        return response


