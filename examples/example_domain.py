import rivr

def index(request):
    return rivr.Response('Welcome to localhost!')

def profile(request, user):
    return rivr.Response('Welcome to %s\'s profile' % user)

if __name__ == '__main__':
    rivr.serve(rivr.Domain(
        (r'^localhost/$', index), # domain homepages
        (r'^(?P<user>[-\w]+).localhost/$', profile), # user.domain
        (r'^localhost/(?P<user>[-\w]+)/$', profile) # domain/user
    ))
