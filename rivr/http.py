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
    def __init__(self, path='/', method='GET', GET={}, POST={}, COOKIES={}):
        self.path = path
        self.method = method
        self.GET = GET
        self.POST = POST
        self.COOKIES = COOKIES

class Response(object):
    status_code = 200
    
    def __init__(self, content='', status=None, content_type='text/html; charset=utf8'):
        self.content = content
        
        if status:
            self.status_code = status
        
        self.headers = {'Content-Type': content_type}
        self.cookies = SimpleCookie()
    
    def __str__(self):
        return '\n'.join(['%s: %s' % (key, value) for key, value in self.headers.items()]) + '\n\n' + self.content
    
    def set_cookie(self, key, value='', max_age=None, expires=None, path='/', domain=None, secure=False):
        self.cookies[key] = value
        
        if max_age is not None:
            self.cookies[key]['max-age'] = max_age
        
        if expires is not None:
            self.cookies[key]['expires'] = expires
        
        if path is not None:
            self.cookies[key]['path'] = path
        
        if domain is not None:
            self.cookies[key]['domain'] = domain
        
        if secure:
            self.cookies[key]['secure'] = True
    
    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, max_age=0, path=path, domain=domain, expires='Thu, 01-Jan-1970 00:00:00 GMT')
    
    def headers_items(self):
        headers = self.headers.items()
        
        for cookie in self.cookies.values():
            headers.append(('Set-Cookie', str(cookie.output(header=''))))
        
        return headers

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

class ResponseNotAllowed(Response):
    status_code = 405

    def __init__(self, permitted_methods):
        super(ResponseNotAllowed, self).__init__()
        self.headers['Allow'] = ', '.join(permitted_methods)

