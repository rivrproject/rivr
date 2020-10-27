from http.cookies import CookieError, SimpleCookie
from io import BytesIO
from typing import IO, Dict, List, Optional, Union
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
        """
        >>> query = Query({'category': 'fruits'})
        >>> str(query)
        'category=fruits'
        """

        return urlencode(self._query)

    def __contains__(self, name: str) -> bool:
        """
        >>> query = Query('category=fruits')
        >>> 'category' in query
        True
        """

        return self[name] is not None

    def __getitem__(self, name: str) -> Optional[str]:
        """
        >>> query = Query('category=fruits')
        >>> query['category']
        'fruits'
        """

        for (key, value) in self._query:
            if key == name:
                return value

        return None

    def __len__(self) -> int:
        """
        >>> query = Query('category=fruits&limit=10')
        >>> len(query)
        2
        """

        return len(self._query)


class Request(HTTPMessage):
    """
    A request is an object which represents a HTTP request. You wouldn't
    normally create a request yourself but instead be passed a request. Each
    view gets passed the clients request.
    """

    host = 'localhost'

    def __init__(
        self,
        path: str = '/',
        method: str = 'GET',
        query: Optional[Union[Dict[str, str], Query]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ):
        self.path = path
        self.method = method

        if query:
            if isinstance(query, Query):
                self.query = query
            else:
                self.query = Query(query)
        else:
            self.query = Query()

        if body:
            if isinstance(body, bytes):
                self.body: IO[bytes] = BytesIO(body)
            else:
                self.body = body
        else:
            self.body = BytesIO()

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
