from typing import Callable, List, Optional
from email.utils import formatdate, parsedate
from datetime import datetime
from calendar import timegm

from rivr.request import Request
from rivr.response import (
    Http404,
    Response,
    ResponseNotAllowed,
    ResponseRedirect,
    ResponsePermanentRedirect,
    RESTResponse,
    ResponseNoContent,
    ResponseNotModified,
)

__all__ = ['View', 'RedirectView']


class View(object):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def as_view(cls, **initkwargs) -> Callable[..., Response]:
        """
        This method will return a callable which will generate a new instance
        of the class passing it the kwargs passed to it.

        Usage::

            view = View.as_view()
            response = view(request)

        """

        def view(*args, **kwargs) -> Response:
            return cls(**initkwargs).dispatch(*args, **kwargs)

        return view

    def get_handler(self, request: Request) -> Callable[..., Response]:
        if request.method.lower() in self.http_method_names:
            return getattr(self, request.method.lower(), self.http_method_not_allowed)
        return self.http_method_not_allowed

    def dispatch(self, request: Request, *args, **kwargs) -> Response:
        self.request = request
        self.args = args
        self.kwargs = kwargs

        return self.get_handler(request)(request, *args, **kwargs)

    def http_method_not_allowed(self, request: Request, *args, **kwargs) -> Response:
        return ResponseNotAllowed(self.get_allowed_methods())

    def get_allowed_methods(self) -> List[str]:
        allowed_methods = [m for m in self.http_method_names if hasattr(self, m)]
        if not hasattr(self, 'get'):
            allowed_methods.remove('head')

        return allowed_methods

    def options(self, request: Request, *args, **kwargs) -> Response:
        allowed_methods = [m.upper() for m in self.get_allowed_methods()]
        response = ResponseNoContent()
        response.headers['Allow'] = ','.join(allowed_methods)
        return response

    def head(self, request: Request, *args, **kwargs) -> Response:
        get = getattr(self, 'get', None)
        if get:
            response = get(request, *args, **kwargs)
            response.content = ''
            return response

        return self.http_method_not_allowed(request, *args, **kwargs)


class RedirectView(View):
    """
    The redirect view will redirect on any GET requests.
    """

    permanent = True
    url: Optional[str] = None
    query_string = False

    def get_redirect_url(self, **kwargs) -> Optional[str]:
        """
        Return the URL we should redirect to
        """

        if self.url:
            args = self.request.META["QUERY_STRING"]
            if args and self.query_string:
                url = "%s?%s" % (self.url, args)
            else:
                url = self.url
            return url % kwargs
        return None

    def get(self, request: Request, *args, **kwargs) -> Response:
        url = self.get_redirect_url(**kwargs)
        if url:
            if self.permanent:
                return ResponsePermanentRedirect(url)
            return ResponseRedirect(url)
        raise Http404("Redirect URL not found.")
