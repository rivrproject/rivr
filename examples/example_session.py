"""
Example rivr.sessions using a in-memory session store which is
not persistent across restarts. See the documentation for
persistent sessions.
"""

import rivr
from rivr.views import View
from rivr.sessions import *

SESSION_HTML = """
<a href="/clear/">Clear Session</a>

<h2>Current Session</h2>
<p>Session Key: {session_key}</p>
<code>{session}</code>

<h2>Set Name</h2>
<form action="" method="post" accept-charset="utf-8">
    <p>Name: <input type="text" name="name" value=""></p>
    <p><input type="submit" value="Continue &rarr;"></p>
</form>
"""


class SessionView(View):
    def get(self, *args, **kwargs):
        return Response(SESSION_HTML.format(
            session_key=self.request.session.session_key,
            session=self.request.session.data,
        ))

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

app = rivr.MiddlewareController.wrap(
    router,
    SessionMiddleware(session_store=MemorySessionStore())
)

if __name__ == '__main__':
    rivr.serve(app)
