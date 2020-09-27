# rivr

rivr is a Python WSGI Compatible microweb framework. Following a design similar to Django.

## Examples

### Simple views

```python
def hello_world(request):
    return Response('Hello, World!', content_type='text/plain')
```

### Routing

```python
router = Router()

@router.register(r'^$')
def index(request):
    return Response('Hello world.')

@router.register(r'^test/$')
def test(request):
    return Response('Testing!')
```

### Class based views

```python
class ExampleView(View):
    def get(self, request):
        return Response('Hi')
```

## Testing

rivr exposes a `TestClient` which allows you to create requests and get a
response. Simply pass the TestClient your view, router or application and you
can make requests using the testing DSL to get a response.

```python
from rivr.tests import TestClient

class TestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(router)

    def test_status(self):
        assert self.client.get('/status/').status_code is 204
```

## License

rivr is released under the BSD license. See [LICENSE](LICENSE).

