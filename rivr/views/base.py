from rivr.http import ResponseNotAllowed, ResponseRedirect, ResponsePermanentRedirect


class View(object):
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @classmethod
    def as_view(cls, **initkwargs):
        def view(*args, **kwargs):
            return cls(**initkwargs).dispatch(*args, **kwargs)
        return view

    def get_handler(self, request):
        if request.method.lower() in self.http_method_names:
            return getattr(self, request.method.lower(), self.http_method_not_allowed)
        return self.http_method_not_allowed

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

        return self.get_handler(request)(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        allowed_methods = [m for m in self.http_method_names if hasattr(self, m)]
        return ResponseNotAllowed(allowed_methods)

class RedirectView(View):
    permanent = True
    url = None
    query_string = False

    def get_redirect_url(self, **kwargs):
        if self.url:
            args = self.request.META["QUERY_STRING"]
            if args and self.query_string:
                url = "%s?%s" % (self.url, args)
            else:
                url = self.url
            return self.url % kwargs
        return None

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(**kwargs)
        if url:
            if self.permanent:
                return ResponsePermanentRedirect(url)
            return ResponseRedirect(url)
        raise Http404("Redirect URL not found.")
