from typing import Optional, Callable
from rivr.request import Request
from rivr.response import Response

__all__ = ['Middleware']


class Middleware(object):
    @classmethod
    def wrap(cls, view: Callable[..., Response], *initargs, **initkwargs):
        """
        The wrap method allows you to wrap a view calling the middleware's
        process_request and process_response before and after the view.

        If the view raises an exception, the process_exception method will be
        called.

        Example::

            view = Middleware.wrap(view)
            response = view(request)

        """

        def func(*args, **kwargs) -> Response:
            return cls(*initargs, **initkwargs).dispatch(view, *args, **kwargs)

        return func

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def dispatch(
        self, view: Callable[..., Response], request: Request, *args, **kwargs
    ) -> Response:
        response = self.process_request(request)

        if response is None:
            try:
                response = view(request, *args, **kwargs)
            except Exception as e:
                process_exception: Optional[
                    Callable[[Request, Exception], Optional[Response]]
                ] = getattr(self, 'process_exception')
                if process_exception:
                    response = process_exception(request, e)
                    if not response:
                        raise
                else:
                    raise

        return self.process_response(request, response)

    def process_request(self, request: Request) -> Optional[Response]:
        """
        This method is called before the view on each request. This method
        should either return a response or None. If it returns a response, then
        the middleware will not call the view. If it returns None, then we will
        call the view.
        """
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        """
        This method will take the response, either from process_request or the
        view. This method will always be called for each request unless there
        is an exception.

        This method must return a response, this can either be the response
        passed to it, or a completely new response.
        """
        return response
