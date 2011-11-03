import time
from random import random
import hashlib

from rivr.middleware import Middleware

class BaseSessionStore(object):
    def __init__(self, request, session_key=None):
        self.modified = False
        self.session_key = session_key
        self.data = {}

        if self.session_key:
            self.get_session(request)

    def get_session(self, request):
        raise NotImplementedError

    def save(self, request):
        raise NotImplementedError

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.modified = True
        self.data[key] = value

    def __delitem__(self, key):
        self.modified = True
        del self.data[key]

    def has_key(self, key):
        return key in self.data

    def clear(self):
        self.modified = True
        self.data = {}

    def generate_key(self):
        self.modified = True
        self.session_key = hashlib.new('sha1', str(time.time()) + str(random())).hexdigest()

class MemorySessionStoreObject(BaseSessionStore):
    def __init__(self, store, *args, **kwargs):
        self.store = store
        super(MemorySessionStoreObject, self).__init__(*args, **kwargs)

    def get_session(self, request):
        if self.session_key in self.store.sessions:
            self.data = self.store.sessions[self.session_key]

    def save(self, request):
        self.store.sessions[self.session_key] = self.data

class MemorySessionStore(object):
    def __init__(self):
        self.sessions = {}

    def __call__(self, *args, **kwargs):
        return MemorySessionStoreObject(self, *args, **kwargs)

class SessionMiddleware(Middleware):
    cookie_name = 'sessionid'
    cookie_secure = False
    cookie_path = '/'
    cookie_domain = None

    session_store = None

    def process_request(self, request):
        if self.session_store is None:
            raise Exception("SessionMiddleware is improperly configured."
                            "Session store is not defined")

        session_key = request.COOKIES.get(self.cookie_name, None)
        request.session = self.session_store(request, session_key)

    def process_response(self, request, response):
        if request.session.modified:
            # Save the session data and refresh the client cookie.
            request.session.save(request)

            response.set_cookie(self.cookie_name, request.session.session_key,
                path=self.cookie_path, domain=self.cookie_domain,
                secure=self.cookie_secure)

        return response
