import re

from rivr.http import Response

HTML_ESCAPE_DICT = {
    '<': '&lt;',
    '>': '&gt;',
    
    '&':'&amp;',
    '"':'&quot;',
    "'":'&#39;',
    
}

BLOCK_TAG_START = '{%'
BLOCK_TAG_END = '%}'
VARIABLE_TAG_START = '{{'
VARIABLE_TAG_END = '}}'
COMMENT_TAG_START = '{#'
COMMENT_TAG_END = '#}'

TOKEN_TEXT = 0
TOKEN_VAR = 1
TOKEN_BLOCK = 2
TOKEN_COMMENT = 3

tag_re = re.compile('(%s.*?%s|%s.*?%s|%s.*?%s)' % (
    re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END),
    re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
    re.escape(COMMENT_TAG_START), re.escape(COMMENT_TAG_END))
)

class TemplateSyntaxError(Exception):
    pass

class Context(object):
    def __init__(self, kwargs={}):
        self.dicts = [kwargs]
    
    def __setitem__(self, key, value):
        self.dicts[-1][key] = value
    
    def __getitem__(self, key):
        for d in reversed(self.dicts):
            if key in d:
                return d[key]
        raise KeyError(key)
    
    def __delitem__(self, key):
        del self.dicts[-1][key]
    
    def __contains__(self, key):
        for d in self.dicts:
            if key in d:
                return True
        return False
    
    def push(self, _dict={}):
        self.dicts.append(_dict)
    
    def pop(self):
        self.dicts.pop()

class NodeList(list):
    def render(self, context):
        bits = []
        for node in self:
            if isinstance(node, Node):
                bits.append(node.render(context))
            else:
                bits.append(node)
        return ''.join(bits)

class Node(object):
    def render(self, context):
        pass

class TextNode(Node):
    def __init__(self, s):
        self.s = s
    
    def render(self, context):
        return self.s

class VariableNode(Node):
    def __init__(self, s):
        self.variable = s
    
    def render(self, context):
        try:
            var = context
            for component in self.variable.split('.'):
                if hasattr(var, component):
                    var = getattr(var, component)
                elif type(var) == list:
                    var = var[int(component)]
                else:
                    var = var[component]
            
            if callable(var):
                return var()
            
            return str(var)
        except KeyError:
            return ''
        except ValueError:
            return ''

class IfNode(Node):
    def __init__(self, var, nodelist_true=None, nodelist_false=None):
        self.var = var
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
    
    def render(self, context):
        if self.var in context:
            if context[self.var]:
                return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)
    
