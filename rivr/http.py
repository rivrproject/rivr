from Cookie import SimpleCookie, CookieError

def parse_cookie(cookie):
    if cookie == '':
        return {}
    
    try:
        c = SimpleCookie()
        c.load(cookie)
    except CookieError:
        return {}
    
    cookiedict = {}
    for key in c.keys():
        cookiedict[key] = c.get(key).value
    
    return cookiedict

class Http404(Exception): pass

class Request(object):
    def __init__(self, path='/', method='GET', GET={}, POST={}):
        self.path = path
        self.method = method
        self.GET = GET
        self.POST = POST

class Response(object):
    status_code = 200
    
    def __init__(self, content='', status=None, content_type='text/html; charset=utf8'):
        self.content = content
        
        if status:
            self.status_code = status
        
        self.headers = {'Content-Type': content_type}
    
    def __str__(self):
        return '\n'.join(['%s: %s' % (key, value) for key, value in self.headers.items()]) + '\n\n' + self.content

class ResponseRedirect(Response):
    status_code = 302
    
    def __init__(self, redirect_to):
        super(ResponseRedirect, self).__init__()
        self.headers['Location'] = str(redirect_to)

class ResponsePermanentRedirect(ResponseRedirect):
    status_code = 301

class ResponseNotFound(Response):
    status_code = 404

class ResponseNotModified(Response):
    status_code = 304
