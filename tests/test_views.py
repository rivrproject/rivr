import unittest

from rivr import Request, Response
from rivr.views import RedirectView, View


class SimpleView(View):
    def get(self, request: Request) -> Response:
        return Response('Hello Simple View')

    def unknown_method(self, request: Request) -> Response:
        return Response('Unknown Method')


class SimplePostView(View):
    def post(self, request: Request) -> Response:
        return Response()


class ViewTest(unittest.TestCase):
    def test_method_routing(self) -> None:
        view = SimpleView.as_view()

        response = view(Request())
        assert response.status_code == 200
        assert response.content == 'Hello Simple View'

    def test_unimplemented_method_routing(self) -> None:
        view = SimpleView.as_view()

        response = view(Request(method='POST'))
        assert response.status_code == 405

    def test_unknown_implemented_method_routing(self) -> None:
        view = SimpleView.as_view()

        response = view(Request(method='UNKNOWN_METHOD'))
        assert response.status_code == 405

    def test_default_options(self) -> None:
        view = SimpleView.as_view()

        response = view(Request(method='OPTIONS'))
        assert response.status_code == 204
        assert response.headers['Allow'] == 'GET,HEAD,OPTIONS'

    def test_default_head(self) -> None:
        view = SimpleView.as_view()

        response = view(Request(method='HEAD'))
        assert response.status_code == 200
        assert len(response.content) == 0

    def test_head_returns_405_without_get(self) -> None:
        view = SimplePostView.as_view()

        response = view(Request(method='HEAD'))
        assert response.status_code == 405

    def test_head_missing_from_options_without_get(self) -> None:
        view = SimplePostView.as_view()

        response = view(Request(method='OPTIONS'))
        assert response.headers['Allow'] == 'POST,OPTIONS'


class RedirectViewTest(unittest.TestCase):
    def test_permanent_redirect(self) -> None:
        view = RedirectView.as_view(url='/redirect/')

        request = Request()
        response = view(request)
        assert response.status_code == 301
        self.assertEqual(response.headers['Location'], '/redirect/')

    def test_tempoary_redirect(self) -> None:
        view = RedirectView.as_view(url='/redirect/', permanent=False)

        request = Request()
        response = view(request)
        assert response.status_code == 302
        assert response.headers['Location'] == '/redirect/'

    def test_doesnt_include_args(self) -> None:
        view = RedirectView.as_view(url='/redirect/')

        request = Request('/test/', query={'foo': 'bar'})
        response = view(request)
        assert response.status_code == 301
        assert response.headers['Location'] == '/redirect/'

    def test_include_args(self) -> None:
        view = RedirectView.as_view(url='/redirect/', query_string=True)

        request = Request('/test/', query={'foo': 'bar'})
        response = view(request)
        assert response.status_code == 301
        assert response.headers['Location'] == '/redirect/?foo=bar'
