from rivr.http import Response
from rivr.template import Template, Context
from rivr.template.loader import Loader

def render_to_string(template, template_dirs=None, context={}):
    l = Loader()
    
    if template_dirs:
        if isinstance(template_dirs, list):
            l.template_dirs += template_dirs
        else:
            l.template_dirs.append(template_dirs)
    
    t = l.get_template(template)
    c = Context(context)
    c['loader'] = l
    return t.render(c)

def render_to_response(template, template_dirs=None, context={}, *args, **kwargs):
    return Response(render_to_string(template, template_dirs, context), *args, **kwargs)
