from wsgiref.headers import Headers

from rivr.http.message import HTTPMessage


def test_headers():
    headers = Headers()
    headers['Content-Type'] = 'text/plain'
    message = HTTPMessage(headers)
    assert message.headers['Content-Type'] == 'text/plain'


def test_headers_with_dict():
    message = HTTPMessage(
        {
            'Content-Type': 'text/plain',
        }
    )
    assert message.headers['Content-Type'] == 'text/plain'


def test_content_type_getter():
    message = HTTPMessage(
        {
            'Content-Type': 'text/plain',
        }
    )

    assert message.content_type == 'text/plain'


def test_content_type_setter():
    message = HTTPMessage()
    message.content_type = 'text/plain'

    assert message.headers['Content-Type'] == 'text/plain'


def test_content_length_getter():
    message = HTTPMessage({'Content-Length': '1024'})

    assert message.content_length == 1024


def test_content_length_setter():
    message = HTTPMessage()
    message.content_length = 1024

    assert message.headers['Content-Length'] == '1024'
