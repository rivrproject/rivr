import rivr

def auth_handler(username, password):
    return username == 'kylef' and password == 'letmein'

def hello_world(request):
    return rivr.Response('Hello, World!', content_type='text/plain')

if __name__ == '__main__':
    rivr.serve(rivr.AuthMiddleware(auth_handler, hello_world))
