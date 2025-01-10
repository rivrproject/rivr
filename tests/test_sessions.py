import unittest

import pytest

from rivr import Request, Response
from rivr.sessions import BaseSession, MemorySessionStore, SessionMiddleware


class SessionMiddlewareTests(unittest.TestCase):
    def setUp(self) -> None:
        super(SessionMiddlewareTests, self).setUp()
        self.middleware = SessionMiddleware()

    def test_default_cookie_name(self) -> None:
        assert self.middleware.cookie_name == 'sessionid'

    def test_default_session_store(self):
        assert self.middleware.session_store is None

    def test_raises_without_session_store(self):
        with pytest.raises(Exception):
            self.middleware.dispatch(None, None)

    def test_persists_new_session_key(self) -> None:
        def view(request: Request) -> Response:
            session = getattr(request, 'session')
            session['key'] = 'value'
            return Response()

        self.middleware.session_store = MemorySessionStore()
        response = self.middleware.dispatch(view, Request())

        assert response.cookies['sessionid'].value is not None


class BaseSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        super(BaseSessionTests, self).setUp()
        self.session = BaseSession()

    def test_unmodified_by_default(self) -> None:
        assert not self.session.modified

    def test_setting_value(self) -> None:
        self.session['key'] = 'value'
        assert self.session['key'] == 'value'
        assert 'key' in self.session

    def test_deleting_value(self) -> None:
        self.session['key'] = 'value'
        del self.session['key']
        assert 'key' not in self.session

    def test_clearing(self) -> None:
        self.session['key'] = 'value'
        self.session.clear()
        assert 'key' not in self.session


class MemorySessionStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        super(MemorySessionStoreTests, self).setUp()
        self.store = MemorySessionStore()
        self.middleware = SessionMiddleware(session_store=self.store)

    def test_persists_session(self) -> None:
        session = self.store('session-key')
        session['key'] = 'value'
        session.save()

        new_session = self.store('session-key')
        assert new_session['key'] == 'value'

    def test_process_request_loads_session(self) -> None:
        session = self.store('session-key')
        session['key'] = 'value'
        session.save()

        request = Request()
        request.cookies['sessionid'] = 'session-key'
        self.middleware.process_request(request)

        request_session = getattr(request, 'session')
        assert request_session['key'] == 'value'

    def test_process_request_creates_session(self) -> None:
        request = Request()
        self.middleware.process_request(request)

        request_session = getattr(request, 'session')
        request_session['key'] = 'value'

        response = Response()
        self.middleware.process_response(request, response)

        assert len(self.store.sessions) == 1
        assert response.cookies['sessionid'].value
