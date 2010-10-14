from rivr.middleware import Middleware

try:
    from pymongo import Connection
except ImportError:
    Connection = None

def mongodb(func):
    def new_func(request, *args, **kwargs):
        if Connection and 'mongodb_host' in kwargs and 'mongodb_port' in kwargs:
            request.mongodb_connection = Connection(kwargs['mongodb_host'], kwargs['mongodb_port'])
            del kwargs['mongodb_host']
            del kwargs['mongodb_port']
        
        if 'mongodb_database' in kwargs and hasattr(request, 'mongodb_connection'):
            request.mongodb_database = request.mongodb_connection[kwargs['mongodb_database']]
            del kwargs['mongodb_database']
        
        if 'mongodb_collection' in kwargs and hasattr(request, 'mongodb_database'):
            request.mongodb_collection = request.mongodb_database[kwargs['mongodb_collection']]
            del kwargs['mongodb_collection']
        
        if not hasattr(request, 'mongodb_collection'):
            raise Exception, "MongoDB Collection missing"
        
        return func(request, *args, **kwargs)
    return new_func

class MongoDBMiddleware(Middleware):
    def __init__(self, host=None, port=None, database=None, collection=None, handler=None):
        super(MongoDBMiddleware, self).__init__(handler)
        
        self.connection = None
        self.database = None
        self._database = None
        self.collection = None
        self._collection = None
        
        if Connection and host and port:
            self.connection = Connection(host, port)
        
        if database:
            self._database = database
            if self.connection:
                self.database = self.connection[database]
            
        if collection:
            self._collection = collection
            if self.connection:
                self.collection = self.database[collection]
    
    def process_request(self, request):
        if self.connection:
            request.mongodb_connection = self.connection
        
        if self.database:
            request.mongodb_database = self.database
        elif self._database and hasattr(request, 'mongodb_connection'):
            request.mongodb_database = request.mongodb_connection[self._database]
        
        if self.collection:
            request.mongodb_collection = self.collection
        elif self._collection and hasattr(request, 'mongodb_database'):
            request.mongodb_collection = request.mongodb_database[self._collection]
