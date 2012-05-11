from rivr.middleware.base import Middleware
from rivr.http import Response, ResponseNotFound, Http404

class MiddlewareController(Middleware):
    """
    The middleware controller allows you to wrap a view in multiple middleware.

    Example usage::

        view = MiddlewareController.wrap(view,
            FirstMiddleware(),
            SecondMiddleware()
        )

        response = view(request)
    """

    def __init__(self, *middleware):
        self.request_middleware = []
        self.response_middleware = []
        self.exception_middleware = []

        for mw_instance in middleware:
            self.append(mw_instance)

    def append(self, middleware):
        if hasattr(middleware, 'process_request'):
            self.request_middleware.append(middleware.process_request)
        if hasattr(middleware, 'process_response'):
            self.response_middleware.insert(0, middleware.process_response)
        if hasattr(middleware, 'process_exception'):
            self.exception_middleware.insert(0, middleware.process_exception)

    def process_request(self, request):
        for request_mw in self.request_middleware:
            response = request_mw(request)
            if response:
                return response

    def process_response(self, request, response):
        for response_mw in self.response_middleware:
            response = response_mw(request, response)

        return response

    def process_exception(self, request, exception):
        for exception_mw in self.exception_middleware:
            response = exception_mw(request, e)
            if response:
                return response
        else:
            raise exception

class ErrorWrapper(object):
    def __init__(self, app, custom_404=None, custom_500=None):
        self.app = app
        self.error_404 = custom_404 or self.default_error_404
        self.error_500 = custom_500 or self.default_error_500

    def __call__(self, request, *args, **kwargs):
        try:
            response = self.app(request, *args, **kwargs)
        except Http404, e:
            response = self.error_404(request, e)
        except Exception, e:
            response = self.error_500(request, e)

        if not response:
            response = self.error_404(request, Http404())

        return response

    def default_error_404(self, request, e):
        return ResponseNotFound("404: %s" % e)

    def default_error_500(self, request, e):
        return Response("A 500 has occured", status=500)
