from typing import Optional
from base64 import b64decode

from rivr.request import Request
from rivr.response import Response
from rivr.middleware.base import Middleware


class ResponseAuthorizationRequired(Response):
    status_code = 401

    def __init__(self, *args, **kwargs):
        super(ResponseAuthorizationRequired, self).__init__(*args, **kwargs)
        self.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'


class User(object):
    def __init__(self, username: str = ''):
        self.username = username

    def is_anonymous(self) -> bool:
        return False

    def is_authenticated(self) -> bool:
        return True


class AnnonymousUser(object):
    username = ''

    def is_anonymous(self) -> bool:
        return True

    def is_authenticated(self) -> bool:
        return False


class AuthMiddleware(Middleware):
    needs_auth = True

    def process_request(self, request: Request) -> Optional[Response]:
        user = self.check_login(request)
        setattr(request, 'user', user)

        if not user.is_authenticated() and self.needs_auth:
            return ResponseAuthorizationRequired()

        return None

    def check_login(self, request: Request):
        authorization = request.META.get('HTTP_AUTHORIZATION', None)

        if not authorization:
            return AnnonymousUser()

        try:
            method, key = authorization.split()
        except ValueError:
            return AnnonymousUser()

        if method != 'Basic':
            return AnnonymousUser()

        try:
            username, password = b64decode(key).decode('utf-8').split(':')
        except ValueError:
            return AnnonymousUser()

        if self.check_password(username, password):
            return User(username)

        return AnnonymousUser()

    def check_password(self, username: str, password: str) -> bool:
        return False
