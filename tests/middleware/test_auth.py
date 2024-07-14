import pytest

from rivr.http import Request, Response
from rivr.middleware.auth import AnnonymousUser, AuthMiddleware, User
from rivr.test import Client


class ExampleAuthMiddleware(AuthMiddleware):
    def check_password(self, userid, password):
        return userid == 'kylef' and password == 'letmein'

    def authorize_bearer(self, request, token):
        if token == 'letmein':
            return User('test')
        return AnnonymousUser()


def view(request: Request) -> Response:
    return Response('ok')


@pytest.fixture
def client() -> Client:
    middleware = ExampleAuthMiddleware.wrap(view)
    return Client(middleware)


def test_basic_authorized(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'Basic a3lsZWY6bGV0bWVpbg==',
        },
    )
    assert response.status_code == 200


def test_basic_authorizedc_case_insensitive_scheme(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'basic a3lsZWY6bGV0bWVpbg==',
        },
    )
    assert response.status_code == 200


def test_basic_unauthorized_no_credentials(client: Client) -> None:
    response = client.get('/')
    assert response.status_code == 401


def test_basic_unauthorized_incorrect_encoded_credentials(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'Bearer notb64!',
        },
    )
    assert response.status_code == 401


def test_bearer_authorized(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'Bearer letmein',
        },
    )
    assert response.status_code == 200


def test_unauthorized_unknown_scheme(client: Client) -> None:
    response = client.get(
        '/',
        headers={
            'Authorization': 'unknownscheme a3lsZWY6bGV0bWVpbg==',
        },
    )
    assert response.status_code == 401
