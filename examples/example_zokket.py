import rivr
from rivr.wsgi import WSGIHandler
import zokket


def hello_world(request):
    return rivr.Response('Hello, World!', content_type='text/plain')


if __name__ == '__main__':
    host = 'localhost'
    port = 8080

    zokket.WSGIServer(WSGIHandler(hello_world), host, port)
    print('Server is running at http://%s:%s/' % (host, port))
    zokket.DefaultRunloop.run()
