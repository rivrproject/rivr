import rivr

def index(request):
    return rivr.Response('index view.')

def test(request):
    return rivr.Response('test view.')

def array(request):
    if request.path == '/array/':
        return rivr.Response('array view.')
    raise rivr.Http404

def another_view(request):
    return rivr.Response('another view.')

if __name__ == '__main__':
    rivr.serve(rivr.DebugMiddleware(rivr.Array(
        rivr.Router(
            (r'^$', index),
            (r'^test/$', test)
        ),
        array,
        another_view
    )))