def do_if(parser, token):
    var = token.split_contents()[1]
    nodelist_true = parser.parse(('else', 'endif'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return IfNode(var, nodelist_true, nodelist_false)

def do_ifnot(parser, token):
    var = token.split_contents()[1]
    nodelist_false = parser.parse(('else', 'endif'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_true = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_true = NodeList()
    
    return IfNode(var, nodelist_true, nodelist_false)

class ForNode(Node):
    def __init__(self, var, loopvars, nodelist_loop, nodelist_empty):
        self.var = var
        self.loopvars = loopvars
        self.nodelist_loop = nodelist_loop
        self.nodelist_empty = nodelist_empty
    
    def render(self, context):
        try:
            values = context[self.var]
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
        raise TemplateSyntaxError("'for' statements should have atleast 4 works (words: %s)" % token.contents)
    
    if bits[-2] != 'in':
        raise TemplateSyntaxError("'for' statements should use the following 'for x in y': %s" % token.contents)
    
    var = bits[-1]
    loopvars = re.sub(r' *, *', ',', ' '.join(bits[1:-2])).split(',')
    
    nodelist_loop = parser.parse(('empty', 'endfor'))
    token = parser.next_token()
    if token.contents == 'empty':
        nodelist_empty = parser.parse(('endfor',))
        parser.delete_first_token()
    else:
        nodelist_empty = NodeList()
    
    return ForNode(var, loopvars, nodelist_loop, nodelist_empty)

class RenderNode(VariableNode):
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

class IncludeNode(Node):
    def __init__(self, file_name):
        self.file_name = file_name
    
    def render(self, context):
        try:
            fp = open(self.file_name, 'r')
            output = fp.read()
            fp.close()
        except IOError:
            output = ''
        
        return Template(output).render(context)

def do_include(parser, token):
    bits = token.contents.split()
    
    if len(bits) < 2:
        raise TemplateSyntaxError("Include tag takes one argument: the path to the file to be included")
    
    return IncludeNode(bits[1])

class NowNode(Node):
    def __init__(self, format_string):
        self.format_string = format_string
    
    def render(self, context):
        from datetime import datetime
        return datetime.now().strftime(self.format_string)

def do_now(parser, token):
    bits = token.contents.split('"')
    if len(bits) != 3:
        raise TemplateSyntaxError("'now' statement takes one argument")
    format_string = bits[1]
    return NowNode(format_string)

class EscapeNode(VariableNode):
    def render(self, context):
        rendered = super(EscapeNode, self).render(context)
        if rendered:
            return html_escape(rendered)
        return ''

def do_escape(parser, token):
    variable = ' '.join(token.split_contents()[1:])
    return EscapeNode(variable)

DEFAULT_TEMPLATE_TAGS = {
    'if': do_if,
    'ifnot': do_ifnot,
    'for': do_for,
    'render': do_render,
    'include': do_include,
    'now': do_now,
    'escape': do_escape,
}

class Token(object):
    def __init__(self, token_type, contents):
        self.token_type, self.contents = token_type, contents
    
    def split_contents(self):
        return self.contents.split()

class Lexer(object):
    def __init__(self, template_string):
        self.template_string = template_string
    
    def tokenize(self):
        nodes = []
        
        for bit in tag_re.split(self.template_string):
            if bit:
                nodes.append(self.create_token(bit))
        
        return nodes
    
    def create_token(self, token_string):
        if token_string.startswith(VARIABLE_TAG_START):
            return Token(TOKEN_VAR, token_string[len(VARIABLE_TAG_START):-len(VARIABLE_TAG_END)].strip())
        elif token_string.startswith(BLOCK_TAG_START):
            return Token(TOKEN_BLOCK, token_string[len(BLOCK_TAG_START):-len(BLOCK_TAG_END)].strip())
        elif token_string.startswith(COMMENT_TAG_START):
            return Token(TOKEN_COMMENT, '')
        return Token(TOKEN_TEXT, token_string)

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.tags = DEFAULT_TEMPLATE_TAGS
    
    def parse(self, parse_until=[]):
        nodes = NodeList()
        while self.tokens:
            token = self.next_token()
            if token.token_type == TOKEN_TEXT:
                nodes.append(TextNode(token.contents))
            elif token.token_type == TOKEN_VAR:
                nodes.append(VariableNode(token.contents))
            elif token.token_type == TOKEN_BLOCK:
                if token.contents in parse_until:
                    self.prepend_token(token)
                    return nodes
                
                try:
                    command = token.split_contents()[0]
                except IndexError:
                    command = ''
                
                if command in self.tags:
                    nodes.append(self.tags[command](self, token))
                else:
                    raise TemplateSyntaxError("No such tag %s" % command)
        
        return nodes
    
    def prepend_token(self, token):
        self.tokens.insert(0, token)
    
    def next_token(self):
        return self.tokens.pop(0)
    
    def delete_first_token(self):
        del self.tokens[0]

def template_string_to_nodes(template_string):
    tokens = Lexer(template_string).tokenize()
    parser = Parser(tokens)
    return parser.parse()

class Template(object):
    def __init__(self, template_string):
        self.nodelist = template_string_to_nodes(template_string)
    
    def render(self, context):
        try:
            return self.nodelist.render(context)
        except TemplateSyntaxError, e:
            e.template = self
            e.context = context
            raise e

def render_to_string(template_string, context={}):
    t = Template(template_string)
    c = Context(context)
    return t.render(c)

def render_to_response(template_string, context={}, *args, **kwargs):
    return Response(render_to_string(template_string, context), *args, **kwargs)

def html_escape(text):
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])
    
    return text
