"""
Example rivr.sessions using a in-memory session store which is
not persistent across restarts. See the documentation for
persistent sessions.
"""

import rivr
from rivr.sessions import *

class SessionView(rivr.views.TemplateView):
    template_name = "sessions.html"

    def get_context_data(self, **kwargs):
        kwargs['session_key'] = self.request.session.session_key
        kwargs['session'] = self.request.session.data
        return kwargs

    def post(self, request, *args, **kwargs):
        request.session['name'] = request.POST.get('name')
        return self.get(request, *args, **kwargs)

class ClearView(rivr.views.RedirectView):
    url = '/'
    permanent = False

    def get(self, request, *args, **kwargs):
        request.session.clear()
        return super(ClearView, self).get(request, *args, **kwargs)

router = rivr.Router(
    (r'^clear/$', ClearView.as_view()),
    (r'^$', SessionView.as_view())
)

app = rivr.MiddlewareController(router,
    SessionMiddleware(session_store=MemorySessionStore()),
    rivr.TemplateMiddleware(template_dirs='example_templates/')
)

if __name__ == '__main__':
    rivr.serve(app)

