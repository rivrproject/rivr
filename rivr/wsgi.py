try:
    # The mod_python version is more efficient, so try importing it first.
    from mod_python.util import parse_qsl
except ImportError:
    from cgi import parse_qsl

from rivr.http import parse_cookie, Request, Response, ResponseNotFound, Http404

STATUS_CODES = {
    100: 'CONTINUE',
    101: 'SWITCHING PROTOCOLS',
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    203: 'NON-AUTHORITATIVE INFORMATION',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    206: 'PARTIAL CONTENT',
    300: 'MULTIPLE CHOICES',
    301: 'MOVED PERMANENTLY',
    302: 'FOUND',
    303: 'SEE OTHER',
    304: 'NOT MODIFIED',
    305: 'USE PROXY',
    306: 'RESERVED',
    307: 'TEMPORARY REDIRECT',
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    402: 'PAYMENT REQUIRED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'METHOD NOT ALLOWED',
    406: 'NOT ACCEPTABLE',
    407: 'PROXY AUTHENTICATION REQUIRED',
    408: 'REQUEST TIMEOUT',
    409: 'CONFLICT',
    410: 'GONE',
    411: 'LENGTH REQUIRED',
    412: 'PRECONDITION FAILED',
    413: 'REQUEST ENTITY TOO LARGE',
    414: 'REQUEST-URI TOO LONG',
    415: 'UNSUPPORTED MEDIA TYPE',
    416: 'REQUESTED RANGE NOT SATISFIABLE',
    417: 'EXPECTATION FAILED',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
    505: 'HTTP VERSION NOT SUPPORTED',
}

class WSGIRequest(object):
    def __init__(self, environ):
        self.environ = environ
        
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()
        self.path = environ.get('PATH_INFO', '/')
        self.META = environ
    
    #@property
    def get_get(self):
        if not hasattr(self, '_get'):
            self._get = dict((k,v) for k,v in parse_qsl(self.environ.get('QUERY_STRING', ''), True))
        return self._get
    GET = property(get_get)
    
    #@property
    def get_post(self):
        if not hasattr(self, '_post'):
            try:
                content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            
            if content_length > 0:
                body = self.environ['wsgi.input'].read(int(self.environ.get('CONTENT_LENGTH', 0)))
                self._post = dict((k,v) for k,v in parse_qsl(body, True))
            else:
                self._post = {}
        return self._post
    POST = property(get_post)
    
    #@property
    def get_cookies(self):
        if not hasattr(self, '_cookies'):
            self._cookies = parse_cookie(self.environ.get('HTTP_COOKIE', ''))
        return self._cookies
    COOKIES = property(get_cookies)

class WSGIHandler(object):
    request_class = WSGIRequest
    
    def __init__(self, view):
        self.view = view
    
    def __call__(self, environ, start_response):
        request = self.request_class(environ)
        
        try:
            response = self.view(request)
            if not response:
                raise Exception("View did not return a response.")
        except Http404, e:
            response = ResponseNotFound('Page not found')
        except Exception, e:
            response = Response('Internal server error', status=500)
        
        try:
            status_text = STATUS_CODES[response.status_code]
        except KeyError:
            status_text = 'UNKNOWN STATUS CODE'
        
        status = '%s %s' % (response.status_code, status_text)
        
        start_response(status, response.headers_items())
        
        if isinstance(response.content, unicode):
            return [response.content.encode('utf-8')]        
        return [response.content]
