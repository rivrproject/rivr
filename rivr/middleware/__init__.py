from typing import Optional, Callable, List
from rivr.middleware.base import Middleware
from rivr.request import Request
from rivr.response import Response, ResponseNotFound, Http404


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
        self.request_middleware: List[Callable[[Request], Optional[Response]]] = []
        self.response_middleware: List[Callable[[Request, Response], Response]] = []
        self.exception_middleware: List[
            Callable[[Request, Exception], Optional[Response]]
        ] = []

        for mw_instance in middleware:
            self.append(mw_instance)

    def append(self, middleware: Middleware):
        if hasattr(middleware, 'process_request'):
            self.request_middleware.append(middleware.process_request)

        if hasattr(middleware, 'process_response'):
            self.response_middleware.insert(0, middleware.process_response)

        process_exception = getattr(middleware, 'process_exception', None)
        if process_exception:
            self.exception_middleware.insert(0, process_exception)

    def process_request(self, request: Request) -> Optional[Response]:
        for request_mw in self.request_middleware:
            response = request_mw(request)
            if response:
                return response

        return None

    def process_response(self, request: Request, response: Response) -> Response:
        for response_mw in self.response_middleware:
            response = response_mw(request, response)

        return response

    def process_exception(
        self, request: Request, exception: Exception
    ) -> Optional[Response]:
        for exception_mw in self.exception_middleware:
            response = exception_mw(request, exception)
            if response:
                return response
        else:
            raise


class ErrorWrapper(object):
    def __init__(
        self,
        app: Callable[..., Response],
        custom_404: Optional[Callable[[Request, Exception], Response]] = None,
        custom_500: Optional[Callable[[Request, Exception], Response]] = None,
    ):
        self.app = app
        self.error_404 = custom_404 or self.default_error_404
        self.error_500 = custom_500 or self.default_error_500

    def __call__(self, request: Request, *args, **kwargs) -> Response:
        try:
            response = self.app(request, *args, **kwargs)
        except Http404 as e:
            response = self.error_404(request, e)
        except Exception as e:
            response = self.error_500(request, e)

        if not response:
            response = self.error_404(request, Http404())

        return response

    def default_error_404(self, request: Request, e: Exception) -> Response:
        return ResponseNotFound("404: %s" % e)

    def default_error_500(self, request: Request, e: Exception) -> Response:
        return Response("A 500 has occured", status=500)
