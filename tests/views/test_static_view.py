import os
import unittest
from rivr.response import Http404
from rivr.tests import TestClient
from rivr.views.static import StaticView


FIXTURE_DIRECTORY_INDEX = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Language" content="en-us" />
    <meta name="robots" content="NONE,NOARCHIVE" />
    <title>Index of fixture/</title>
</head>

<body>
    <h1>Index of fixture/</h1>
    <ul>
        <li><a href="../">../</a></li>

        <li><a href="directory1/">directory1/</a></li>
        <li><a href="file1.py">file1.py</a></li>
    </ul>
</body>
"""


class StaticViewTests(unittest.TestCase):
    def setUp(self):
        super(StaticViewTests, self).setUp()

        self.root = os.path.dirname(__file__)
        self.view = StaticView.as_view(show_indexes=False,
                                       document_root=self.root,
                                       use_request_path=True)
        self.client = TestClient(self.view)

    def test_show_indexes_disabled_by_default(self):
        self.assertFalse(StaticView().show_indexes)

    def test_directory_index_404s_when_disabled(self):
        with self.assertRaises(Http404):
            self.client.get('/')

    def test_directory_index(self):
        self.view = StaticView.as_view(show_indexes=True,
                                       document_root=self.root,
                                       use_request_path=True)
        self.client = TestClient(self.view)

        def strip(content):
            return content.replace('\n', '').replace(' ', '')

        response = self.client.get('/fixture')
        self.assertEqual(strip(response.content),
                strip(FIXTURE_DIRECTORY_INDEX))

    def test_file(self):
        response = self.client.get('/fixture/file1.py')
        self.assertEqual(response.content, b"print('Hello World')\n")
        self.assertEqual(response.headers['Content-Type'], 'text/x-python')
        self.assertEqual(response.headers['Content-Length'], '21')
