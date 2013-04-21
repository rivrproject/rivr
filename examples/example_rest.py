import datetime
import rivr
from rivr.views import RESTView

class HelloWorldView(RESTView):
    def __init__(self):
        self.last_modified = datetime.datetime.now()
        self.target = 'World'

    def get_last_modified(self, request):
        return self.last_modified

    def get(self, request):
        return {'message': 'Hello, %s!' % self.target}

    def post(self, request):
        self.target = request.POST.get('target', 'World')
        self.last_modified = datetime.datetime.now()
        return self.get(request)

if __name__ == '__main__':
    rivr.serve(HelloWorldView.as_view())

