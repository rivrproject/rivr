from io import BytesIO

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
