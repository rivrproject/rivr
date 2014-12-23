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

    # POST Data

    def testJSONPostDataDeserialisation(self):
        wsgi_input = StringIO('{"test": "👍"}')
        request = WSGIRequest({
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': 16,
            'wsgi.input': wsgi_input,
        })
        post = request.POST

        self.assertEqual(post, {'test': '👍'})

