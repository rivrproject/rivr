import sys
import logging

try:
    from urllib.parse import parse_qsl
except ImportError:
    from cgi import parse_qsl

from rivr.request import parse_cookie, Request
from rivr.response import Response, ResponseNotFound, Http404
from rivr.utils import JSON_CONTENT_TYPES, JSONDecoder

logger = logging.getLogger('rivr.request')

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

    @property
    def headers(self):
        if not hasattr(self, '_headers'):
            headers = {}

            for key in self.META:
                if key.startswith('HTTP_'):
                    headers[key[5:]] = self.META[key]

            self._headers = headers
        return self._headers

    @property
    def is_secure(self):
        """
        Returns True if connection was made over HTTPS/TLS.
        """

        return self.scheme == 'https'

    @property
    def scheme(self):
        """
        Scheme used for the request. For example, `https`.
        """

        return self.environ['wsgi.url_scheme']

    @property
    def host(self):
        """
        Hostname used for the request. For example, `rivr.com`.
        """

        host = self.environ.get('HTTP_HOST', None)

        if host is None:
            host = self.environ.get('SERVER_NAME', None)

        return host

    @property
    def port(self):
        """
        Port used for the connection.
        """

        default = 443 if self.is_secure else 80
        return int(self.environ.get('SERVER_HTTP_PORT', default))

    @property
    def url(self):
        """
        Hostname used for the request. For example, `https://rivr.com/about`.
        """

        scheme = self.scheme
        url = scheme + '://' + self.host
        port = self.port
        if (scheme == 'http' and port != 80) or (scheme == 'https' and port != 443):
            url += ':' + str(port)

        return url + self.path

    @property
    def content_length(self):
        """
        Returns the length of the request's body.
        """

        try:
            content_length = int(self.environ.get('CONTENT_LENGTH', 0))
        except (ValueError, TypeError):
            content_length = 0

        return content_length

    @property
    def body(self):
        """
        Request body (file descriptor).
        """

        return self.environ['wsgi.input']

    #@property
    def get_get(self):
        if not hasattr(self, '_get'):
            query_string = self.environ.get('QUERY_STRING', '')
            self._get = dict((k, v) for k, v in parse_qsl(query_string, True))
        return self._get
    GET = property(get_get)

    # Attributes

    @property
    def attributes(self):
        """
        A request body, deserialized as a dictionary.

        This will automatically deserialize form or JSON encoded request
        bodies.
        """

        if not hasattr(self, '_attributes'):
            if self.content_length > 0:
                content = self.body.read(self.content_length)
                content_type = self.environ.get('CONTENT_TYPE', None)
                content_type = content_type.split(';')[0]

                if content_type in JSON_CONTENT_TYPES:
                    content = content.decode('utf-8')
                    self._attributes = JSONDecoder().decode(content)
                elif content_type == 'application/x-www-form-urlencoded':
                    content = content.decode('utf-8')
                    data = parse_qsl(content, True)
                    self._attributes = dict((k, v) for k, v in data)
            else:
                self._attributes = {}

        return self._attributes

    POST = attributes  # Deprecated

    @property
    def cookies(self):
        """
        Dictionary returning all of the cookies sent with the request.
        """

        if not hasattr(self, '_cookies'):
            self._cookies = parse_cookie(self.headers.get('COOKIE', ''))
        return self._cookies

    COOKIES = cookies  # legacy


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
        except Http404:
            response = ResponseNotFound('Page not found')
        except Exception:
            logger.error('Internal Server Error: {}'.format(request.path),
                exc_info=sys.exc_info(),
                extra={
                    'status_code': 500,
                    'request': request
                }
            )

            response = Response('Internal server error', status=500)

        try:
            status_text = STATUS_CODES[response.status_code]
        except KeyError:
            status_text = 'UNKNOWN STATUS CODE'

        status = '%s %s' % (response.status_code, status_text)

        start_response(status, response.headers_items())

        response_content = response.content

        if isinstance(response_content, str):
            response_content = response_content.encode('utf-8')
        elif sys.version_info[0] < 3 and isinstance(response.content, unicode):
            response_content = response_content.encode('utf-8')

        return [response_content]

