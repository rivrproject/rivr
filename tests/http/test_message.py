from wsgiref.headers import Headers

from rivr.http.message import HTTPMessage


def test_headers() -> None:
    headers = Headers()
    headers['Content-Type'] = 'text/plain'
    message = HTTPMessage(headers)
    assert message.headers['Content-Type'] == 'text/plain'


def test_headers_with_dict() -> None:
    message = HTTPMessage(
        {
            'Content-Type': 'text/plain',
        }
    )
    assert message.headers['Content-Type'] == 'text/plain'


def test_content_type_getter() -> None:
    message = HTTPMessage(
        {
            'Content-Type': 'text/plain',
        }
    )

    assert message.content_type == 'text/plain'


def test_content_type_setter() -> None:
    message = HTTPMessage()
    message.content_type = 'text/plain'

    assert message.headers['Content-Type'] == 'text/plain'


def test_content_length_getter() -> None:
    message = HTTPMessage({'Content-Length': '1024'})

    assert message.content_length == 1024


def test_content_length_setter() -> None:
    message = HTTPMessage()
    message.content_length = 1024

    assert message.headers['Content-Length'] == '1024'
