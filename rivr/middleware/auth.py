from base64 import b64decode

from rivr.http import Response
from rivr.middleware.base import Middleware

class ResponseAuthorizationRequired(Response):
    status_code = 401
    
    def __init__(self, *args, **kwargs):
        super(ResponseAuthorizationRequired, self).__init__(*args, **kwargs)
        self.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'

class User(object):
    def __init__(self, username=''):
        self.username = username
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True

class AnnonymousUser(object):
    username = ''
    
    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

class AuthMiddleware(Middleware):
    needs_auth = True

    def process_request(self, request):
        request.user = self.check_login(request)

        if not request.user.is_authenticated() and self.needs_auth:
            return ResponseAuthorizationRequired()

    def check_login(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION', False)
        
        if not authorization:
            return AnnonymousUser()
        
        try:
            method, key = authorization.split()
        except ValueError:
            return AnnonymousUser()
        
        if method != 'Basic':
            return AnnonymousUser()
        
        try:
            username, password = b64decode(key).split(':')
        except ValueError:
            return AnnonymousUser()
        
        if self.check_password(username, password):
            return User(username)
        
        return AnnonymousUser()

    def check_password(self, username, password):
        return False

