import re

from rivr.importlib import import_module
from rivr.template.context import Context

__all__ = ('Template', 'Context')

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

def import_library(library_module):
    module = import_module(library_module)
    return getattr(module, 'register')

class TemplateSyntaxError(Exception):
    pass

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
        self.tags = {}
        self.add_library(import_library('rivr.template.defaulttags'))
    
    def add_library(self, lib):
        self.tags.update(lib.tags)
    
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

class Library(object):
    def __init__(self):
        self.tags = {}
    
    def tag(self, name, function):
        self.tags[name] = function

def template_string_to_nodes(template_string):
    tokens = Lexer(template_string).tokenize()
    parser = Parser(tokens)
    return parser.parse()

def html_escape(text):
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])
    
    return text
