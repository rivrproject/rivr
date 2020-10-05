from typing import Optional, Dict
import time
from random import random
import hashlib

from rivr.middleware import Middleware
from rivr.request import Request
from rivr.response import Response


class BaseSession(object):
    def __init__(self, session_key: Optional[str] = None):
        self.modified = False
        self.session_key = session_key
        self.data: Dict[str, str] = {}

        if self.session_key:
            self.get_session()

    def get_session(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __getitem__(self, key: str) -> str:
        return self.data[key]

    def __setitem__(self, key: str, value: str):
        self.modified = True
        self.data[key] = value

    def __delitem__(self, key: str):
        self.modified = True
        del self.data[key]

    def clear(self):
        self.modified = True
        self.data = {}

    def generate_key(self):
        self.modified = True
        hsh = hashlib.sha1((str(time.time()) + str(random())).encode('utf-8'))
        self.session_key = hsh.hexdigest()


class MemorySession(BaseSession):
    def __init__(self, store, *args, **kwargs):
        self.store = store
        super(MemorySession, self).__init__(*args, **kwargs)

    def get_session(self):
        if self.session_key in self.store.sessions:
            self.data = self.store.sessions[self.session_key]

    def save(self):
        self.store.sessions[self.session_key] = self.data


class MemorySessionStore(object):
    def __init__(self):
        self.sessions = {}

    def __call__(self, *args, **kwargs):
        return MemorySession(self, *args, **kwargs)


class SessionMiddleware(Middleware):
    cookie_name = 'sessionid'
    cookie_secure = False
    cookie_path = '/'
    cookie_domain = None

    session_store = None

    def process_request(self, request: Request) -> Optional[Response]:
        if self.session_store is None:
            raise Exception(
                "SessionMiddleware is improperly configured."
                "Session store is not defined"
            )

        session_key = request.COOKIES.get(self.cookie_name, None)
        request.session = self.session_store(session_key)

    def process_response(self, request: Request, response: Response) -> Response:
        session = getattr(request, 'session')
        if session and session.modified:
            # Save the session data and refresh the client cookie.
            session.save()

            if not session.session_key:
                session.generate_key()

            response.set_cookie(
                self.cookie_name,
                session.session_key,
                path=self.cookie_path,
                domain=self.cookie_domain,
                secure=self.cookie_secure,
            )

        return response
