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

    def options(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ) -> Response:
        return self.http('OPTIONS', path, query=query, headers=headers, body=body)

    def head(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.http('HEAD', path, query=query, headers=headers)

    def get(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.http('GET', path, query=query, headers=headers)

    def put(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ) -> Response:
        return self.http('PUT', path, query=query, headers=headers, body=body)

    def post(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ) -> Response:
        return self.http('POST', path, query=query, headers=headers, body=body)

    def patch(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ) -> Response:
        return self.http('PATCH', path, query=query, headers=headers, body=body)

    def delete(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[bytes, IO[bytes]]] = None,
    ) -> Response:
        return self.http('DELETE', path, query=query, headers=headers, body=body)


TestClient.__test__ = False  # type: ignore
