import re

from rivr import template

register = template.Library()

class IfNode(template.Node):
    def __init__(self, var, nodelist_true=None, nodelist_false=None):
        self.var = template.Variable(var)
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    
    def render(self, context):
        try:
            if self.var.resolve(context):
                return self.nodelist_true.render(context)
            return self.nodelist_false.render(context)
        except template.VariableDoesNotExist:
            return self.nodelist_false.render(context)
    
def do_if(parser, token):
    var = token.split_contents()[1]
    nodelist_true = parser.parse(('else', 'endif'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    
    return IfNode(var, nodelist_true, nodelist_false)
register.tag('if', do_if)

def do_ifnot(parser, token):
    var = token.split_contents()[1]
    nodelist_false = parser.parse(('else', 'endif'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_true = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_true = template.NodeList()
    
    return IfNode(var, nodelist_true, nodelist_false)
register.tag('ifnot', do_ifnot)

class IfEqualNode(template.Node):
    def __init__(self, var1, var2, nodelist_true=None, nodelist_false=None):
        self.var1 = template.Variable(var1)
        self.var2 = template.Variable(var2)
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    
    def render(self, context):
        try:
            if self.var1.resolve(context) == self.var2.resolve(context):
                return self.nodelist_true.render(context)
            return self.nodelist_false.render(context)
        except template.VariableDoesNotExist:
            return self.nodelist_false.render(context)

def do_ifequal(parser, token):
    var1 = token.split_contents()[1]
    var2 = token.split_contents()[2]
    nodelist_true = parser.parse(('else', 'endifequal'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifequal',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    
    return IfEqualNode(var1, var2, nodelist_true, nodelist_false)
register.tag('ifequal', do_ifequal)

def do_ifnotequal(parser, token):
    var1 = token.split_contents()[1]
    var2 = token.split_contents()[2]
    nodelist_true = parser.parse(('else', 'endifnotequal'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifnotequal',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    
    return IfEqualNode(var1, var2, nodelist_false, nodelist_true)
register.tag('ifnotequal', do_ifnotequal)

class ForNode(template.Node):
    def __init__(self, var, loopvars, nodelist_loop, nodelist_empty):
        self.var = template.Variable(var)
        self.loopvars = loopvars
        self.nodelist_loop = nodelist_loop
        self.nodelist_empty = nodelist_empty
    
    def render(self, context):
        try:
            values = self.var.resolve(context)
            if not hasattr(values, '__len__'):
                values = list(values)
        except KeyError:
            values = []
        
        if len(values) == 0:
            return self.nodelist_empty.render(context)
        
        result = []
        context.push()
        unpack = len(self.loopvars) > 1
        
        for item in values:
            if unpack:
                if (type(values) == dict) and (len(self.loopvars) == 2):
                    context.push(dict(zip(self.loopvars, [item, values[item]])))
                else:
                    context.push(dict(zip(self.loopvars, item)))
            else:
                context[self.loopvars[0]] = item
            result.append(self.nodelist_loop.render(context))
            if unpack:
                context.pop()
        
        context.pop()
        return ''.join(result)

def do_for(parser, token):
    bits = token.contents.split()
    if len(bits) < 4:
        raise template.TemplateSyntaxError("'for' statements should have atleast 4 works (words: %s)" % token.contents)
    
    if bits[-2] != 'in':
        raise template.TemplateSyntaxError("'for' statements should use the following 'for x in y': %s" % token.contents)
    
    var = bits[-1]
    loopvars = re.sub(r' *, *', ',', ' '.join(bits[1:-2])).split(',')
    
    nodelist_loop = parser.parse(('empty', 'endfor'))
    token = parser.next_token()
    if token.contents == 'empty':
        nodelist_empty = parser.parse(('endfor',))
        parser.delete_first_token()
    else:
        nodelist_empty = template.NodeList()
    
    return ForNode(var, loopvars, nodelist_loop, nodelist_empty)
register.tag('for', do_for)

class RenderNode(template.VariableNode):
    def render(self, context):
        try:
            return context[self.variable].render(context)
        except KeyError:
            return ''
        except AttributeError:
            return Template(context[self.variable]).render(context)

def do_render(parser, token):
    var = token.contents.split()[1]
    return RenderNode(var)
register.tag('render', do_render)

class SSINode(template.Node):
    def __init__(self, file_name):
        self.file_name = template.Variable(file_name)
    
    def render(self, context):
        try:
            fp = open(self.file_name.resolve(context), 'r')
            output = fp.read()
            fp.close()
        except IOError:
            output = ''
        
        return Template(output).render(context)

def do_ssi(parser, token):
    bits = token.contents.split()
    
    if len(bits) < 2:
        raise template.TemplateSyntaxError("ssi tag takes one argument: the path to the file to be included")
    
    return SSINode(bits[1])
register.tag('ssi', do_ssi)

class NowNode(template.Node):
    def __init__(self, format_string):
        self.format_string = format_string
    
    def render(self, context):
        from datetime import datetime
        return datetime.now().strftime(self.format_string)

def do_now(parser, token):
    bits = token.contents.split('"')
    if len(bits) != 3:
        raise template.TemplateSyntaxError("'now' statement takes one argument")
    format_string = bits[1]
    return NowNode(format_string)
register.tag('now', do_now)

def do_load(parser, token):
    bits = token.contents.split()
    
    if len(bits) < 2:
        raise template.TemplateSyntaxError("Load tag takes one argument: the module of the template library")
    
    lib = template.import_library(bits[1])
    parser.add_library(lib)
    return ''
register.tag('load', do_load)

class FilterNode(template.Node):
    def __init__(self, filter_expr, nodelist):
        self.filter_expr, self.nodelist = filter_expr, nodelist
    
    def render(self, context):
        output = self.nodelist.render(context)
        context.push({'var':output})
        filtered = self.filter_expr.resolve(context)
        context.pop()
        return filtered

def do_filter(parser, token):
    _, filter_expr = token.contents.split(None, 1)
    nodelist = parser.parse(('endfilter',))
    parser.delete_first_token()
    
    filter_expr = parser.compile_filter("var|%s" % filter_expr)
    return FilterNode(filter_expr, nodelist)
register.tag('filter', do_filter)
