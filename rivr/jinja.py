from rivr.http import Response
from rivr.views.base import TemplateView
from rivr.middleware import Middleware

from jinja2 import Environment

class JinjaResponse(Response):
    def __init__(self, request, template_name, context, env=None, *args, **kwargs):
        super(JinjaResponse, self).__init__()
        self.request = request
        self.template_name = template_name
        self.context = context
        self._content = None
        self.jinja_env = env

        if 'request' not in self.context:
            self.context['request'] = request

    def get_env(self):
        if self.jinja_env:
            return self.jinja_env

        if hasattr(self.request, 'jinja_env'):
            return self.request.jinja_env

        raise Exception("JinjaResponse is improperly configured"
                        "and requires a jinja environment")

    def render(self):
        t = self.get_env().get_template(self.template_name)
        return t.render(self.context)

    def get_content(self):
        if not self._content:
            self._content = self.render()

        return self._content

    def set_content(self, value):
        pass
    content = property(get_content, set_content)


class JinjaView(TemplateView):
    response_class = JinjaResponse


class JinjaMiddleware(Middleware):
    def __init__(self, env, *args, **kwargs):
        self.jinja_env = env
        super(JinjaMiddleware, self).__init__(*args, **kwargs)

    def process_response(self, request, response):
        if isinstance(response, JinjaResponse):
            response.jinja_env = self.jinja_env
        return response
