import unittest

import pytest

from rivr import Request, Response
from rivr.router import Resolver404, Router
from rivr.views import View


class RouterTest(unittest.TestCase):
    def test_decorator(self) -> None:
        r = Router()

        @r.register(r'^test/$')
        def func(request):
            pass

        assert r.resolve('test/') == (func, (), {})

    def test_register(self) -> None:
        r = Router()

        def func(request: Request) -> Response:
            return Response()

        r.register(r'^test/$', func)

        assert r.resolve('test/') == (func, (), {})

    def test_404(self) -> None:
        r = Router()

        with pytest.raises(Resolver404):
            r.resolve('test')

    def test_resolver(self) -> None:
        def func(request: Request) -> Response:
            return Response()

        r = Router(
            (r'^/test/$', func),
        )

        assert r.is_valid_path('/test/')
        assert not r.is_valid_path('/not-found/')

    def test_register_class_view(self) -> None:
        r = Router()

        @r.register(r'^test/$')
        class TestView(View):
            def get(self, request: Request) -> Response:
                return Response('It works')

        response = r(Request('/test/'))
        assert response.status_code == 200
        assert response.content == 'It works'

    def test_append_slashes(self) -> None:
        def func(request: Request) -> Response:
            return Response()

        r = Router(
            (r'^/test/$', func),
        )

        response = r(Request('/test'))
        assert response.status_code == 301
        assert response.headers['location'] == '/test/'

    def test_joining_routers(self) -> None:
        def func(request: Request) -> Response:
            return Response()

        router = Router(
            (r'^/test1/$', func),
        )
        assert len(router.urlpatterns) == 1

        router += Router(
            (r'^/test2/$', func),
        )
        assert len(router.urlpatterns) == 2
