import json
import logging
import sys
from typing import Any, Callable, Dict, Iterable
from urllib.parse import parse_qsl

from rivr.http.request import Query, Request, parse_cookie
from rivr.http.response import Http404, Response, ResponseNotFound

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


class WSGIRequest(Request):
    """
    https://wsgi.readthedocs.io/en/latest/definitions.html
    """

    def __init__(self, environ: Dict[str, Any]):
        method: str = environ['REQUEST_METHOD']
        path: str = environ['PATH_INFO']

        query = Query(environ.get('QUERY_STRING', ''))

        super(WSGIRequest, self).__init__(
            path, method, query=query, body=environ['wsgi.input']
        )

        self.environ = environ
        self.META = environ

        if 'HTTP_HOST' in environ:
            self.host = environ['HTTP_HOST']
        else:
            self.host = environ['SERVER_NAME']

        content_type = self.environ.get('CONTENT_TYPE', None)
        if content_type:
            self.content_type = content_type

        content_length = self.environ.get('CONTENT_LENGTH', None)
        if content_length:
            self.headers['Content-Length'] = content_length

        for key in self.META:
            if key.startswith('HTTP_'):
                self.headers[key[5:].replace('_', '-')] = self.META[key]

    @property
    def is_secure(self) -> bool:
        """
        Returns True if connection was made over HTTPS/TLS.
        """

        return self.scheme == 'https'

    @property
    def scheme(self) -> str:
        """
        Scheme used for the request. For example, `https`.
        """

        return self.environ['wsgi.url_scheme']

    @property
    def port(self) -> int:
        """
        Port used for the connection.
        """

        return int(self.environ['SERVER_PORT'])

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

    # Attributes

    @property
    def attributes(self):
        """
        A request body, deserialized as a dictionary.

        This will automatically deserialize form or JSON encoded request
        bodies.
        """

        if not hasattr(self, '_attributes'):
            if self.content_length and self.content_length > 0:
                content = self.body.read(self.content_length)
                content_type = self.content_type.split(';')[0]

                if content_type == 'application/json':
                    content = content.decode('utf-8')
                    self._attributes = json.loads(content)
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
        if not hasattr(self, '_cookies'):
            self._cookies = parse_cookie(self.headers.get_all('Cookie'))

        return self._cookies


class WSGIHandler(object):
    request_class = WSGIRequest

    def __init__(self, view: Callable[[Request], Response]):
        self.view = view

    def __call__(
        self, environ: Dict[str, Any], start_response: Callable[[str, Any], Any]
    ) -> Iterable[bytes]:
        request = self.request_class(environ)

        try:
            response = self.view(request)
            if not response:
                raise Exception("View did not return a response.")
        except Http404:
            response = ResponseNotFound('Page not found')
        except Exception:
            logger.error(
                'Internal Server Error: {}'.format(request.path),
                exc_info=sys.exc_info(),
                extra={'status_code': 500, 'request': request},
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

        return [response_content]
