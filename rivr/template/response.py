from rivr.http import Response
from rivr.middleware import Middleware
from rivr.template import Context
from rivr.template.loader import Loader

class TemplateResponse(Response):
    def __init__(self, request, template_name, context, template_dirs=[], *args, **kwargs):
        self.request = request
        self.loader = None
        self.template_name = template_name
        self.context = context
        self.template_dirs = template_dirs
        self.extra_context = {}
        self._content = None
        super(TemplateResponse, self).__init__(*args, **kwargs)
    
    def resolve_template(self):
        self.loader = Loader()
        
        if isinstance(self.template_dirs, list):
            self.loader.template_dirs += self.template_dirs
        else:
            self.loader.template_dirs.append(self.template_dirs)
        
        return self.loader.get_template(self.template_name)
    
    def resolve_context(self):
        if isinstance(self.context, Context):
            return self.context
        
        c = Context(self.extra_context)
        c.push({'request':self.request, 'loader':self.loader})
        c.push(self.context)
        self.context = c
        
        return self.context
    
    def render(self):
        t = self.resolve_template()
        c = self.resolve_context()
        return t.render(c)
    
    def get_content(self):
        if self._content:
            return self._content
        
        self._content = self.render()
        return self._content
    
    def set_content(self, value):
        pass
    content = property(get_content, set_content)

class TemplateMiddleware(Middleware):
    template_dirs = None
    extra_context = {}

    def process_response(self, request, response):
        if isinstance(response, TemplateResponse):
            response.template_dirs = self.template_dirs
            response.extra_context = self.extra_context

        return response

def direct_to_template(request, template, extra_context={}, **kwargs):
    return TemplateResponse(request, template, extra_context)
