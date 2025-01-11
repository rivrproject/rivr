import unittest

import rivr
from rivr.test import Client


def hello_world(request):
    return rivr.Response('Hello World')


class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(hello_world)

    def test200(self):
        assert self.client.get('/').status_code is 200

    def testResponseContent(self):
        self.assertEqual(self.client.get('/').content, 'Hello World')


if __name__ == '__main__':
    unittest.main()
