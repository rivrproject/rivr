import unittest
import datetime

from rivr.response import (Response, ResponseNoContent, ResponseRedirect,
                          ResponseNotAllowed, ResponsePermanentRedirect,
                          ResponseNotFound, ResponseNotModified)


class ResponseTest(unittest.TestCase):
    def test_status_code(self):
        "Status code should be successful by default"

        self.assertEqual(Response().status_code, 200)

    def test_custom_status_code(self):
        response = Response(status=302)
        self.assertEqual(response.status_code, 302)

    def test_content_type(self):
        "Content type header should be set"

        response = Response(content_type='application/json')
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_delete_cookie(self):
        response = Response()
        response.delete_cookie('test_cookie')
        self.assertEqual(response.cookies['test_cookie']['path'], '/')
        self.assertEqual(response.cookies['test_cookie']['domain'], '')
        self.assertEqual(response.cookies['test_cookie']['expires'],
                         'Thu, 01-Jan-1970 00:00:00 GMT')

    def test_set_cookie(self):
        expires = datetime.datetime(2013, 12, 30)

        response = Response()
        response.set_cookie('test_cookie', 'testing', domain='rivr.com',
                            max_age=3600, expires=expires, path='/cookie/',
                            secure=True)
        self.assertEqual(response.cookies['test_cookie'].value, 'testing')
        self.assertEqual(response.cookies['test_cookie']['path'], '/cookie/')
        self.assertEqual(response.cookies['test_cookie']['domain'], 'rivr.com')
        self.assertEqual(response.cookies['test_cookie']['secure'], True)
        self.assertEqual(response.cookies['test_cookie']['max-age'], 3600)
        self.assertEqual(response.cookies['test_cookie']['expires'],
                         'Mon, 30 Dec 2013 00:00:00')

        self.assertEqual(str(response.cookies['test_cookie']),
                         'Set-Cookie: test_cookie=testing; Domain=rivr.com; expires=Mon, 30 Dec 2013 00:00:00; Max-Age=3600; Path=/cookie/; secure')

    def test_header_items(self):
        response = Response()
        response.delete_cookie('test_cookie')
        response.headers['Location'] = '/'

        self.assertEqual(response.headers_items().sort(), [
            ('Content-Type', 'text/html; charset=utf8'),
            ('Location', '/'),
            ('Set-Cookie', ' test_cookie=; expires=Thu, 01-Jan-1970 00:00:00 GMT; Max-Age=0; Path=/')
        ].sort())

    def test_to_string(self):
        response = Response('Hello World')
        self.assertEqual(str(response), 'Content-Type: text/html; charset=utf8\n\nHello World')


class ResponseNoContentTest(unittest.TestCase):
    def test_status_code(self):
        response = ResponseNoContent()
        self.assertEqual(response.status_code, 204)


class ResponseRedirectTest(unittest.TestCase):
    def test_redirect(self):
        response = ResponseRedirect('/redirect/')
        self.assertEqual(response.status_code, 302)

    def test_sets_location_header(self):
        response = ResponseRedirect('/redirect/')
        self.assertEqual(response.headers['Location'], '/redirect/')

    def test_url_property(self):
        response = ResponseRedirect('/redirect/')
        self.assertEqual(response.url, '/redirect/')


class ResponsePermanentRedirectTest(unittest.TestCase):
    def test_redirect(self):
        response = ResponsePermanentRedirect('/redirect/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['Location'], '/redirect/')


class ResponseNotFoundTest(unittest.TestCase):
    def test_status_code(self):
        response = ResponseNotFound()
        self.assertEqual(response.status_code, 404)


class ResponseNotModifiedTest(unittest.TestCase):
    def test_status_code(self):
        response = ResponseNotModified()
        self.assertEqual(response.status_code, 304)


class ResponseNotAllowedTest(unittest.TestCase):
    def test_status_code(self):
        response = ResponseNotAllowed(['GET'])
        self.assertEqual(response.status_code, 405)

    def test_permitted_methods(self):
        response = ResponseNotAllowed(['GET', 'HEAD', 'OPTIONS'])
        self.assertEqual(response.headers['Allow'], 'GET, HEAD, OPTIONS')

