from typing import Dict, Optional
from http.cookies import SimpleCookie, CookieError

__all__ = ['Request']


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


class Request(object):
    """
    A request is an object which represents a HTTP request. You wouldn't
    normally create a request yourself but instead be passed a request. Each
    view gets passed the clients request.
    """

    def __init__(
        self,
        path: str = '/',
        method: str = 'GET',
        get: Optional[Dict[str, str]] = None,
        attributes=None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.path = path
        self.method = method
        self.GET = get or {}
        self.attributes = attributes or {}
        self.headers = headers or {}
        self.META: Dict[str, str] = {}

    @property
    def cookies(self):
        return parse_cookie(self.headers.get('COOKIE', ''))

    COOKIES = cookies  # legacy
