from rivr.middleware import Middleware

try:
    from pymongo import Connection
except ImportError:
    Connection = None

class mongodb(object):
    def __init__(self, func, database=True, collection=True, gridfs=False):
        self.func = func
        self.database = database
        self.collection = collection
        self.gridfs = gridfs
        
        if gridfs or collection:
            self.database = True
    
    def __call__(self, request, *args, **kwargs):
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
        
        if self.database and not hasattr(request, 'mongodb_database'):
            raise Exception, "MongoDB Database missing"
        
        if self.collection and not hasattr(request, 'mongodb_collection'):
            raise Exception, "MongoDB Collection missing"
        
        if self.gridfs:
            import gridfs
            request.mongodb_gridfs = gridfs.GridFS(request.mongodb_database)
        
        return self.func(request, *args, **kwargs)

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
