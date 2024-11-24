import datetime
from io import BytesIO

import pytest

from rivr.http.request import Query, Request


def test_query_parse() -> None:
    query = Query('message=Hello+World')

    assert query['message'] == 'Hello World'


def test_query_from_dict() -> None:
    query = Query(
        {
            'message': 'Hello World',
        }
    )

    assert query['message'] == 'Hello World'


def test_query_contains() -> None:
    query = Query('message=Hello+World')

    assert 'message' in query
    assert 'unknown' not in query


def test_query_str() -> None:
    query = Query('message=Hello+World')

    assert str(query) == 'message=Hello+World'


def test_init_headers_dict() -> None:
    request = Request(headers={'Content-Type': 'text/plain'})

    assert request.headers['Content-Type'] == 'text/plain'


def test_init_query() -> None:
    request = Request(query={'message': 'Hello World'})

    assert request.query['message'] == 'Hello World'


def test_init_body_bytes() -> None:
    request = Request(body=b'Hello World')

    assert isinstance(request.body, BytesIO)
    assert request.body.read() == b'Hello World'


def test_init_body_io() -> None:
    request = Request(body=BytesIO(b'Hello World'))

    assert isinstance(request.body, BytesIO)
    assert request.body.read() == b'Hello World'


def test_init_body_empty() -> None:
    request = Request()

    assert isinstance(request.body, BytesIO)
    assert request.body.read() == b''


def test_text() -> None:
    request = Request(body=BytesIO(b'Hello World'))

    assert request.text() == 'Hello World'


def test_text_with_text_content_type_charset() -> None:
    request = Request(
        headers={'content-type': 'text/plain; charset=gb2312'},
        body=BytesIO('还'.encode('gb2312')),
    )

    assert request.text() == '还'


def test_text_with_content_length_too_big() -> None:
    request = Request(
        headers={'content-length': str(1000001)}, body=BytesIO(b'Hello World')
    )

    with pytest.raises(IOError):
        request.text()

    # verify no IO bytes had been read
    assert request.body.read() == b'Hello World'


def test_text_with_chunked_transfer_too_big() -> None:
    request = Request(body=BytesIO(b'.' * 1000002))

    with pytest.raises(IOError):
        request.text()

    # verify only read up until limit + 1
    assert request.body.read() == b'.'


def test_text_with_content_length_and_chunked_transfer() -> None:
    request = Request(
        headers={
            'content-length': str(1000001),
            'transfer-encoding': 'chunked',
        },
        body=BytesIO(b'.' * 5),
    )

    assert request.text() == '.....'


def test_cookies() -> None:
    request = Request(headers={'Cookie': 'name=Kyle; username=kylef'})

    assert request.cookies['name'].value == 'Kyle'
    assert request.cookies['username'].value == 'kylef'


def test_multiple_cookies() -> None:
    request = Request()
    request.headers.add_header('Cookie', 'name=Kyle')
    request.headers.add_header('Cookie', 'username=kylef')

    assert request.cookies['name'].value == 'Kyle'
    assert request.cookies['username'].value == 'kylef'


def test_no_cookies() -> None:
    request = Request()

    assert len(request.cookies) == 0


def test_authorization() -> None:
    request = Request(headers={})
    assert request.authorization is None

    request = Request(headers={'authorization': 'scheme token'})
    assert request.authorization == ('scheme', 'token')

    # auth-params are currently encoded within token field
    request = Request(headers={'authorization': 'Digest username="test"'})
    assert request.authorization == ('Digest', 'username="test"')


def test_if_match() -> None:
    request = Request(headers={})
    assert request.if_match is None

    request = Request(headers={'If-Match': '"tag1", "tag2"'})
    assert request.if_match == ['"tag1"', '"tag2"']


def test_if_none_match() -> None:
    request = Request(headers={})
    assert request.if_none_match is None

    request = Request(headers={'If-None-Match': '"tag1", "tag2"'})
    assert request.if_none_match == ['"tag1"', '"tag2"']


def test_if_modified_since() -> None:
    request = Request(headers={})
    assert request.if_modified_since is None

    request = Request(headers={'If-Modified-Since': 'invalid'})
    assert request.if_modified_since is None

    request = Request(
        headers={
            'If-Modified-Since': 'Sat, 29 Oct 1994 19:43:31 GMT',
        }
    )
    assert request.if_modified_since == datetime.datetime(
        1994, 10, 29, 19, 43, 31, tzinfo=datetime.timezone.utc
    )


def test_if_unmodified_since() -> None:
    request = Request(headers={})
    assert request.if_unmodified_since is None

    request = Request(headers={'If-Unmodified-Since': 'invalid'})
    assert request.if_unmodified_since is None

    request = Request(
        headers={
            'If-Unmodified-Since': 'Sat, 29 Oct 1994 19:43:31 GMT',
        }
    )
    assert request.if_unmodified_since == datetime.datetime(
        1994, 10, 29, 19, 43, 31, tzinfo=datetime.timezone.utc
    )
