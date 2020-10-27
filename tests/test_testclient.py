import pytest

from rivr.http import Request, Response
from rivr.test import Client


def view(request: Request) -> Response:
    return Response('{} {}'.format(request.method, request.path))


@pytest.fixture
def client() -> Client:
    return Client(view)


def test_http(client: Client) -> None:
    response = client.http('METHOD', '/path/')
    assert response.content == 'METHOD /path/'


def test_options(client: Client) -> None:
    response = client.options('/')
    assert response.content == 'OPTIONS /'


def test_head(client: Client) -> None:
    response = client.head('/')
    assert response.content == 'HEAD /'


def test_get(client: Client) -> None:
    response = client.get('/')
    assert response.content == 'GET /'


def test_put(client: Client) -> None:
    response = client.put('/')
    assert response.content == 'PUT /'


def test_post(client: Client) -> None:
    response = client.post('/')
    assert response.content == 'POST /'


def test_patch(client: Client) -> None:
    response = client.patch('/')
    assert response.content == 'PATCH /'


def test_delete(client: Client) -> None:
    response = client.delete('/resource')
    assert response.content == 'DELETE /resource'
