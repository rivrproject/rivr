from rivr.http import ResponseRedirect, ResponsePermanentRedirect

def redirect_to(request, url, permanent=False, **kwargs):
    if permanent:
        return ResponsePermanentRedirect(url % kwargs)
    return ResponseRedirect(url % kwargs)
