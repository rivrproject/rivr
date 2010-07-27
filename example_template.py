import rivr
from rivr.template.defaulttags import register as tag_lib
from rivr.template.defaultfilters import register as filter_lib

TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <title>rivr templates</title>
    <style type="text/css" media="screen">
    html * { padding:0; margin:0; }
    body * { padding:10px 20px; font-family: 'Helvetica Neue', HelveticaNeue, Arial, Helvetica, sans-serif; color: #555; }
    body * * { padding:0; }
    h1, h2 { font-weight: normal; margin-bottom:.4em; letter-spacing: -1px; }
    h1 { font-size: 27px; }
    h2 { font-size: 22px; }
    #header { background: #eeeeee; border-bottom: 1px solid #ddd; }
    #header h1 { text-shadow: #fff 2px 2px 0; }
    #content { margin: 5px; }
    code { border: 1px solid #ddd; background: #eee; padding: 2px 3px; border-radius: 4px; font-size: 9pt; font-weight: normal; font-family: Consolas, Monaco, 'Lucida Console', 'Liberation Mono', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Courier New'; }
    ul { margin-left: 25px; }
    li { list-style: circle; padding-bottom: 5px;}
    </style>
</head>
<body>
    <div id="header">
        <h1>rivr templates</h1>
    </div>
    
    <div id="content">
        <h2>Template tags</h2>
        <ul>
        {% for tag in tag_list %}
            <li><code>{{ tag }}</code></li>
        {% endfor %}
        </ul>
        
        <h2>Template filters</h2>
        <ul>
        {% for filter in filter_list %}
            <li><code>{{ filter }}</code></li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

def view(request):
    return rivr.render_to_response(TEMPLATE, {
        'tag_list': tag_lib.tags,
        'filter_list': filter_lib.filters,
    })

if __name__ == '__main__':
    rivr.serve(view)
