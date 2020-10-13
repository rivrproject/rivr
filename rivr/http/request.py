from typing import Dict, Optional, Union, List, IO
from io import BytesIO
from wsgiref.headers import Headers
from http.cookies import SimpleCookie, CookieError
from urllib.parse import parse_qsl, urlencode

from rivr.http.message import HTTPMessage

__all__ = ['Query', 'Request']


def parse_cookie(values: List[str]) -> SimpleCookie:
    cookies: SimpleCookie = SimpleCookie()

    for value in values:
        try:
            cookies.load(value)
        except CookieError:
            pass

    return cookies


QueryConvertible = Union[str, Dict[str, str]]


class Query:
    def __init__(self, query: Optional[QueryConvertible] = None):
        if query:
            if isinstance(query, str):
                self._query = parse_qsl(query, True)
            elif isinstance(query, dict):
                self._query = list(query.items())
        else:
            self._query = []

    def __str__(self) -> str:
        return urlencode(self._query)

    def __contains__(self, name: str) -> bool:
        return self[name] is not None

    def __getitem__(self, name: str) -> Optional[str]:
        for (key, value) in self._query:
            if key == name:
                return value

        return None


class Request(HTTPMessage):
    """
    A request is an object which represents a HTTP request. You wouldn't
    normally create a request yourself but instead be passed a request. Each
    view gets passed the clients request.
    """

    def __init__(
        self,
        path: str = '/',
        method: str = 'GET',
        query: Optional[Dict[str, str]] = None,
        get: Optional[Dict[str, str]] = None,
        attributes=None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.path = path
        self.method = method
        self.attributes = attributes or {}
        self.META: Dict[str, str] = {}

        if query and get:
            raise ValueError('Cannot set both query and get. Use query')

        self.query = Query(query or get)
        self.body: IO[bytes] = BytesIO()

        super(Request, self).__init__(headers)

    @property
    def cookies(self):
        if not hasattr(self, '_cookies'):
            self._cookies = parse_cookie(self.headers.get_all('Cookie'))

        return self._cookies

    # Deprecated
    @property
    def GET(self) -> Dict[str, str]:
        return dict((k, v) for k, v in self.query._query)
