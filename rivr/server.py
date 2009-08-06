from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
from rivr.wsgi import WSGIHandler

def serve(handler, host='localhost', port=8080):
    httpd = WSGIServer((host, port), WSGIRequestHandler)
    httpd.set_app(WSGIHandler(handler))
    httpd.serve_forever()
