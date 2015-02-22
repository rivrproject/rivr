# -*- coding: utf8 -*-

from __future__ import unicode_literals
import unittest

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from rivr.wsgi import WSGIRequest

class WSGIRequestTest(unittest.TestCase):
    def testMethod(self):
        request = WSGIRequest({
            'REQUEST_METHOD': 'PATCH',
        })

        self.assertEqual(request.method, 'PATCH')

    def testPath(self):
        request = WSGIRequest({
            'PATH_INFO': '/path/',
        })

        self.assertEqual(request.path, '/path/')

    def testHeaders(self):
        request = WSGIRequest({
            'HTTP_HEADERX': 'Hello World',
        })

        self.assertEqual(request.headers, {'HEADERX': 'Hello World'})

    def testQueryString(self):
        request = WSGIRequest({
            'QUERY_STRING': 'name=Kyle&something=else',
        })

        self.assertEqual(request.GET, {'name': 'Kyle', 'something': 'else'})

    def testHTTPIsNotSecure(self):
        request = WSGIRequest({
            'wsgi.url_scheme': 'http'
        })

        self.assertFalse(request.is_secure)

    def testHTTPSIsSecure(self):
        request = WSGIRequest({
            'wsgi.url_scheme': 'https'
        })

        self.assertTrue(request.is_secure)

    def testScheme(self):
        request = WSGIRequest({
            'wsgi.url_scheme': 'https'
        })

        self.assertEqual(request.scheme, 'https')

    def testHost(self):
        request = WSGIRequest({
            'HTTP_HOST': 'example.com'
        })

        self.assertEqual(request.host, 'example.com')

    def testPort(self):
        request = WSGIRequest({
            'wsgi.url_scheme': 'https',
            'SERVER_HTTP_PORT': 8080,
        })

        self.assertEqual(request.port, 8080)

    def testURL(self):
        request = WSGIRequest({
            'wsgi.url_scheme': 'https',
            'HTTP_HOST': 'example.com',
            'SERVER_HTTP_PORT': 443,
            'PATH_INFO': '/path/',
        })

        self.assertEqual(request.url, 'https://example.com/path/')

    def testContentLength(self):
        request = WSGIRequest({
            'CONTENT_LENGTH': 5
        })

        self.assertEqual(request.content_length, 5)

    def testBody(self):
        wsgi_input = StringIO('Hi')
        request = WSGIRequest({
            'wsgi.input': wsgi_input,
        })

        self.assertEqual(request.body.read(), 'Hi')

    # Parameters

    def test_parameters(self):
        request = WSGIRequest({
            'QUERY_STRING': 'key=value',
        })

        self.assertEqual(request.parameters, {'key': 'value'})

    def test_deprecated_GET_returns_parameters(self):
        request = WSGIRequest({
            'QUERY_STRING': 'key=value',
        })

        self.assertEqual(request.GET, {'key': 'value'})

    # Attributes

    def test_deprecated_POST_returns_attributes(self):
        # POST is deprecated, but for now is an alias for attributes
        wsgi_input = StringIO('Hi')
        request = WSGIRequest({})

        self.assertEqual(request.POST, {})

    def test_parameters_deserializes_JSON_HTTP_body(self):
        wsgi_input = StringIO('{"test": "👍"}')
        request = WSGIRequest({
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': 16,
            'wsgi.input': wsgi_input,
        })

        self.assertEqual(request.attributes, {'test': '👍'})

