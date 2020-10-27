import hashlib
import time
from random import random
from typing import Any, Dict, Optional

from rivr.http import Request, Response
from rivr.middleware import Middleware


class Session:  # FIXME: once dropped py 3.7 move to Protocol
    def __contains__(self, key: str) -> bool:
        raise NotImplementedError

    def __getitem__(self, key: str) -> str:
        raise NotImplementedError

    def __setitem__(self, key: str, value: str) -> None:
        raise NotImplementedError

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError


class SessionStore:  # FIXME: once dropped py 3.7 move to Protocol
    def __call__(self, *args, **kwargs) -> Session:
        raise NotImplementedError


class BaseSession(object):
    def __init__(self, session_key: Optional[str] = None):
        self.modified = False
        self.session_key = session_key
        self.data: Dict[str, str] = {}

        if self.session_key:
            self.get_session()

    def get_session(self):
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __getitem__(self, key: str) -> str:
        return self.data[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.modified = True
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        self.modified = True
        del self.data[key]

    def clear(self) -> None:
        self.modified = True
        self.data = {}

    def generate_key(self) -> None:
        self.modified = True
        hsh = hashlib.sha1((str(time.time()) + str(random())).encode('utf-8'))
        self.session_key = hsh.hexdigest()


class MemorySession(BaseSession, Session):
    def __init__(self, store, *args, **kwargs):
        self.store: Optional[Any] = store
        super(MemorySession, self).__init__(*args, **kwargs)

    def get_session(self):
        if self.session_key in self.store.sessions:
            self.data = self.store.sessions[self.session_key]

    def save(self):
        self.store.sessions[self.session_key] = self.data


class MemorySessionStore(SessionStore):
    def __init__(self):
        self.sessions = {}

    def __call__(self, *args, **kwargs) -> Session:
        return MemorySession(self, *args, **kwargs)


class SessionMiddleware(Middleware):
    cookie_name = 'sessionid'
    cookie_secure = False
    cookie_path = '/'
    cookie_domain = None

    session_store: Optional[SessionStore] = None

    def process_request(self, request: Request) -> Optional[Response]:
        if self.session_store is None:
            raise Exception(
                "SessionMiddleware is improperly configured."
                "Session store is not defined"
            )

        session_key = request.cookies.get(self.cookie_name)
        if session_key:
            session = self.session_store(session_key.value)
        else:
            session = self.session_store(None)

        setattr(request, 'session', session)

        return None

    def process_response(self, request: Request, response: Response) -> Response:
        session = getattr(request, 'session')
        if session and session.modified:
            # Save the session data and refresh the client cookie.
            if not session.session_key:
                session.generate_key()

            session.save()

            response.set_cookie(
                self.cookie_name,
                session.session_key,
                path=self.cookie_path,
                domain=self.cookie_domain,
                secure=self.cookie_secure,
            )

        return response
