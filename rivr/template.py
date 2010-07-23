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

class Context(object):
    def __init__(self, kwargs=None):
        self.dicts = []
        if kwargs:
            self.dicts.append(kwargs)
    
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
            return context[self.variable]
        except KeyError:
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
                context.push(dict(zip(self.loopvars, item)))
            else:
                context[self.loopvars[0]] = item
            result.append(self.nodelist_loop.render(context))
        
        context.pop()
        return ''.join(result)

def do_for(parser, token):
    bits = token.contents.split()
    if len(bits) < 4:
        # todo raise something
        pass
    
    if bits[-2] != 'in':
        # todo raise something
        pass
    
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

def do_render(parser, token):
    var = token.contents.split()[1]
    return RenderNode(var)

BLOCKS = {
    'if': do_if,
    'ifnot': do_ifnot,
    'for': do_for,
    'render': do_render,
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
                    # todo
                    pass
                
                if command in BLOCKS:
                    nodes.append(BLOCKS[command](self, token))
        
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
        return self.nodelist.render(context)

def render_to_string(template_string, context):
    t = Template(template_string)
    c = Context(context)
    return t.render(c)

def render_to_response(template_string, context, *args, **kwargs):
    return Response(render_to_string(template_string, context), *args, **kwargs)

def html_escape(text):
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])
    
    return text
