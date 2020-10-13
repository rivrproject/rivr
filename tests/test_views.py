import unittest

from rivr.views import View, RedirectView
from rivr.http import Request, Response


class SimpleView(View):
    def get(self, request):
        return Response('Hello Simple View')

    def unknown_method(self, request):
        return Response('Unknown Method')


class SimplePostView(View):
    def post(self, request):
        pass


class ViewTest(unittest.TestCase):
    def test_method_routing(self):
        view = SimpleView.as_view()

        response = view(Request())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'Hello Simple View')

    def test_unimplemented_method_routing(self):
        view = SimpleView.as_view()

        response = view(Request(method='POST'))
        self.assertEqual(response.status_code, 405)

    def test_unknown_implemented_method_routing(self):
        view = SimpleView.as_view()

        response = view(Request(method='UNKNOWN_METHOD'))
        self.assertEqual(response.status_code, 405)

    def test_default_options(self):
        view = SimpleView.as_view()

        response = view(Request(method='OPTIONS'))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers['Allow'], 'GET,HEAD,OPTIONS')

    def test_default_head(self):
        view = SimpleView.as_view()

        response = view(Request(method='HEAD'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 0)

    def test_head_returns_405_without_get(self):
        view = SimplePostView.as_view()

        response = view(Request(method='HEAD'))
        self.assertEqual(response.status_code, 405)

    def test_head_missing_from_options_without_get(self):
        view = SimplePostView.as_view()

        response = view(Request(method='OPTIONS'))
        self.assertEqual(response.headers['Allow'], 'POST,OPTIONS')


class RedirectViewTest(unittest.TestCase):
    def test_permanent_redirect(self):
        view = RedirectView.as_view(url='/redirect/')

        request = Request()
        response = view(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['Location'], '/redirect/')

    def test_tempoary_redirect(self):
        view = RedirectView.as_view(url='/redirect/', permanent=False)

        request = Request()
        response = view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/redirect/')

    def test_doesnt_include_args(self):
        view = RedirectView.as_view(url='/redirect/')

        request = Request('/test/', query={'foo': 'bar'})
        response = view(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['Location'], '/redirect/')

    def test_include_args(self):
        view = RedirectView.as_view(url='/redirect/', query_string=True)

        request = Request('/test/', query={'foo': 'bar'})
        response = view(request)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['Location'], '/redirect/?foo=bar')
