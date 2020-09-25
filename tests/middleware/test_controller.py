import unittest

from rivr.response import Response
from rivr.middleware import MiddlewareController, Middleware


class TestMiddleware(Middleware):
    def __init__(self):
        self.processed_request = 0
        self.processed_response = 0
        self.processed_exception = 0
        self.response = None

    def process_request(self, request):
        self.processed_request += 1
        return self.response

    def process_response(self, request, response):
        self.processed_response += 1
        return self.response or response

    def process_exception(self, request, exception):
        self.processed_exception += 1
        return self.response


TestMiddleware.__test__ = False


class MiddlewareControllerTests(unittest.TestCase):
    def setUp(self):
        super(MiddlewareControllerTests, self).setUp()
        self.middleware = TestMiddleware()
        self.controller = MiddlewareController(self.middleware)

    def test_processes_request(self):
        self.middleware.response = Response()
        response = self.controller.process_request(None)
        self.assertEqual(self.middleware.processed_request, 1)
        self.assertEqual(response, self.middleware.response)

    def test_processes_response(self):
        self.controller.process_response(None, None)
        self.assertEqual(self.middleware.processed_response, 1)

    def test_processes_exception(self):
        self.middleware.response = Response()
        response = self.controller.process_exception(None, None)
        self.assertEqual(self.middleware.processed_exception, 1)
        self.assertEqual(response, self.middleware.response)

