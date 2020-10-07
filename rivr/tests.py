from typing import Callable, Dict, Optional
from rivr.http import Request, Response

__all__ = ['TestClient']


class TestClient(object):
    def __init__(self, handler: Callable[[Request], Response]):
        self.handler = handler

    def http(
        self,
        method: str,
        path: str,
        data=None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        if method == 'GET':
            get = data
        else:
            get = {}

        request = Request(path, method, get, data, headers)

        return self.handler(request)

    def get(self, path: str, *args, **kwargs) -> Response:
        return self.http('GET', path, *args, **kwargs)

    def put(self, path: str, *args, **kwargs) -> Response:
        return self.http('PUT', path, *args, **kwargs)

    def post(self, path: str, *args, **kwargs) -> Response:
        return self.http('POST', path, *args, **kwargs)

    def delete(self, path: str, *args, **kwargs) -> Response:
        return self.http('DELETE', path, *args, **kwargs)


TestClient.__test__ = False  # type: ignore
