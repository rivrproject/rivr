class Middleware(object):
    @classmethod
    def wrap(cls, view, *initargs, **initkwargs):
        def func(*args, **kwargs):
            return cls(*initargs, **initkwargs).dispatch(view, *args, **kwargs)
        return func

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def dispatch(self, view, request, *args, **kwargs):
        response = self.process_request(request)

        if not response:
            try:
                response = view(request, *args, **kwargs)
            except Exception, e:
                if hasattr(self, 'process_exception'):
                    response = self.process_exception(request, e)
                else:
                    raise e

        return self.process_response(request, response)

    def process_request(self, request):
        return

    def process_response(self, request, response):
        return response


