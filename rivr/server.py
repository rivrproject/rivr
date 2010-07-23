from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
from rivr.wsgi import WSGIHandler

def serve(handler, host='localhost', port=8080):
    httpd = WSGIServer((host, port), WSGIRequestHandler)
    httpd.set_app(WSGIHandler(handler))
    print "Server is running at http://%s:%s/" % (host, port)
    httpd.serve_forever()
