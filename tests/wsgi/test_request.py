# -*- coding: utf8 -*-

import unittest
from io import BytesIO

from rivr.wsgi import WSGIRequest


class WSGIRequestTest(unittest.TestCase):
    def setUp(self) -> None:
        super(WSGIRequestTest, self).setUp()

        self.environ = {
            'REQUEST_METHOD': 'PATCH',
            'PATH_INFO': '/path/',
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': 443,
            'wsgi.url_scheme': 'https',
        }
        self.request = WSGIRequest(self.environ)

    def test_method(self) -> None:
        assert self.request.method == 'PATCH'

    def test_path(self) -> None:
        assert self.request.path == '/path/'

    def test_headers(self) -> None:
        self.environ['HTTP_HEADERX'] = 'Hello World'
        request = WSGIRequest(self.environ)

        assert request.headers['headerx'] == 'Hello World'

    def test_query_string(self) -> None:
        self.environ['QUERY_STRING'] = 'name=Kyle&something=else'
        request = WSGIRequest(self.environ)

        assert request.GET == {'name': 'Kyle', 'something': 'else'}

    def test_scheme(self) -> None:
        assert self.request.scheme == 'https'

    def test_is_secure_http_scheme(self) -> None:
        self.environ['wsgi.url_scheme'] = 'http'
        self.request = WSGIRequest(self.environ)

        assert not self.request.is_secure

    def test_is_secure_https_scheme(self) -> None:
        self.environ['wsgi.url_scheme'] = 'https'
        self.request = WSGIRequest(self.environ)

        assert self.request.is_secure

    def test_host(self) -> None:
        assert self.request.host == 'example.com'

    def test_host_header_preferred(self) -> None:
        self.environ['HTTP_HOST'] = 'dev.example.com'

        assert self.request.host == 'dev.example.com'

    def test_port(self) -> None:
        assert self.request.port == 443

    def test_url(self) -> None:
        assert self.request.url == 'https://example.com/path/'

    def test_content_type(self) -> None:
        self.environ['CONTENT_TYPE'] = 'text/plain'
        self.request = WSGIRequest(self.environ)

        assert self.request.content_type == 'text/plain'

    def test_content_length(self) -> None:
        self.environ['CONTENT_LENGTH'] = '5'
        self.request = WSGIRequest(self.environ)

        assert self.request.content_length == 5

    def test_body(self) -> None:
        self.environ['wsgi.input'] = BytesIO(b'Hi')
        self.request = WSGIRequest(self.environ)

        assert self.request.body.read() == b'Hi'

    # Attributes

    def test_depreacted_POST_returns_attributes(self) -> None:
        # POST is deprecated, but for now is an alias for attributes
        assert self.request.POST == {}

    def test_attributes_deserializes_form_urlencoded(self) -> None:
        self.environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        self.environ['CONTENT_LENGTH'] = '9'
        self.environ['wsgi.input'] = BytesIO('test=👍'.encode('utf-8'))
        request = WSGIRequest(self.environ)

        assert request.attributes == {'test': '👍'}

    def test_attributes_deserializes_JSON_HTTP_body(self) -> None:
        self.environ['CONTENT_TYPE'] = 'application/json'
        self.environ['CONTENT_LENGTH'] = '16'
        self.environ['wsgi.input'] = BytesIO('{"test": "👍"}'.encode('utf-8'))
        request = WSGIRequest(self.environ)

        assert request.attributes == {'test': '👍'}

    # Cookies

    def test_cookies(self) -> None:
        self.environ['HTTP_COOKIE'] = 'name=Kyle; username=kylef'
        request = WSGIRequest(self.environ)

        assert request.cookies['name'].value == 'Kyle'
        assert request.cookies['username'].value == 'kylef'
