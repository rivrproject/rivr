from rivr.http import ResponseRedirect

def redirect_to(request, url):
    return ResponseRedirect(url)
