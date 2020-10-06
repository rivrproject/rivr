from typing import Callable, Optional, Tuple, Iterable, Any, Dict
import re

from rivr.importlib import import_module
from rivr.request import Request
from rivr.response import Http404, Response, ResponsePermanentRedirect


class Resolver404(Http404):
    pass


class ViewDoesNotExist(Exception):
    pass


class RegexURL(object):
    def __init__(self, regex: str):
        self.regex = re.compile(regex, re.UNICODE)

    def resolve(
        self, path: str
    ) -> Optional[Tuple[Callable, Iterable[Any], Dict[str, Any]]]:
        match = self.regex.search(path)
        if match:
            return self.match_found(path, match)

        return None

    def match_found(
        self, path: str, match
    ) -> Optional[Tuple[Callable, Iterable[Any], Dict[str, Any]]]:
        raise NotImplementedError


class RegexURLPattern(RegexURL):
    def __init__(
        self,
        regex: str,
        callback: Callable[..., Response],
        kwargs={},
        name: Optional[str] = None,
        prefix: Optional[str] = None,
    ):
        super(RegexURLPattern, self).__init__(regex)

        if callable(callback):
            self._callback = callback
        else:
            self._callback = None
            self._callback_str = callback

        self.default_kwargs = kwargs
        self.name = name

        self.add_prefix(prefix)

    def match_found(
        self, path: str, match
    ) -> Optional[Tuple[Callable, Iterable[Any], Dict[str, Any]]]:
        kwargs = match.groupdict()

        if kwargs:
            args: Iterable = tuple()
        else:
            args = match.groups()

        kwargs.update(self.default_kwargs)

        return self.callback, args, kwargs

    @property
    def callback(self):
        if self._callback is not None:
            return self._callback
        try:
            self._callback = import_module(self._callback_str)
        except ImportError as e:
            raise ViewDoesNotExist(
                'Could not import %s (%s)' % (self._callback_str, str(e))
            )

        return self._callback

    def add_prefix(self, prefix):
        if prefix and hasattr(self, '_callback_str'):
            self._callback_str = prefix + '.' + self._callback_str


class RegexURLResolver(RegexURL):
    def __init__(self, regex, router, kwargs={}):
        super(RegexURLResolver, self).__init__(regex)

        if callable(router):
            self._router = router
        else:
            self._router = None
            self._router_str = router

        self.default_kwargs = kwargs

    def match_found(
        self, path: str, match
    ) -> Optional[Tuple[Callable, Iterable[Any], Dict[str, Any]]]:
        new_path = path[match.end() :]

        try:
            callback, args, kwargs = self.router.resolve(new_path)
        except Http404:
            return None

        kwargs.update(self.default_kwargs)
        return callback, args, kwargs

    @property
    def router(self):
        if self._router is not None:
            return self._router
        try:
            self._router = import_module(self._router_str)
        except ImportError as e:
            raise Http404(
                'Could not import %s. Error was: %s' % (self._router_str, str(e))
            )

        return self._router


class BaseRouter(object):
    def __init__(self, *urls):
        """
        Router takes URLs which you can register on creation.

        Example::

            router = rivr.Router(
                (r'^$', index),
                (r'^test/$', test),
            )
        """

        self.urlpatterns = []

        try:
            if isinstance(urls[0], str):
                prefix = urls[0]
                urls = urls[1:]
            else:
                prefix = None
        except IndexError:
            prefix = None

        for t in urls:
            if isinstance(t, (list, tuple)):
                t = url(*t)

            if prefix and hasattr(t, 'add_prefix'):
                t.add_prefix(prefix)

            self.urlpatterns.append(t)

    def __iadd__(self, router):
        self.urlpatterns.__iadd__(router.urlpatterns)

    def __isub__(self, router):
        self.urlpatterns.__isub__(router.urlpatterns)

    def append(self, url):
        self.urlpatterns.append(url)

    def register(self, *t):
        """
        Register a URL pattern with a view. This can either be used as a
        decorator, or it can be used as a method with a view.

        Decorator Example::

            @router.register(r'^$')
            def view(request):
                return Response()

        View Example::

            router.register(r'^$', view)

        """

        if isinstance(t, (list, tuple)):
            if len(t) == 1:

                def func(view):
                    self.register(t[0], view)
                    return view

                return func

            t = url(*t)

        self.append(t)


class Router(BaseRouter):
    append_slash = True
    """
    When append_slash is True, if the request URL does not match any patterns
    in the router and it doesn't end in a slash. The router will HTTP redirect
    any issues to the same URL with a slash appended.
    """

    def resolve(self, path: str) -> Tuple[Callable, Iterable[Any], Dict[str, Any]]:
        for pattern in self.urlpatterns:
            result = pattern.resolve(path)
            if result is not None:
                return result
        raise Resolver404('No URL pattern matched.')

    def __call__(self, request: Request) -> Response:
        if self.append_slash and (not request.path.endswith('/')):
            if (not self.is_valid_path(request.path)) and self.is_valid_path(
                request.path + '/'
            ):
                return ResponsePermanentRedirect(request.path + '/')

        result = RegexURLResolver(r'^/', self).resolve(request.path)
        if result:
            callback, args, kwargs = result
            return callback(request, *args, **kwargs)
        raise Resolver404('No URL pattern matched.')

    def is_valid_path(self, path: str) -> bool:
        try:
            self.resolve(path)
            return True
        except Resolver404:
            return False


class Domain(BaseRouter):
    APPEND_SLASH = True

    def resolve(self, path: str) -> Tuple[Callable, Iterable[Any], Dict[str, Any]]:
        for pattern in self.urlpatterns:
            result = pattern.resolve(path)
            if result is not None:
                return result
        raise Resolver404('No URL pattern matched.')

    def __call__(self, request: Request) -> Response:
        host = request.META.get('HTTP_HOST', 'localhost:80')
        host = ':'.join(host.split(':')[:-1])
        url = host + request.path

        if self.APPEND_SLASH and (not url.endswith('/')):
            if (not self.is_valid_url(url)) and self.is_valid_url(url + '/'):
                return ResponsePermanentRedirect(url + '/')

        result = self.resolve(url)
        if result:
            callback, args, kwargs = result
            return callback(request, *args, **kwargs)
        raise Resolver404('No URL pattern matched.')

    def is_valid_url(self, path: str) -> bool:
        try:
            self.resolve(path)
            return True
        except Resolver404:
            return False


# Shortcuts
def url(regex, view: Callable[..., Response], kwargs={}, name=None, prefix=None):
    if isinstance(view, list):
        return RegexURLResolver(regex, view[0], kwargs)

    as_view = getattr(view, 'as_view', None)
    if as_view and callable(as_view):
        view = as_view()

    return RegexURLPattern(regex, view, kwargs, name, prefix)


def include(router):
    return [router]
