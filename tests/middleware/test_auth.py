import pytest

from rivr.http import Request, Response
from rivr.middleware.auth import AuthMiddleware
from rivr.test import Client


class ExampleAuthMiddleware(AuthMiddleware):
    def check_password(self, username, password):
        return username == 'kylef' and password == 'letmein'


def view(request: Request) -> Response:
    return Response('ok')


@pytest.fixture
def client() -> Client:
    middleware = ExampleAuthMiddleware.wrap(view)
    return Client(middleware)


def test_authorized(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'Basic a3lsZWY6bGV0bWVpbg==',
        },
    )
    assert response.status_code == 200


def test_unauthorized_no_credentials(client: Client) -> None:
    response = client.get('/')
    assert response.status_code == 401


def test_unauthorized_not_basic_credentials(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'Bearer a3lsZWY6bGV0bWVpbg==',
        },
    )
    assert response.status_code == 401


def test_unauthorized_incorrect_encoded_credentials(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'Bearer notb64!',
        },
    )
    assert response.status_code == 401
