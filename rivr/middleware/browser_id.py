from browserid import verify

from rivr.http import Response, ResponseRedirect, ResponseNotFound
from rivr.middleware.base import Middleware

class BrowserIDMiddleware(Middleware):
    audience = None

    login_success_url = '/'
    login_failure_url = '/'
    logout_redirect_url = '/'

    def login(self, request):
        data = verify(request.POST['assertion'], self.audience)

        if data and 'email' in data:
            request.session['browserid'] = data['email']
            return ResponseRedirect(self.login_success_url)

        return ResponseRedirect(self.login_failure_url)

    def logout(self, request):
        request.browserid = None

        if 'browserid' in request.session:
            del request.session['browserid']

        return ResponseRedirect(self.logout_redirect_url)

    def process_request(self, request):
        if 'browserid' in request.session:
            request.browserid = request.session['browserid']
        else:
            request.browserid = None

        if request.path == '/browserid/login/':
            return self.login(request)
        elif request.path == '/browserid/logout/':
            return self.logout(request)


