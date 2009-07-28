import rivr

def index(request):
    return rivr.Response('index view.')

def test(request):
    return rivr.Response('test view.')

if __name__ == '__main__':
    rivr.serve(rivr.Router(
        (r'^$', index),
        (r'^test/$', test)
    ))
