from rivr.sessions import BaseSessionStore

class MongoSessionStore(BaseSessionStore):
    object_id = None
    collection = 'sessions'

    def get_collection(self, request):
        return request.mongodb_database[self.collection]

    def get_session(self, request):
        session = self.get_collection(request).find_one({'key': self.session_key})
        if session:
            self.object_id = session['_id']
            self.data = session['data']

    def save(self, request):
        collection = self.get_collection(request)

        if not self.data and self.object_id: # delete our session
            self.object_id = collection.remove(self.object_id)
        else: # update our session
            if not self.session_key:
                self.generate_key()

            session = {
                "key": self.session_key,
                "data": self.data
            }

            if self.object_id:
                session['_id'] = self.object_id

            self.object_id = collection.save(session)

