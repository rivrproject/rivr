from rivr.http import ResponseNotAllowed, ResponseRedirect, ResponsePermanentRedirect
from rivr.template.response import TemplateResponse

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

class TemplateMixin(object):
    template_name = None
    response_class = TemplateResponse

    def get_template_names(self):
        if self.template_name is None:
            raise Exception("TemplateResponseMixin requires either a"
                            "definition of 'template_name' or a"
                            "implementation of 'get_template_names()'")
        return self.template_name

    def render_to_response(self, context):
        return self.response_class(self.request, self.get_template_names(), context)

class TemplateView(TemplateMixin, View):
    def get_context_data(self, **kwargs):
        return {'params': kwargs}

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

