import json
from datetime import datetime
from email.utils import parsedate_to_datetime
from http.cookies import CookieError, SimpleCookie
from io import BytesIO
from typing import IO, Any, Dict, List, Optional, Tuple, Union
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
        except (ValueError, TypeError):
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
        except (ValueError, TypeError):
            # A recipient MUST ignore the If-Unmodified-Since header field
            # if the received field value is not a valid HTTP-date
            # (including when the field value appears to be a list of dates).
            return None

    # Body

    def text(self, max_bytes: Optional[int] = 1000000) -> str:
        """
        Read the request body into a string, up until a default limit of 1mb.

        By default utf-8 will be used, or the charset of the content type
        for text types.

        text is a blocking method, and can block if a client slowly
        streams a request body.
        """

        if max_bytes:
            transfer_encoding = self.headers['transfer-encoding']
            is_chunked = False
            if transfer_encoding:
                supported_encodings = set(
                    map(lambda te: te.strip(), transfer_encoding.split(','))
                )
                is_chunked = 'chunked' in supported_encodings

            if not is_chunked:
                content_length = self.content_length
                if content_length and content_length > max_bytes:
                    raise IOError('Message body is above max bytes limit')

        encoding = 'utf-8'

        content_type = self.content_type
        if content_type and content_type.type == 'text' and 'charset' in content_type:
            encoding = content_type['charset']

        buffer = self.body.read(max_bytes or -1)

        if len(self.body.read(1)) > 0:
            raise IOError('Message body is above max bytes limit')

        return buffer.decode(encoding)

    # Deprecated
    @property
    def GET(self) -> Dict[str, str]:
        return dict((k, v) for k, v in self.query._query)

    @property
    def attributes(self) -> Any:
        """
        A request body, deserialized as a dictionary.

        This will automatically deserialize form or JSON encoded request
        bodies.
        """

        if not hasattr(self, '_attributes'):
            content_type = self.content_type

            if content_type:
                text = self.text(max_bytes=None)

                if (
                    content_type.type == 'application'
                    and content_type.subtype == 'json'
                ):
                    self._attributes = json.loads(text)
                elif (
                    content_type.type == 'application'
                    and content_type.subtype == 'x-www-form-urlencoded'
                ):
                    data = parse_qsl(text, True)
                    self._attributes = dict((k, v) for k, v in data)
            else:
                self._attributes = {}

        return self._attributes

    POST = attributes  # Deprecated
