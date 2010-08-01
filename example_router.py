import rivr

def index(request):
    return rivr.Response('index view.')

def test(request):
    return rivr.Response('test view.')

def page(request, slug):
    return rivr.Response('page view, slug is `%s`' % slug)

if __name__ == '__main__':
    rivr.serve(rivr.Router(
        (r'^$', index),
        (r'^test/$', test),
        (r'^(?P<slug>[-\w]+)/$', page)
    ))
