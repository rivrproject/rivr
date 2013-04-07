import rivr
from rivr.views import RESTView

class HelloWorldView(RESTView):
    def get(self, request):
        return {'message': 'Hello, World!'}

    def post(self, request):
        target = request.POST.get('target', 'World')
        return {'message': 'Hello, {}!'.format(target)}

if __name__ == '__main__':
    rivr.serve(HelloWorldView.as_view())

