try:
    from http.cookies import SimpleCookie, CookieError
except ImportError:
    from Cookie import SimpleCookie, CookieError

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

    def __init__(self, path='/', method='GET', get=None, attributes=None,
                 headers=None):
        self.path = path
        self.method = method
        self.GET = get or {}
        self.attributes = attributes or {}
        self.headers = headers or {}

    @property
    def cookies(self):
        return parse_cookie(self.headers.get('COOKIE', ''))

    COOKIES = cookies  # legacy


