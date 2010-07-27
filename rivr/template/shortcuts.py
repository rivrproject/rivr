from rivr.http import Response
from rivr.template import Template, Context

def render_to_string(template_string, context={}):
    t = Template(template_string)
    c = Context(context)
    return t.render(c)

def render_to_response(template_string, context={}, *args, **kwargs):
    return Response(render_to_string(template_string, context), *args, **kwargs)