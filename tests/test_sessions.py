import unittest

from rivr.http import Request, Response
from rivr.sessions import BaseSession, MemorySessionStore, SessionMiddleware


class SessionMiddlewareTests(unittest.TestCase):
    def setUp(self):
        super(SessionMiddlewareTests, self).setUp()
        self.middleware = SessionMiddleware()

    def test_default_cookie_name(self):
        self.assertEqual(self.middleware.cookie_name, 'sessionid')

    def test_default_session_store(self):
        self.assertEqual(self.middleware.session_store, None)

    def test_raises_without_session_store(self):
        with self.assertRaises(Exception):
            self.middleware.dispatch(None, None)

    def test_persists_new_session_key(self):
        def view(request):
            request.session['key'] = 'value'
            return Response()

        self.middleware.session_store = MemorySessionStore()
        response = self.middleware.dispatch(view, Request())

        self.assertIsNotNone(response.cookies['sessionid'].value)


class BaseSessionTests(unittest.TestCase):
    def setUp(self):
        super(BaseSessionTests, self).setUp()
        self.session = BaseSession()

    def test_unmodified_by_default(self):
        self.assertFalse(self.session.modified)

    def test_setting_value(self):
        self.session['key'] = 'value'
        self.assertEqual(self.session['key'], 'value')
        self.assertTrue('key' in self.session)

    def test_deleting_value(self):
        self.session['key'] = 'value'
        del self.session['key']
        self.assertFalse('key' in self.session)

    def test_clearing(self):
        self.session['key'] = 'value'
        self.session.clear()
        self.assertFalse('key' in self.session)


class MemorySessionStoreTests(unittest.TestCase):
    def setUp(self):
        super(MemorySessionStoreTests, self).setUp()
        self.store = MemorySessionStore()
        self.middleware = SessionMiddleware(session_store=self.store)

    def test_persists_session(self):
        session = self.store('session-key')
        session['key'] = 'value'
        session.save()

        new_session = self.store('session-key')
        self.assertEqual(new_session['key'], 'value')

    def test_process_request_loads_session(self):
        session = self.store('session-key')
        session['key'] = 'value'
        session.save()

        request = Request()
        request.cookies['sessionid'] = 'session-key'
        self.middleware.process_request(request)

        request_session = getattr(request, 'session')
        assert request_session['key'] == 'value'

    def test_process_request_creates_session(self):
        request = Request()
        self.middleware.process_request(request)

        request_session = getattr(request, 'session')
        request_session['key'] = 'value'

        response = Response()
        self.middleware.process_response(request, response)

        assert len(self.middleware.session_store.sessions) == 1
        assert response.cookies['sessionid'].value
