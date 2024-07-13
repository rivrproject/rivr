from datetime import datetime
from email.utils import parsedate_to_datetime
from http.cookies import CookieError, SimpleCookie
from io import BytesIO
from typing import IO, Dict, List, Optional, Tuple, Union
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

        for key, value in self._query:
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
    def cookies(self) -> SimpleCookie:
        if not hasattr(self, '_cookies'):
            self._cookies = parse_cookie(self.headers.get_all('Cookie'))

        return self._cookies

    # Header accessors

    @property
    def authorization(self) -> Optional[Tuple[str, str]]:
        authorization = self.headers.get('authorization')
        if not authorization:
            return None

        scheme, _, token = authorization.partition(' ')
        return (scheme, token)

    @property
    def if_match(self) -> Optional[List[str]]:
        if_match = self.headers.get('if-match')
        if not if_match:
            return None

        return [m.strip() for m in if_match.split(',')]

    @property
    def if_none_match(self) -> Optional[List[str]]:
        if_none_match = self.headers.get('if-none-match')
        if not if_none_match:
            return None

        return [m.strip() for m in if_none_match.split(',')]

    @property
    def if_modified_since(self) -> Optional[datetime]:
        value = self.headers.get('if-modified-since')
        if value is None:
            return None

        try:
            return parsedate_to_datetime(value)
        except ValueError:
            # A recipient MUST ignore the If-Modified-Since header field if
            # the received field value is not a valid HTTP-date
            return None

    @property
    def if_unmodified_since(self) -> Optional[datetime]:
        value = self.headers.get('if-unmodified-since')
        if value is None:
            return None

        try:
            return parsedate_to_datetime(value)
        except ValueError:
            # A recipient MUST ignore the If-Unmodified-Since header field
            # if the received field value is not a valid HTTP-date
            # (including when the field value appears to be a list of dates).
            return None

    # Deprecated
    @property
    def GET(self) -> Dict[str, str]:
        return dict((k, v) for k, v in self.query._query)
