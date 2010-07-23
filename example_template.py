import rivr
from rivr.template import BLOCKS

TEMPLATE = """
<h1>rivr templates</h1>

<h2>Template tags</h2>
<ul>
{% for tag in tag_list %}
    <li>{{ tag }}</li>
{% endfor %}
</ul>
"""

def view(request):
    t = rivr.Template(TEMPLATE)
    c = rivr.Context({ 'tag_list': BLOCKS.keys() })
    return rivr.Response(t.render(c))

if __name__ == '__main__':
    rivr.serve(view)
