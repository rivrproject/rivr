from typing import Callable
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from rivr.wsgi import WSGIHandler
from rivr.middleware.debug import DebugMiddleware
from rivr.request import Request
from rivr.response import Response

__all__ = ['serve']


def serve(
    handler: Callable[[Request], Response],
    host: str = 'localhost',
    port: int = 8080,
    debug: bool = True,
):
    """
    Starts a developent server on the local machine. By default, the
    server runs on port 8080 on localhost. You can pass in a different
    hostname and/or IP using the keyword arguments.
    """

    if debug:
        handler = DebugMiddleware.wrap(handler)

    httpd = WSGIServer((host, port), WSGIRequestHandler)
    httpd.set_app(WSGIHandler(handler))
    print("Development server is running at http://%s:%s/" % (host, port))
    httpd.serve_forever()
