import os
import unittest
from pathlib import Path

from rivr.http import Http404
from rivr.test import Client
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
    def setUp(self) -> None:
        super(StaticViewTests, self).setUp()

        fixture_file = Path(__file__).parent / 'fixture' / 'file1.py'
        os.utime(fixture_file, (10000, 1720900063))

        self.root = os.path.dirname(__file__)
        self.view = StaticView.as_view(
            show_indexes=False, document_root=self.root, use_request_path=True
        )
        self.client = Client(self.view)

    def test_show_indexes_disabled_by_default(self) -> None:
        self.assertFalse(StaticView().show_indexes)

    def test_directory_index_404s_when_disabled(self) -> None:
        with self.assertRaises(Http404):
            self.client.get('/')

    def test_directory_index(self) -> None:
        self.view = StaticView.as_view(
            show_indexes=True, document_root=self.root, use_request_path=True
        )
        self.client = Client(self.view)

        def strip(content):
            return content.replace('\n', '').replace(' ', '')

        response = self.client.get('/fixture')
        assert strip(response.content) == strip(FIXTURE_DIRECTORY_INDEX)

    def test_index_file(self) -> None:
        self.view = StaticView.as_view(
            show_indexes=True,
            document_root=self.root,
            use_request_path=True,
            index='file1.py',
        )
        self.client = Client(self.view)
        response = self.client.get('/fixture')
        assert response.status_code == 200
        assert response.content == b"print('Hello World')\n"
        assert response.headers['Content-Type'] == 'text/x-python'
        assert response.headers['Content-Length'] == '21'
        assert response.headers['Last-Modified'] == 'Sat, 13 Jul 2024 19:47:43 GMT'

    def test_file(self) -> None:
        response = self.client.get('/fixture/file1.py')
        assert response.status_code == 200
        assert response.content == b"print('Hello World')\n"
        assert response.headers['Content-Type'] == 'text/x-python'
        assert response.headers['Content-Length'] == '21'
        assert response.headers['Last-Modified'] == 'Sat, 13 Jul 2024 19:47:43 GMT'

    def test_non_existent_file(self) -> None:
        with self.assertRaises(Http404):
            self.client.get('/fixture/not_found.py')

    def test_file_not_modified(self) -> None:
        response = self.client.get(
            '/fixture/file1.py',
            headers={
                'If-Modified-Since': 'Sat, 13 Jul 2024 19:47:43 GMT',
            },
        )
        assert response.status_code == 304

        response = self.client.get(
            '/fixture/file1.py',
            headers={
                'If-Modified-Since': 'Sat, 13 Jul 2024 20:47:43 GMT',
            },
        )
        assert response.status_code == 304

        response = self.client.get(
            '/fixture/file1.py',
            headers={
                'If-Modified-Since': 'Sat, 13 Jul 2024 18:47:43 GMT',
            },
        )
        assert response.status_code == 200
