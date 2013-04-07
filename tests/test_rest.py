import unittest

from rivr.http import Request, Response, RESTResponse
from rivr.views import RESTView

class RESTViewTestCase(unittest.TestCase):
    def test_no_content(self):
        class NoContentView(RESTView):
            def get(self, request):
                pass

        response = NoContentView().dispatch(Request())
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, '')

    def test_response(self):
        response = Response()

        class ResponseView(RESTView):
            def get(self, request):
                return response

        out_response = ResponseView().dispatch(Request())
        self.assertEqual(response, out_response)

    def test_json(self):
        class JSONView(RESTView):
            def get(self, request):
                return {'test':True}

        response = JSONView().dispatch(Request())
        self.assertIsInstance(response, RESTResponse)
        self.assertEqual(response.content, '{"test": true}')

