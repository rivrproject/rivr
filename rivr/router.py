import re

from rivr.importlib import import_module
from rivr.http import Http404
from rivr.http import ResponsePermanentRedirect

class Resolver404(Http404): pass
class ViewDoesNotExist(Exception): pass

class RegexURL(object):
    def __init__(self, regex):
        self.regex = re.compile(regex, re.UNICODE)
    
    def resolve(self, path):
        match = self.regex.search(path)
        if match:
            return self.match_found(path, match)

class RegexURLPattern(RegexURL):
    def __init__(self, regex, callback, kwargs={}, name=None, prefix=None):
        super(RegexURLPattern, self).__init__(regex)
        
        if callable(callback):
            self._callback = callback
        else:
            self._callback = None
            self._callback_str = callback
        
        self.default_kwargs = kwargs
        self.name = name
        
        self.add_prefix(prefix)
    
    def match_found(self, path, match):
        kwargs = match.groupdict()
        
        if kwargs:
            args = tuple()
        else:
            args = match.groups()
        
        kwargs.update(self.default_kwargs)
        
        return self.callback, args, kwargs
    
    #@property
    def callback(self):
        if self._callback is not None:
            return self._callback
        try:
            self._callback = import_module(self._callback_str)
        except ImportError, e:
            raise ViewDoesNotExist('Could not import %s. Error was: %s' % (self._callback_str, str(e)))
        
        return self._callback
    callback = property(callback)
    
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
    
    def match_found(self, path, match):
        new_path = path[match.end():]
        
        try:
            callback, args, kwargs = self.router.resolve(new_path)
        except Http404:
            return
        
        kwargs.update(self.default_kwargs)
        return callback, args, kwargs
    
    #@property 
    def router(self):
        if self._router is not None:
            return self._router
        try:
            self._router = import_module(self._router_str)
        except ImportError, e:
            raise Http404('Could not import %s. Error was: %s' % (mod_name, str(e)))
        
        return self._router
    router = property(router)

class BaseRouter(object):
    def __init__(self, *urls):
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
        if isinstance(t, (list, tuple)):
            if len(t) == 1:
                def func(view):
                    self.register(t[0], view)
                    return view

                return func

            t = url(*t)
        
        self.append(t)

class Router(BaseRouter):
    APPEND_SLASH = True
    
    def resolve(self, path):
        for pattern in self.urlpatterns:
            result = pattern.resolve(path)
            if result is not None:
                return result
        raise Resolver404('No URL pattern matched.')
    
    def __call__(self, request):
        if self.APPEND_SLASH and (not request.path.endswith('/')):
            if (not self.is_valid_path(request.path)) and self.is_valid_path(request.path+'/'):
                return ResponsePermanentRedirect(request.path+'/')
            
        result = RegexURLResolver(r'^/', self).resolve(request.path)
        if result:
            callback, args, kwargs = result
            return callback(request, *args, **kwargs)
        raise Resolver404('No URL pattern matched.')
    
    def is_valid_path(self, path):
        try:
            self.resolve(path)
            return True
        except Resolver404:
            return False

class Domain(BaseRouter):
    APPEND_SLASH = True
    
    def resolve(self, path):
        for pattern in self.urlpatterns:
            result = pattern.resolve(path)
            if result is not None:
                return result
        raise Resolver404('No URL pattern matched.')
    
    def __call__(self, request):
        host = request.META.get('HTTP_HOST', 'localhost:80')
        host = ':'.join(host.split(':')[:-1])
        url = host + request.path
        
        if self.APPEND_SLASH and (not url.endswith('/')):
            if (not self.is_valid_url(url)) and self.is_valid_url(url+'/'):
                return ResponsePermanentRedirect(url+'/')
        
        result = self.resolve(url)
        if result:
            callback, args, kwargs = result
            return callback(request, *args, **kwargs)
        raise Resolver404('No URL pattern matched.')
    
    def is_valid_url(self, path):
        try:
            self.resolve(path)
            return True
        except Resolver404:
            return False

# Shortcuts
def url(regex, view, kwargs={}, name=None, prefix=None):
    if isinstance(view, list):
        return RegexURLResolver(regex, view[0], kwargs)
    else:
        return RegexURLPattern(regex, view, kwargs, name, prefix)

def include(router):
    return [router]
