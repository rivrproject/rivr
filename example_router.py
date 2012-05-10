import rivr

def index(request):
    return rivr.Response('index view.')

def test(request):
    return rivr.Response('test view.')

router = rivr.Router(
    (r'^$', index),
    (r'^test/$', test)
)

@router.register(r'^example/$')
def example(request):
    return rivr.Response('Example view. Showing the register decorator.')

def page(request, slug):
    return rivr.Response('page view, slug is `%s`' % slug)
router.register(r'^(?P<slug>[-\w]+)/$', page)

if __name__ == '__main__':
    rivr.serve(rivr.ErrorWrapper(router))
