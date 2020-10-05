from typing import Callable, Dict, Optional
from rivr.request import Request
from rivr.response import Response

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

    def get(self, *args, **kwargs) -> Response:
        return self.http('GET', *args, **kwargs)

    def put(self, *args, **kwargs) -> Response:
        return self.http('PUT', *args, **kwargs)

    def post(self, *args, **kwargs) -> Response:
        return self.http('POST', *args, **kwargs)

    def delete(self, *args, **kwargs) -> Response:
        return self.http('DELETE', *args, **kwargs)


TestClient.__test__ = False  # type: ignore
