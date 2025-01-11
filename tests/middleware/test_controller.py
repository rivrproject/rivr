import unittest
from typing import Optional

from rivr.http import Request, Response
from rivr.middleware import Middleware, MiddlewareController


class TestMiddleware(Middleware):
    def __init__(self) -> None:
        self.processed_request = 0
        self.processed_response = 0
        self.processed_exception = 0
        self.response: Optional[Response] = None

    def process_request(self, request: Request) -> Optional[Response]:
        self.processed_request += 1
        return self.response

    def process_response(self, request: Request, response: Response) -> Response:
        self.processed_response += 1
        return self.response or response

    def process_exception(self, request: Request, exception: Exception) -> Response:
        self.processed_exception += 1
        assert self.response
        return self.response


TestMiddleware.__test__ = False  # type: ignore


class MiddlewareControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        super(MiddlewareControllerTests, self).setUp()
        self.middleware = TestMiddleware()
        self.controller = MiddlewareController(self.middleware)

    def test_processes_request(self) -> None:
        self.middleware.response = Response()
        response = self.controller.process_request(Request('/', 'GET'))
        assert self.middleware.processed_request == 1
        assert response == self.middleware.response

    def test_processes_response(self) -> None:
        self.controller.process_response(Request('/', 'GET'), Response())
        assert self.middleware.processed_response == 1

    def test_processes_exception(self) -> None:
        self.middleware.response = Response()
        response = self.controller.process_exception(Request('/', 'GET'), Exception())
        assert self.middleware.processed_exception == 1
        assert response == self.middleware.response
