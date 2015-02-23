import unittest
from rivr.response import Response
from rivr.tests import TestClient


class TestClientTests(unittest.TestCase):
    def setUp(self):
        def view(request):
            return Response('{} {}'.format(request.method, request.path))

        self.client = TestClient(view)

    def test_http(self):
        response = self.client.http('METHOD', '/path/')
        self.assertEqual(response.content, 'METHOD /path/')

    def test_get(self):
        response = self.client.get('/')
        self.assertEqual(response.content, 'GET /')

    def test_put(self):
        response = self.client.put('/')
        self.assertEqual(response.content, 'PUT /')

    def test_post(self):
        response = self.client.post('/')
        self.assertEqual(response.content, 'POST /')

    def test_delete(self):
        response = self.client.delete('/resource')
        self.assertEqual(response.content, 'DELETE /resource')
