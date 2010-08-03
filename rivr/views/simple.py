from rivr.http import ResponseRedirect
from rivr.template.response import TemplateResponse

def redirect_to(request, url):
    return ResponseRedirect(url)

def direct_to_template(request, template, extra_context={}, **kwargs):
    return TemplateResponse(request, template, extra_context)
