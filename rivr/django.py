from rivr.http import Response

def django_view(func):
    def wrap(*args, **kwargs):
        django_response = func(*args, **kwargs)
        if django_response:
            response = Response(django_response.content, django_response.status_code)
            
            response.headers = {} # Reset the headers (removing Content-Type)
            for key, value in django_response._headers.values():
                response.headers[key] = value
            
            return response
    return wrap
