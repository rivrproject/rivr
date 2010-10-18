from rivr.http import ResponseRedirect, ResponsePermanentRedirect

class RedirectMiddleware(object):
    def __init__(self, url, permanent=False):
        self.url = url
        self.permanent = permanent
    
    def __call__(self, request, **kwargs):
        if self.permanent:
            return ResponsePermanentRedirect(self.url % kwargs)
        return ResponseRedirect(self.url % kwargs)
