import rivr


class ExampleAuthMiddleware(rivr.AuthMiddleware):
    def check_password(self, username, password):
        return username == 'kylef' and password == 'letmein'


def hello_world(request):
    return rivr.Response(
        'Hello, {}!'.format(request.user.username), content_type='text/plain'
    )


if __name__ == '__main__':
    rivr.serve(ExampleAuthMiddleware.wrap(hello_world))
