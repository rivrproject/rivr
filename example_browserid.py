import rivr
from rivr.views import TemplateView
from rivr.middleware.browser_id import *
from rivr.sessions import *

app = rivr.MiddlewareController(
    TemplateView.as_view(template_name='browserid.html'),

    SessionMiddleware(session_store=MemorySessionStore()),
    BrowserIDMiddleware(audience='*'),
    rivr.TemplateMiddleware(template_dirs='example_templates/')
)

if __name__ == '__main__':
    rivr.serve(rivr.DebugMiddleware(app))
