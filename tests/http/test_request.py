from rivr.http.request import Query, Request
from wsgiref.headers import Headers


def test_query_parse():
    query = Query('message=Hello+World')

    assert query['message'] == 'Hello World'


def test_query_from_dict():
    query = Query(
        {
            'message': 'Hello World',
        }
    )

    assert query['message'] == 'Hello World'


def test_query_contains():
    query = Query('message=Hello+World')

    assert 'message' in query
    assert 'unknown' not in query


def test_query_str():
    query = Query('message=Hello+World')

    assert str(query) == 'message=Hello+World'


def test_init_headers_dict():
    request = Request(headers={'Content-Type': 'text/plain'})

    assert request.headers['Content-Type'] == 'text/plain'


def test_init_query():
    request = Request(query={'message': 'Hello World'})

    assert request.query['message'] == 'Hello World'


def test_init_get():  # deprecated
    request = Request(get={'message': 'Hello World'})

    assert request.query['message'] == 'Hello World'


def test_get():  # deprecated
    request = Request(query={'message': 'Hello World'})

    assert request.GET['message'] == 'Hello World'


def test_cookies():
    request = Request(headers={'Cookie': 'name=Kyle; username=kylef'})

    assert request.cookies['name'].value == 'Kyle'
    assert request.cookies['username'].value == 'kylef'


def test_multiple_cookies():
    request = Request()
    request.headers.add_header('Cookie', 'name=Kyle')
    request.headers.add_header('Cookie', 'username=kylef')

    assert request.cookies['name'].value == 'Kyle'
    assert request.cookies['username'].value == 'kylef'


def test_no_cookies():
    request = Request()

    assert len(request.cookies) == 0
