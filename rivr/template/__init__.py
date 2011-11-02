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

FILTER_SEPARATOR = '|'
FILTER_ARGUMENT_SEPARATOR = ':'
VARIABLE_ATTRIBUTE_SEPARATOR = '.'
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

literal_re = re.compile(r'^(\'.*\'|".*")$')

def import_library(library_module):
    module = import_module(library_module)
    return getattr(module, 'register')

class TemplateSyntaxError(Exception):
    pass

class VariableDoesNotExist(Exception):
    pass

class Variable(object):
    def __init__(self, var):
        self.var = var
        self.lookups = None
        self.literal = ''
        
        try:
            self.literal = float(var)
            if '.' not in var and 'e' not in var.lower():
                self.literal = int(var)
        except ValueError:
            if literal_re.match(var):
                self.literal = var[1:-1]
            else:
                self.lookups = tuple(var.split(VARIABLE_ATTRIBUTE_SEPARATOR))
    
    def resolve(self, context, fail_silently=True):
        if self.lookups is not None:
            try:
                return self.resolve_lookup(context)
            except VariableDoesNotExist:
                if fail_silently:
                    return ''
                else:
                    raise
        return self.literal
    
    def resolve_lookup(self, context):
        current = context
        for bit in self.lookups:
            try: # Dictionary lookup
                current = current[bit]
            except (TypeError, AttributeError, KeyError):
                try: # Attribute lookup
                    current = getattr(current, bit)
                    if callable(current):
                        try:
                            current = current()
                        except TypeError: # This function requires arguments
                            raise VariableDoesNotExist
                except (TypeError, AttributeError):
                    try: # list-index lookup
                        current = current[int(bit)]
                    except (
                        IndexError, # list index out of range
                        ValueError, # invalid literal for int()
                        KeyError,   # current is a dict without `int(bit)` key
                        TypeError,  # unsubscriptable object
                    ):
                       raise VariableDoesNotExist
        return current

class FilterExpression(object):
    def __init__(self, token, parser):
        self.token = token
        self.filters = []
        bits = token.split('|')
        
        if len(bits) < 1:
            raise TemplateSyntaxError("Variable tags must inclue 1 argument")
        
        self.var = Variable(bits[0].strip())
        
        for filter_name in bits[1:]:
            self.filters.append(parser.find_filter(filter_name.strip()))
    
    def resolve(self, context):
        if isinstance(self.var, Variable):
            obj = self.var.resolve(context)
        else:
            obj = self.var
        
        for filter_func in self.filters:
            obj = filter_func(obj)
        
        return obj

class NodeList(list):
    def render(self, context):
        bits = []
        for node in self:
            if isinstance(node, Node):
                bits.append(node.render(context))
            else:
                bits.append(node)
        return ''.join(bits)

    def get_nodes_by_type(self, nodetype):
        nodes = []
        for node in self:
            if isinstance(node, nodetype):
                nodes.append(node)
        return nodes

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
        return unicode(self.variable.resolve(context))

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
        self.filters = {}
        self.add_library(import_library('rivr.template.defaulttags'))
        self.add_library(import_library('rivr.template.defaultfilters'))
        self.add_library(import_library('rivr.template.loader_tags'))
    
    def add_library(self, lib):
        self.tags.update(lib.tags)
        self.filters.update(lib.filters)
    
    def parse(self, parse_until=[]):
        nodes = NodeList()
        while self.tokens:
            token = self.next_token()
            if token.token_type == TOKEN_TEXT:
                nodes.append(TextNode(token.contents))
            elif token.token_type == TOKEN_VAR:
                nodes.append(VariableNode(self.compile_filter(token.contents)))
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
    
    def compile_filter(self, token):
        return FilterExpression(token, self)
    
    def find_filter(self, filter_name):
        if filter_name in self.filters:
            return self.filters[filter_name]
        else:
            raise TemplateSyntaxError("Invalid filter: '%s'" % filter_name)
    
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
        self.filters = {}
    
    def tag(self, name, function):
        self.tags[name] = function
    
    def filter(self, name, function):
        self.filters[name] = function

def template_string_to_nodes(template_string):
    tokens = Lexer(template_string).tokenize()
    parser = Parser(tokens)
    return parser.parse()

def html_escape(text):
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])
    
    return text
