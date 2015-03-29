from email.utils import formatdate, parsedate
from datetime import datetime
from calendar import timegm

from rivr.response import (Response, ResponseNotAllowed, ResponseRedirect,
                           ResponsePermanentRedirect, RESTResponse,
                           ResponseNoContent, ResponseNotModified)


class View(object):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options',
                         'trace']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def as_view(cls, **initkwargs):
        """
        This method will return a callable which will generate a new instance
        of the class passing it the kwargs passed to it.

        Usage::

            view = View.as_view()
            response = view(request)

        """
        def view(*args, **kwargs):
            return cls(**initkwargs).dispatch(*args, **kwargs)
        return view

    def get_handler(self, request):
        if request.method.lower() in self.http_method_names:
            return getattr(self, request.method.lower(),
                           self.http_method_not_allowed)
        return self.http_method_not_allowed

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        return self.get_handler(request)(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseNotAllowed(self.get_allowed_methods())

    def get_allowed_methods(self):
        allowed_methods = [m for m in self.http_method_names if hasattr(self, m)]
        if not hasattr(self, 'get'):
            allowed_methods.remove('head')

        return allowed_methods

    def options(self, request, *args, **kwargs):
        allowed_methods = [m.upper() for m in self.get_allowed_methods()]
        response = ResponseNoContent()
        response.headers['Allow'] = ','.join(allowed_methods)
        return response

    def head(self, request, *args, **kwargs):
        if hasattr(self, 'get'):
            response = self.get(request, *args, **kwargs)
            response.content = ''
            return response

        return self.http_method_not_allowed(request, *args, **kwargs)


class RedirectView(View):
    """
    The redirect view will redirect on any GET requests.
    """

    permanent = True
    url = None
    query_string = False

    def get_redirect_url(self, **kwargs):
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

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(**kwargs)
        if url:
            if self.permanent:
                return ResponsePermanentRedirect(url)
            return ResponseRedirect(url)
        raise Http404("Redirect URL not found.")

