import unittest

from rivr.http import Http404, Request, Response
from rivr.middleware.debug import DebugMiddleware


class DebugMiddlewareTests(unittest.TestCase):
    def test_catches_exception(self) -> None:
        def view(request: Request) -> Response:
            raise Exception('Testing')

        middleware = DebugMiddleware.wrap(view)
        response = middleware(Request('/', 'GET'))

        assert response.status_code == 500

    def test_errors_when_nothing_is_returned_from_view(self) -> None:
        def view(request: Request) -> None:
            pass

        middleware = DebugMiddleware.wrap(view)  # type: ignore
        response = middleware(Request('/', 'GET'))

        assert response.status_code == 500

    def test_catches_Http404(self) -> None:
        def view(request: Request) -> Response:
            raise Http404('Page not found')

        middleware = DebugMiddleware.wrap(view)
        response = middleware(Request('/', 'GET'))

        assert response.status_code == 404
