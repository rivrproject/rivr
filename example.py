import rivr

def hello_world(request):
    return rivr.Response('Hello, World!', content_type='text/plain')

if __name__ == '__main__':
    rivr.serve(hello_world)
