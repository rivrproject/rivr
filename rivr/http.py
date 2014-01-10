try:
    from http.cookies import SimpleCookie, CookieError
except ImportError:
    from Cookie import SimpleCookie, CookieError

import datetime

from rivr.utils import JSON_CONTENT_TYPES, JSONEncoder


def parse_cookie(cookie):
    if cookie == '':
        return {}

    try:
        c = SimpleCookie()
        c.load(cookie)
    except CookieError:
        return {}

    cookiedict = {}
    for key in c.keys():
        cookiedict[key] = c.get(key).value

    return cookiedict


class Http404(Exception):
    pass


class Request(object):
    """
    A request is an object which represents a HTTP request. You wouldn't
    normally create a request yourself but instead be passed a request. Each
    view gets passed the clients request.
    """

    def __init__(self, path='/', method='GET', get=None, post=None,
                 headers=None):
        self.path = path
        self.method = method
        self.GET = get or {}
        self.POST = post or {}
        self.headers = headers or {}

    @property
    def cookies(self):
        return parse_cookie(self.headers.get('COOKIE', ''))


class Response(object):
    """
    Response is an object for describing a HTTP response. Every view is
    responsible for either returning a response or raising an exception.
    """

    status_code = 200
    """The HTTP status code for the response."""

    def __init__(self, content='', status=None,
                 content_type='text/html; charset=utf8'):
        self.content = content

        if status:
            self.status_code = status

        self.headers = {'Content-Type': content_type}
        self.cookies = SimpleCookie()

    def __str__(self):
        headers = ['%s: %s' % (key, value) for key, value in self.headers.items()]
        return '\n'.join(headers) + '\n\n' + self.content

    def set_cookie(self, key, value='', max_age=None, expires=None, path='/',
                   domain=None, secure=False):
        """
        Sets a cookie. The parameters are the same as in the Cookie.Morsel
        object in the Python standard library.
        """

        self.cookies[key] = value

        if max_age is not None:
            self.cookies[key]['max-age'] = max_age

        if expires is not None:
            if isinstance(expires, datetime.datetime):
                expires = expires.strftime('%a, %d %b %Y %H:%M:%S')

            self.cookies[key]['expires'] = expires

        if path is not None:
            self.cookies[key]['path'] = path

        if domain is not None:
            self.cookies[key]['domain'] = domain

        if secure:
            self.cookies[key]['secure'] = True

    def delete_cookie(self, key, path='/', domain=None):
        """
        Deletes the cookie with the given key. Fails silently if the key
        doesn't exist
        """

        self.set_cookie(key, max_age=0, path=path, domain=domain,
                        expires='Thu, 01-Jan-1970 00:00:00 GMT')

    def headers_items(self):
        headers = [(k, v) for k, v in self.headers.items()]

        for cookie in self.cookies.values():
            headers.append(('Set-Cookie', str(cookie.output(header=''))))

        return headers


class ResponseNoContent(Response):
    """A response that uses the 204 status code to indicate no content."""
    status_code = 204


class ResponseRedirect(Response):
    """
    Acts just like a ResponseRedirect, but uses a 302 status code.
    It takes a URL to redirect the user to.
    """

    status_code = 302

    def __init__(self, redirect_to):
        super(ResponseRedirect, self).__init__()
        self.headers['Location'] = str(redirect_to)

    @property
    def url(self):
        """
        A property that returns the URL for the redirect.
        """
        return self.headers['Location']


class ResponsePermanentRedirect(ResponseRedirect):
    """Acts just like a ResponseRedirect, but uses a 302 status code."""
    status_code = 301


class ResponseNotFound(Response):
    """Acts just like a Response, but uses a 404 status code."""
    status_code = 404


class ResponseNotModified(Response):
    """Acts just like a Response, but uses a 304 status code."""
    status_code = 304


class ResponseNotAllowed(Response):
    """
    A response that uses the 405 status code and takes a list of
    permitted HTTP methods.
    """
    status_code = 405

    def __init__(self, permitted_methods):
        super(ResponseNotAllowed, self).__init__()
        self.headers['Allow'] = ', '.join(permitted_methods)


class RESTResponse(Response):
    def __init__(self, request, payload, status=None):
        content = JSONEncoder().encode(payload)
        content_type = JSON_CONTENT_TYPES[0]

        super(RESTResponse, self).__init__(content, status, content_type)

