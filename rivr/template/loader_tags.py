from rivr import template

register = template.Library()

BLOCK_CONTEXT_KEY = 'block_context'

class BlockContext(object):
    def __init__(self):
        self.blocks = {}

    def has_block(self, name):
        return name in self.blocks and len(self.blocks[name])

    def add_blocks(self, blocks):
        for name, block in blocks.iteritems():
            if name in self.blocks:
                self.blocks[name].insert(0, block)
            else:
                self.blocks[name] = [block]

    def pop(self, name):
        try:
            return self.blocks[name].pop()
        except (IndexError, KeyError):
            return None

    def push(self, name, block):
        self.blocks[name].append(block)

class ExtendsNode(template.Node):
    def __init__(self, template_name, nodelist):
        self.template_name = template_name
        self.blocks = dict([(n.name, n) for n in nodelist.get_nodes_by_type(BlockNode)])

    def get_parent(self, context):
        if 'loader' not in context:
            raise template.TemplateSyntaxError("Template loader not in context.")
        
        t = context['loader'].load_template(self.template_name)
        
        if isinstance(t, list):
            raise template.TemplateSyntaxError("%s template not found in: %s" % (self.template_name, ', '.join(t)))
        
        return template.Template(t)

    def render(self, context):
        context[BLOCK_CONTEXT_KEY] = BlockContext()
        context[BLOCK_CONTEXT_KEY].add_blocks(self.blocks)
        return self.get_parent(context).render(context)

def do_extends(parser, token):
    bits = token.contents.split('"')

    if len(bits) != 3:
        raise template.TemplateSyntaxError("Extends tag takes one argument: the template file to be included")

    nodelist = parser.parse()

    if nodelist.get_nodes_by_type(ExtendsNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])

    return ExtendsNode(bits[1], nodelist)
register.tag('extends', do_extends)

class BlockNode(template.Node):
    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        if BLOCK_CONTEXT_KEY in context and context[BLOCK_CONTEXT_KEY].has_block(self.name):
            return context[BLOCK_CONTEXT_KEY].pop(self.name).render(context)
        return self.nodelist.render(context)

def do_block(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' tag takes only one argument" % bits[0])
    block_name = bits[1]

    block_nodelist = parser.parse(('endblock',))
    parser.delete_first_token()

    return BlockNode(block_name, block_nodelist)
register.tag('block', do_block)

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
