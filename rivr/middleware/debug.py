import sys

try:
    from pygments import highlight
    from pygments.lexers import PythonTracebackLexer
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

from rivr.middleware import Middleware
from rivr.http import Response, ResponseNotFound, Http404
from rivr.template import Template, Context, html_escape

error_template = Template("""
<!DOCTYPE HTML>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style type="text/css" media="screen">
    {{ extra_css }}
    html * { padding:0; margin:0; }
    body * { padding:10px 20px; font-family: 'Helvetica Neue', HelveticaNeue, Arial, Helvetica, sans-serif; color: #555; }
    body * * { padding:0; }
    h1, h2 { font-weight: normal; margin-bottom:.4em; letter-spacing: -1px; }
    h1 { font-size: 27px; }
    h2 { font-size: 22px; }
    header { background: #eeeeee; border-bottom: 1px solid #ddd; }
    header h1 { text-shadow: #fff 2px 2px 0; }
    #content { margin: 5px; }
    pre { border: 1px solid #ddd; margin: 10px 0; background: #eee; width: 720px; padding: 10px; border-radius: 6px; overflow: auto; font-size: 9pt; font-weight: normal; }
    pre:hover { border: 1px solid #bbb; }
    code { font-family: Consolas, Monaco, 'Lucida Console', 'Liberation Mono', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Courier New'; }
    </style>
</head>
<body>
    <header>
        <h1>{{ title }}</h1>
    </header>

    <div id="content">
        <section>
            <h2>Traceback</h2>
            {{ traceback }}
        </section>

        <section>
            <h2>Request</h2>
            <pre><code>{{ request }}</code></pre>
        </section>
    </div>
</body>
""")

class DebugMiddleware(Middleware):
    def process_404(self, request):
        return ResponseNotFound('Page Not Found')
    
    def process_exception(self, request, e):
        if isinstance(e, Http404):
            return self.process_404(request)
        
        import traceback
        tb = '\n'.join(traceback.format_exception(*sys.exc_info()))

        if HAS_PYGMENTS:
            formatter = HtmlFormatter(style='borland')
            html_tb = highlight(tb, PythonTracebackLexer(), formatter)
        else:
            html_tb = '<pre><code>%s</pre></code>'

        context = Context({
            'title': str(e),
            'traceback': html_tb,
            'request': html_escape(repr(request))
        })

        if HAS_PYGMENTS:
            context['extra_css'] = formatter.get_style_defs('.highlight')

        return Response(error_template.render(context), status=500)
    
    def process_response(self, request, response):
        if not response:
            return self.process_exception(request, Exception, "View did not return a response.")
        return response
