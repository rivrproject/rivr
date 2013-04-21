import rivr

class ExampleMiddleware(rivr.Middleware):
    def process_request(self, request):
        return rivr.Response("Hello World")

def view(request):
    raise Exception, "Debugger example"

if __name__ == '__main__':
    rivr.serve(rivr.MiddlewareController.wrap(view,
        ExampleMiddleware(),  # This example middleware will run instead of our view on process_request
        rivr.DebugMiddleware(),
    ))
