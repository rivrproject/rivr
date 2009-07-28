from rivr.http import Http404

class Array(object):
    def __init__(self, *views):
        self.views = views
    
    def __call__(self, request):
        for view in self.views:
            try:
                response = view(request)
                if response:
                    return response
            except Http404:
                continue
        
        raise Http404
