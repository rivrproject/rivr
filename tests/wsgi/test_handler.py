import unittest

from rivr.wsgi import WSGIHandler
from rivr.http import Response, Http404


class WSGIHandlerTests(unittest.TestCase):
    def hello_view(self, request):
        return Response('Hello World')

    def start_response(self, status, headers):
        self.status = status
        self.headers = headers

    def test_sets_status(self):
        handler = WSGIHandler(self.hello_view)
        handler({}, self.start_response)
        self.assertEqual(self.status, '200 OK')

    def test_sets_headers(self):
        handler = WSGIHandler(self.hello_view)
        handler({}, self.start_response)
        self.assertEqual(self.headers,
                         [('Content-Type', 'text/html; charset=utf8')])

    def test_returns_content(self):
        handler = WSGIHandler(self.hello_view)
        content = handler({}, self.start_response)
        self.assertEqual(content, ['Hello World'])

    def test_catches_http_404(self):
        def view(request):
            raise Http404('Not found.')

        handler = WSGIHandler(view)
        handler({}, self.start_response)
        self.assertEqual(self.status, '404 NOT FOUND')

    def test_catches_exceptions(self):
        def view(request):
            raise Exception('Not found.')

        handler = WSGIHandler(view)
        handler({}, self.start_response)
        self.assertEqual(self.status, '500 INTERNAL SERVER ERROR')

    def test_handles_view_not_returning_response(self):
        def view(request):
            pass

        handler = WSGIHandler(view)
        handler({}, self.start_response)
        self.assertEqual(self.status, '500 INTERNAL SERVER ERROR')
