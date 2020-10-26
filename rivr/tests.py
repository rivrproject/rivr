from typing import IO, Callable, Dict, Optional, Union

from rivr.http import Request, Response

__all__ = ['TestClient']


class TestClient(object):
    def __init__(self, handler: Callable[[Request], Response]):
        self.handler = handler

    def http(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ) -> Response:
        request = Request(path, method, headers=headers, query=query, body=body)
        return self.handler(request)

    def options(self, path: str, *args, **kwargs) -> Response:
        return self.http('OPTIONS', path, *args, **kwargs)

    def head(self, path: str, *args, **kwargs) -> Response:
        return self.http('HEAD', path, **kwargs)

    def get(self, path: str, *args, **kwargs) -> Response:
        return self.http('GET', path, *args, **kwargs)

    def put(self, path: str, *args, **kwargs) -> Response:
        return self.http('PUT', path, *args, **kwargs)

    def post(self, path: str, *args, **kwargs) -> Response:
        return self.http('POST', path, *args, **kwargs)

    def patch(self, path: str, *args, **kwargs) -> Response:
        return self.http('PATCH', path, *args, **kwargs)

    def delete(self, path: str, *args, **kwargs) -> Response:
        return self.http('DELETE', path, *args, **kwargs)


TestClient.__test__ = False  # type: ignore
