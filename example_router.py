import rivr

def index(request):
    return rivr.Response('index view.')

def test(request):
    return rivr.Response('test view.')

router = rivr.Router(
    (r'^$', index),
    (r'^test/$', test)
)

def example(request):
    return rivr.Response('Example view. Showing the register command on a router.')
router.register(r'^example/$', example)

def page(request, slug):
    return rivr.Response('page view, slug is `%s`' % slug)
router.register(r'^(?P<slug>[-\w]+)/$', page)

if __name__ == '__main__':
    rivr.serve(router)
