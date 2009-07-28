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
    <title>Title</title>
</head>
<body>
    <h1>%(title)s</h1>
    
    <h2>Traceback</h2>
    <pre><code>%(traceback)s</code></pre>
    
    <h2>Request</h2>
    <pre><code>%(request)s</code></pre>
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
