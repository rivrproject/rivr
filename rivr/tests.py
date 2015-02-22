from rivr.http import Request


class TestClient(object):
    def __init__(self, handler):
        self.handler = handler

    def http(self, method, path, parameters=None, attributes=None, headers=None):
        request = Request(path, method, parameters, attributes, headers)

        return self.handler(request)

    def get(self, *args, **kwargs):
        return self.http('GET', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.http('PUT', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.http('POST', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.http('DELETE', *args, **kwargs)

