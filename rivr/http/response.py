import datetime
from http.cookies import SimpleCookie
from typing import Iterable, List, Optional, Tuple, Union

from rivr.http.message import HTTPMessage


class Http404(Exception):
    pass


class Response(HTTPMessage):
    """
    Response is an object for describing a HTTP response. Every view is
    responsible for either returning a response or raising an exception.
    """

    status_code: int = 200
    """The HTTP status code for the response."""

    def __init__(
        self,
        content: Union[str, bytes] = '',
        status: Optional[int] = None,
        content_type: Optional[str] = 'text/html; charset=utf8',
    ):
        super(Response, self).__init__()

        self.content = content

        if status:
            self.status_code = status

        if content_type:
            self.content_type = content_type

        self.cookies: SimpleCookie = SimpleCookie()

    def __str__(self) -> str:
        headers = ['%s: %s' % (key, value) for key, value in self.headers.items()]
        if isinstance(self.content, bytes):
            return '\n'.join(headers) + '\n\n' + self.content.decode('utf-8')

        return '\n'.join(headers) + '\n\n' + self.content

    def set_cookie(
        self,
        key: str,
        value: str = '',
        max_age: Optional[int] = None,
        expires: Union[datetime.datetime, str, None] = None,
        path: str = '/',
        domain: Optional[str] = None,
        secure: bool = False,
    ) -> None:
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

    def delete_cookie(
        self, key: str, path: str = '/', domain: Optional[str] = None
    ) -> None:
        """
        Deletes the cookie with the given key. Fails silently if the key
        doesn't exist
        """

        self.set_cookie(
            key,
            max_age=0,
            path=path,
            domain=domain,
            expires='Thu, 01-Jan-1970 00:00:00 GMT',
        )

    def headers_items(self) -> Iterable[Tuple[str, str]]:
        headers = [(k, v) for k, v in self.headers.items()]

        for cookie in self.cookies.values():
            headers.append(('Set-Cookie', cookie.OutputString()))

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

    def __init__(self, redirect_to: str):
        super(ResponseRedirect, self).__init__()
        self.headers['Location'] = str(redirect_to)

    @property
    def url(self) -> Optional[str]:
        """
        A property that returns the URL for the redirect.
        """
        return self.headers['Location']


class ResponsePermanentRedirect(ResponseRedirect):
    """Acts just like a ResponseRedirect, but uses a 301 status code."""

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

    def __init__(self, permitted_methods: List[str]):
        super(ResponseNotAllowed, self).__init__()
        self.headers['Allow'] = ', '.join(permitted_methods)
