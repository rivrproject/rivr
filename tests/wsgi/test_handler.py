import unittest
from io import BytesIO
from typing import List, Tuple

from rivr.http import Http404, Request, Response
from rivr.wsgi import WSGIHandler


class WSGIHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        super(WSGIHandlerTests, self).setUp()

        self.environ = {
            'REQUEST_METHOD': 'PATCH',
            'PATH_INFO': '/path/',
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': 443,
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(),
        }

    def hello_view(self, request: Request) -> Response:
        return Response('Hello World')

    def start_response(self, status: str, headers: List[Tuple[str, str]]) -> None:
        self.status = status
        self.headers = headers

    def test_sets_status(self) -> None:
        handler = WSGIHandler(self.hello_view)
        handler(self.environ, self.start_response)
        assert self.status == '200 OK'

    def test_sets_headers(self) -> None:
        handler = WSGIHandler(self.hello_view)
        handler(self.environ, self.start_response)
        assert self.headers == [('Content-Type', 'text/html; charset=utf8')]

    def test_returns_content(self) -> None:
        handler = WSGIHandler(self.hello_view)
        content = handler(self.environ, self.start_response)
        assert content == [b'Hello World']

    def test_catches_http_404(self) -> None:
        def view(request: Request) -> Response:
            raise Http404('Not found.')

        handler = WSGIHandler(view)
        handler(self.environ, self.start_response)
        assert self.status == '404 NOT FOUND'

    def test_catches_exceptions(self) -> None:
        def view(request: Request) -> Response:
            raise Exception('Not found.')

        handler = WSGIHandler(view)
        handler(self.environ, self.start_response)
        assert self.status == '500 INTERNAL SERVER ERROR'

    def test_handles_view_not_returning_response(self) -> None:
        def view(request: Request) -> None:
            pass

        handler = WSGIHandler(view)  # type: ignore
        handler(self.environ, self.start_response)
        assert self.status == '500 INTERNAL SERVER ERROR'
