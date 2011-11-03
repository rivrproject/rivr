import os
import pymongo
from urlparse import urlparse

from rivr.middleware import Middleware

def get_database(uri=None):
    if not uri and 'MONGODB_URI' in os.environ:
        uri = os.environ['MONGODB_URI']

    if not uri:
        raise Exception("MongoDB URI unconfigured")

    m = urlparse(uri)
    connection = pymongo.Connection(m.hostname, m.port)
    database = connection[m.path.strip('/')]

    if m.username and m.password:
        database.authenticate(m.username, m.password)

    return database

class MongoMiddleware(Middleware):
    database = None
    uri = None

    def get_database(self):
        if not self.database:
            self.database = get_database(self.uri)

        return self.database

    def process_request(self, request):
        request.mongodb_database = self.get_database()

