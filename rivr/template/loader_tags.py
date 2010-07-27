from rivr import template

register = template.Library()

class IncludeNode(template.Node):
    def __init__(self, template_name):
        self.template_name = template_name
    
    def render(self, context):
        if 'loader' not in context:
            raise template.TemplateSyntaxError("Template loader not in context.")
        
        t = context['loader'].load_template(self.template_name)
        
        if isinstance(t, list):
            raise template.TemplateSyntaxError("%s template not found in: %s" % (self.template_name, ', '.join(t)))
        
        t = template.Template(t)
        return t.render(context)

def do_include(parser, token):
    bits = token.contents.split('"')
    
    if len(bits) != 3:
        raise template.TemplateSyntaxError("Include tag takes one argument: the template file to be included")
    
    return IncludeNode(bits[1])
register.tag('include', do_include)
