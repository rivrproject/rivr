import rivr
from rivr.template import DEFAULT_TEMPLATE_TAGS

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
    return rivr.render_to_response(TEMPLATE, {
        'tag_list': DEFAULT_TEMPLATE_TAGS
    })

if __name__ == '__main__':
    rivr.serve(view)
