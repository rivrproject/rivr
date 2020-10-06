# -*- coding: utf8 -*-

import unittest
from io import StringIO

from rivr.wsgi import WSGIRequest


class WSGIRequestTest(unittest.TestCase):
    def setUp(self):
        super(WSGIRequestTest, self).setUp()

        self.environ = {
            'REQUEST_METHOD': 'PATCH',
            'PATH_INFO': '/path/',
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': 443,
            'wsgi.url_scheme': 'https',
        }
        self.request = WSGIRequest(self.environ)

    def test_method(self):
        self.assertEqual(self.request.method, 'PATCH')

    def test_path(self):
        self.assertEqual(self.request.path, '/path/')

    def test_headers(self):
        self.environ['HTTP_HEADERX'] = 'Hello World'
        request = WSGIRequest(self.environ)

        self.assertEqual(request.headers['headerx'], 'Hello World')

    def test_query_string(self):
        self.environ['QUERY_STRING'] = 'name=Kyle&something=else'
        request = WSGIRequest(self.environ)

        self.assertEqual(request.GET, {'name': 'Kyle', 'something': 'else'})

    def test_scheme(self):
        self.assertEqual(self.request.scheme, 'https')

    def test_is_secure_http_scheme(self):
        self.environ['wsgi.url_scheme'] = 'http'
        self.request = WSGIRequest(self.environ)

        self.assertFalse(self.request.is_secure)

    def test_is_secure_https_scheme(self):
        self.environ['wsgi.url_scheme'] = 'https'
        self.request = WSGIRequest(self.environ)

        self.assertTrue(self.request.is_secure)

    def test_host(self):
        self.assertEqual(self.request.host, 'example.com')

    def test_host_header_preferred(self):
        self.environ['HTTP_HOST'] = 'dev.example.com'

        self.assertEqual(self.request.host, 'dev.example.com')

    def test_port(self):
        self.assertEqual(self.request.port, 443)

    def test_url(self):
        self.assertEqual(self.request.url, 'https://example.com/path/')

    def test_content_type(self):
        self.environ['CONTENT_TYPE'] = 'text/plain'
        self.request = WSGIRequest(self.environ)

        self.assertEqual(self.request.content_type, 'text/plain')

    def test_content_length(self):
        self.environ['CONTENT_LENGTH'] = '5'
        self.request = WSGIRequest(self.environ)

        self.assertEqual(self.request.content_length, 5)

    def test_body(self):
        self.environ['wsgi.input'] = StringIO('Hi')
        self.request = WSGIRequest(self.environ)

        self.assertEqual(self.request.body.read(), 'Hi')

    # Attributes

    def test_depreacted_POST_returns_attributes(self):
        # POST is deprecated, but for now is an alias for attributes
        self.assertEqual(self.request.POST, {})

    def test_attributes_deserializes_form_urlencoded(self):
        self.environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        self.environ['CONTENT_LENGTH'] = '9'
        self.environ['wsgi.input'] = StringIO('test=👍')
        request = WSGIRequest(self.environ)

        self.assertEqual(request.attributes, {'test': '👍'})

    def test_attributes_deserializes_JSON_HTTP_body(self):
        self.environ['CONTENT_TYPE'] = 'application/json'
        self.environ['CONTENT_LENGTH'] = '16'
        self.environ['wsgi.input'] = StringIO('{"test": "👍"}')
        request = WSGIRequest(self.environ)

        self.assertEqual(request.attributes, {'test': '👍'})

    # Cookies

    def test_cookies(self):
        self.environ['HTTP_COOKIE'] = 'name=Kyle; username=kylef'
        request = WSGIRequest(self.environ)

        self.assertEqual(
            request.cookies,
            {
                'name': 'Kyle',
                'username': 'kylef',
            },
        )
