import datetime
import unittest

from rivr.http import (
    Response,
    ResponseNoContent,
    ResponseNotAllowed,
    ResponseNotFound,
    ResponseNotModified,
    ResponsePermanentRedirect,
    ResponseRedirect,
)


class ResponseTest(unittest.TestCase):
    def test_status_code(self) -> None:
        "Status code should be successful by default"

        assert Response().status_code == 200

    def test_custom_status_code(self) -> None:
        response = Response(status=302)
        assert response.status_code == 302

    def test_content_type(self) -> None:
        "Content type header should be set"

        response = Response(content_type='application/json')
        assert response.content_type == 'application/json'
        assert response.headers['Content-Type'] == 'application/json'

    def test_delete_cookie(self) -> None:
        response = Response()
        response.delete_cookie('test_cookie')
        assert response.cookies['test_cookie']['path'] == '/'
        assert response.cookies['test_cookie']['domain'] == ''
        assert (
            response.cookies['test_cookie']['expires']
            == 'Thu, 01-Jan-1970 00:00:00 GMT'
        )

    def test_set_cookie(self) -> None:
        expires = datetime.datetime(2013, 12, 30)

        response = Response()
        response.set_cookie(
            'test_cookie',
            'testing',
            domain='rivr.com',
            max_age=3600,
            expires=expires,
            path='/cookie/',
            secure=True,
        )
        assert response.cookies['test_cookie'].value == 'testing'
        assert response.cookies['test_cookie']['path'] == '/cookie/'
        assert response.cookies['test_cookie']['domain'] == 'rivr.com'
        assert response.cookies['test_cookie']['secure']
        assert response.cookies['test_cookie']['max-age'] == 3600
        assert response.cookies['test_cookie']['expires'] == 'Mon, 30 Dec 2013 00:00:00'
        assert (
            str(response.cookies['test_cookie'])
            == 'Set-Cookie: test_cookie=testing; Domain=rivr.com; expires=Mon, 30 Dec 2013 00:00:00; Max-Age=3600; Path=/cookie/; Secure'
        )

    def test_header_items(self) -> None:
        response = Response()
        response.delete_cookie('test_cookie')
        response.headers['Location'] = '/'

        assert sorted(response.headers_items()) == sorted(
            [
                ('Content-Type', 'text/html; charset=utf8'),
                ('Location', '/'),
                (
                    'Set-Cookie',
                    ' test_cookie=""; expires=Thu, 01-Jan-1970 00:00:00 GMT; Max-Age=0; Path=/',
                ),
            ]
        )

    def test_to_string(self) -> None:
        response = Response('Hello World')
        assert str(response) == 'Content-Type: text/html; charset=utf8\n\nHello World'

    def test_to_string_bytes_content(self) -> None:
        response = Response(b'Hello World')
        assert str(response) == 'Content-Type: text/html; charset=utf8\n\nHello World'


class ResponseNoContentTest(unittest.TestCase):
    def test_status_code(self) -> None:
        response = ResponseNoContent()
        assert response.status_code == 204


class ResponseRedirectTest(unittest.TestCase):
    def test_redirect(self) -> None:
        response = ResponseRedirect('/redirect/')
        assert response.status_code == 302

    def test_sets_location_header(self) -> None:
        response = ResponseRedirect('/redirect/')
        assert response.headers['Location'] == '/redirect/'

    def test_url_property(self) -> None:
        response = ResponseRedirect('/redirect/')
        assert response.url == '/redirect/'


class ResponsePermanentRedirectTest(unittest.TestCase):
    def test_redirect(self) -> None:
        response = ResponsePermanentRedirect('/redirect/')
        assert response.status_code == 301
        assert response.headers['Location'] == '/redirect/'


class ResponseNotFoundTest(unittest.TestCase):
    def test_status_code(self) -> None:
        response = ResponseNotFound()
        assert response.status_code == 404


class ResponseNotModifiedTest(unittest.TestCase):
    def test_status_code(self) -> None:
        response = ResponseNotModified()
        assert response.status_code == 304


class ResponseNotAllowedTest(unittest.TestCase):
    def test_status_code(self) -> None:
        response = ResponseNotAllowed(['GET'])
        assert response.status_code == 405

    def test_permitted_methods(self) -> None:
        response = ResponseNotAllowed(['GET', 'HEAD', 'OPTIONS'])
        assert response.headers['Allow'] == 'GET, HEAD, OPTIONS'
