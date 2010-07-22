import sys

from rivr.middleware import Middleware
from rivr.http import Response, ResponseNotFound, Http404
from rivr.template import html_escape

ERROR_HTML = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <title>%(title)s</title>
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
    pre { border: 1px solid #ddd; margin: 10px 0; background: #eee; width: 720px; padding: 10px; border-radius: 6px; overflow: auto; font-size: 9pt; font-weight: normal; }
    code { font-family: Consolas, Monaco, 'Lucida Console', 'Liberation Mono', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Courier New'; }
    </style>
</head>
<body>
    <div id="header">
        <h1>%(title)s</h1>
    </div>
    
    <div id="content">
        <h2>Traceback</h2>
        <pre><code>%(traceback)s</code></pre>
        
        <h2>Request</h2>
        <pre><code>%(request)s</code></pre>
    </div>
</body>
"""

class DebugMiddleware(Middleware):
    def process_404(self, request):
        return ResponseNotFound('Page Not Found')
    
    def process_exception(self, request, e):
        if isinstance(e, Http404):
            return self.process_404(request)
        
        import traceback
        tb = '\n'.join(traceback.format_exception(*sys.exc_info()))

        html = ERROR_HTML % {
            'title':str(e),
            'traceback': tb,
            'request':html_escape(repr(request))
        }

        return Response(html, status=500)
    
    def process_response(self, request, response):
        if not response:
            return self.process_exception(request, Exception, "View did not return a response.")
        return response
