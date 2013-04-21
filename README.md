rivr is a microweb framework inspired by djng, the reason I decided to create rivr and not use djng was that djng still depended on Django. I wanted rivr for places where I don't have Django. It is a lightweight framework which can be included along side another python application. rivr does not have a database layer, you are free to use whatever you choose.

What rivr includes:

- Django like template engine
- Domain router (Like django's URL router, but you can have a regex search over the whole domain, useful for subdomains).
- A debugging middleware
- Basic HTTP authentication

Simple views:

    def hello_world(request):
        return Response('Hello, World!', content_type='text/plain')

View router:

    router = Router()

    @router.register(r'^$')
    def index(request):
        return Response('Hello world.')

    @router.register(r'^test/$')
    def test(request):
        return Response('Testing!')

