from rivr.http import Request
from wsgiref.headers import Headers


def test_init_headers_dict():
    request = Request(headers={'Content-Type': 'text/plain'})

    assert request.headers['Content-Type'] == 'text/plain'
