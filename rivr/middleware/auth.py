from base64 import b64decode
from typing import Optional, Union

from rivr.http import Request, Response
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
        user = self.authorize(request)
        setattr(request, 'user', user)

        if not user.is_authenticated() and self.needs_auth:
            return ResponseAuthorizationRequired()

        return None

    def authorize(self, request: Request) -> Union[AnnonymousUser, User]:
        authorization = request.authorization
        if not authorization:
            return AnnonymousUser()

        scheme, token = authorization
        if scheme.casefold() == 'basic':
            return self.authorize_basic_token(request, token)
        elif scheme.casefold() == 'bearer':
            return self.authorize_bearer(request, token)

        return AnnonymousUser()

    def authorize_basic_token(
        self, request: Request, token: str
    ) -> Union[AnnonymousUser, User]:
        try:
            userid, password = b64decode(token).decode('utf-8').split(':')
        except ValueError:
            return AnnonymousUser()

        return self.authorize_basic(request, userid, password)

    def authorize_basic(
        self, request: Request, userid: str, password: str
    ) -> Union[AnnonymousUser, User]:
        if self.check_password(userid, password):
            return User(userid)

        return AnnonymousUser()

    def check_password(self, userid: str, password: str) -> bool:
        return False

    def authorize_bearer(
        self, request: Request, token: str
    ) -> Union[AnnonymousUser, User]:
        return AnnonymousUser()
