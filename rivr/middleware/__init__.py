class Middleware(object):
    def __init__(self, handler=None):
        self.handler = handler

    def __call__(self, request):
        if hasattr(self, 'process_request'):
            response = self.process_request(request)

            if response:
                return response

        try:
            response = self.handler(request)
        except Exception, e:
            if hasattr(self, 'process_exception'):
                response = self.process_exception(request, e)

                if response:
                    return response
            else:
                raise e

        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)

        return response


class MiddlewareController(Middleware):
    def __init__(self, handler, *middleware):
        super(MiddlewareController, self).__init__(handler)
        self.request_middleware = []
        self.response_middleware = []
        self.exception_middleware = []

        for mw_instance in middleware:
            self.append(mw_instance)

    def append(self, middleware):
        if hasattr(middleware, 'process_request'):
            self.request_middleware.append(middleware.process_request)
        if hasattr(middleware, 'process_response'):
            self.response_middleware.insert(0, middleware.process_response)
        if hasattr(middleware, 'process_exception'):
            self.exception_middleware.insert(0, middleware.process_exception)

    def process_request(self, request):
        response = None

        for request_mw in self.request_middleware:
            response = request_mw(request)
            if response:
                break

        if response is None:
            try:
                response = self.handler(request)
            except Exception, e:
                for exception_mw in self.exception_middleware:
                    response = exception_mw(request, e)
                    if response:
                        return response
                else:
                    raise e

        for response_mw in self.response_middleware:
            response = response_mw(request, response)

        return response

    def process_response(self, request, response):
        pass

    def process_exception(self, request, exception):
        pass
