class Middleware(object):
    def __init__(self, handler=None, **kwargs):
        self.handler = handler

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __call__(self, request):
        response = None

        if hasattr(self, 'process_request'):
            response = self.process_request(request)

        if not response:
            try:
                response = self.handler(request)
            except Exception, e:
                if hasattr(self, 'process_exception'):
                    response = self.process_exception(request, e)
                else:
                    raise e

        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)

        return response

