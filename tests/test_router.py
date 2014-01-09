import unittest

from rivr.router import Router, Resolver404
from rivr.views import View
from rivr.http import Request, Response


class RouterTest(unittest.TestCase):
    def test_decorator(self):
        r = Router()

        @r.register(r'^test/$')
        def func(request):
            pass

        self.assertEqual(r.resolve('test/'), (func, (), {}))

    def test_register(self):
        r = Router()

        def func(request):
            pass
        r.register(r'^test/$', func)

        self.assertEqual(r.resolve('test/'), (func, (), {}))

    def test_404(self):
        r = Router()
        self.assertRaises(Resolver404, r.resolve, 'test')

    def test_resolver(self):
        def func(request):
            pass

        r = Router(
            (r'^test/$', func),
        )

        self.assertTrue(r.is_valid_path('test/'))
        self.assertFalse(r.is_valid_path('not-found/'))

    def test_register_class_view(self):
        r = Router()

        @r.register(r'^test/$')
        class TestView(View):
            def get(self, request):
                return Response('It works')

        response = r(Request('/test/'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'It works')

