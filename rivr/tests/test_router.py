import unittest

from rivr.router import Router, Resolver404

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
