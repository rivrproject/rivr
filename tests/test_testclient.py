import pytest

from rivr.http import Request, Response
from rivr.tests import TestClient


def view(request: Request) -> Response:
    return Response('{} {}'.format(request.method, request.path))


@pytest.fixture
def client() -> TestClient:
    return TestClient(view)


def test_http(client: TestClient) -> None:
    response = client.http('METHOD', '/path/')
    assert response.content == 'METHOD /path/'


def test_options(client: TestClient) -> None:
    response = client.options('/')
    assert response.content == 'OPTIONS /'


def test_head(client: TestClient) -> None:
    response = client.head('/')
    assert response.content == 'HEAD /'


def test_get(client: TestClient) -> None:
    response = client.get('/')
    assert response.content == 'GET /'


def test_put(client: TestClient) -> None:
    response = client.put('/')
    assert response.content == 'PUT /'


def test_post(client: TestClient) -> None:
    response = client.post('/')
    assert response.content == 'POST /'


def test_patch(client: TestClient) -> None:
    response = client.patch('/')
    assert response.content == 'PATCH /'


def test_delete(client: TestClient) -> None:
    response = client.delete('/resource')
    assert response.content == 'DELETE /resource'
