import os
from urlparse import urlparse

from rivr.middleware import Middleware

import pymongo

class MongoMiddleware(Middleware):
    database = None
    uri = None

    def get_database(self):
        if not self.database:
            if not self.uri and 'MONGODB_URI' in os.environ:
                self.uri = os.environ['MONGODB_URI']

            if not self.uri:
                raise Exception("MongoMiddleware improperly configured")

            m = urlparse(self.uri)
            self.connection = pymongo.Connection(m.hostname, m.port)

            self.database = self.connection[m.path.strip('/')]
            
            if m.username and m.password:
                self.database.authenticate(m.username, m.password)

        return self.database

    def process_request(self, request):
        request.mongodb_database = self.get_database()

