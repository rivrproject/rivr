import unittest
from rivr.middleware.debug import DebugMiddleware
from rivr.response import Http404


class DebugMiddlewareTests(unittest.TestCase):
    def test_catches_exception(self):
        def view(request):
            raise Exception('Testing')

        middleware = DebugMiddleware.wrap(view)
        response = middleware(None)

        self.assertEqual(response.status_code, 500)

    def test_errors_when_nothing_is_returned_from_view(self):
        def view(request):
            pass

        middleware = DebugMiddleware.wrap(view)
        response = middleware(None)

        self.assertEqual(response.status_code, 500)

    def test_catches_Http404(self):
        def view(request):
            raise Http404('Page not found')

        middleware = DebugMiddleware.wrap(view)
        response = middleware(None)

        self.assertEqual(response.status_code, 404)
