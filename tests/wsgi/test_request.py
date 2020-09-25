# -*- coding: utf8 -*-

import unittest
from io import StringIO

from rivr.wsgi import WSGIRequest


class WSGIRequestTest(unittest.TestCase):
    def testMethod(self):
        request = WSGIRequest(
            {
                'REQUEST_METHOD': 'PATCH',
            }
        )

        self.assertEqual(request.method, 'PATCH')

    def testPath(self):
        request = WSGIRequest(
            {
                'PATH_INFO': '/path/',
            }
        )

        self.assertEqual(request.path, '/path/')

    def testHeaders(self):
        request = WSGIRequest(
            {
                'HTTP_HEADERX': 'Hello World',
            }
        )

        self.assertEqual(request.headers, {'HEADERX': 'Hello World'})

    def testQueryString(self):
        request = WSGIRequest(
            {
                'QUERY_STRING': 'name=Kyle&something=else',
            }
        )

        self.assertEqual(request.GET, {'name': 'Kyle', 'something': 'else'})

    def testHTTPIsNotSecure(self):
        request = WSGIRequest({'wsgi.url_scheme': 'http'})

        self.assertFalse(request.is_secure)

    def testHTTPSIsSecure(self):
        request = WSGIRequest({'wsgi.url_scheme': 'https'})

        self.assertTrue(request.is_secure)

    def testScheme(self):
        request = WSGIRequest({'wsgi.url_scheme': 'https'})

        self.assertEqual(request.scheme, 'https')

    def testHost(self):
        request = WSGIRequest({'HTTP_HOST': 'example.com'})

        self.assertEqual(request.host, 'example.com')

    def testPort(self):
        request = WSGIRequest(
            {
                'wsgi.url_scheme': 'https',
                'SERVER_HTTP_PORT': 8080,
            }
        )

        self.assertEqual(request.port, 8080)

    def testURL(self):
        request = WSGIRequest(
            {
                'wsgi.url_scheme': 'https',
                'HTTP_HOST': 'example.com',
                'SERVER_HTTP_PORT': 443,
                'PATH_INFO': '/path/',
            }
        )

        self.assertEqual(request.url, 'https://example.com/path/')

    def test_content_type(self):
        request = WSGIRequest(
            {
                'CONTENT_TYPE': 'text/plain',
            }
        )

        self.assertEqual(request.content_type, 'text/plain')

    def testContentLength(self):
        request = WSGIRequest({'CONTENT_LENGTH': 5})

        self.assertEqual(request.content_length, 5)

    def testBody(self):
        wsgi_input = StringIO('Hi')
        request = WSGIRequest(
            {
                'wsgi.input': wsgi_input,
            }
        )

        self.assertEqual(request.body.read(), 'Hi')

    # Attributes

    def test_depreacted_POST_returns_attributes(self):
        # POST is deprecated, but for now is an alias for attributes
        request = WSGIRequest({})
        self.assertEqual(request.POST, {})

    def test_attributes_deserializes_form_urlencoded(self):
        wsgi_input = StringIO('test=👍')
        request = WSGIRequest(
            {
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'CONTENT_LENGTH': 9,
                'wsgi.input': wsgi_input,
            }
        )

        self.assertEqual(request.attributes, {'test': '👍'})

    def test_attributes_deserializes_JSON_HTTP_body(self):
        wsgi_input = StringIO('{"test": "👍"}')
        request = WSGIRequest(
            {
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': 16,
                'wsgi.input': wsgi_input,
            }
        )

        self.assertEqual(request.attributes, {'test': '👍'})

    # Cookies

    def test_cookies(self):
        request = WSGIRequest({'HTTP_COOKIE': str('name=Kyle; username=kylef')})

        self.assertEqual(
            request.cookies,
            {
                'name': 'Kyle',
                'username': 'kylef',
            },
        )
