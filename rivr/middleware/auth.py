from base64 import b64decode

try:
    from hashlib import sha256
except ImportError: # Python < 2.5
    try:
        from Crypto.Hash import SHA256
        sha256 = SHA256.new
    except ImportError:
        print "Update to python 2.5+, or install PyCrypto."
        raise ImportError, "No SHA256"

from rivr.http import Response

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

class AuthMiddleware(object):
    def __init__(self, handler, view, needs_auth=True):
        self.handler = handler
        self.view = view
        self.needs_auth = needs_auth
    
    def __call__(self, request, *args, **kwargs):
        request.user = self.check_login(request)
        
        if not request.user.is_authenticated() and self.needs_auth:
            return ResponseAuthorizationRequired()
        
        return self.view(request, *args, **kwargs)
    
    def hash(self, password):
        return sha256(password).hexdigest()
    
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
        
        if self.handler(username, password):
            return User(username)
        
        return AnnonymousUser()
