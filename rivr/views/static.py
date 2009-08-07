import os
import posixpath
import urllib
import mimetypes
import stat
import re
from email.Utils import formatdate, parsedate_tz, mktime_tz

from rivr.http import Response, ResponseRedirect, ResponseNotModified, Http404

def was_modified_since(header=None, mtime=0, size=0):
    if header is None:
        return True
    
    matches = re.match(r'^([^;]+)(; length=([0-9]+))?$', header, re.IGNORECASE)
    
    header_mtime = mktime_tz(parsedate_tz(matches.group(1)))
    header_len = matches.group(3)
    
    if header_len and int(header_len) != size:
        return True
    
    if mtime > header_mtime:
        return True
    
    return False

def serve(request, path, document_root=None, show_indexes=False):
    """
    Usage in the router:
    
    (r'(?P<path>.*)$', 'rivr.views.serve', {'document_root':'/usr/var/http/'})
    """
    
    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        
        newpath = os.path.join(newpath, part).replace('\\', '/')
    
    if newpath and path != newpath:
        return ResponseRedirect(newpath)
    
    fullpath = os.path.join(document_root, newpath)
    
    if not os.path.exists(fullpath):
        raise Http404, '"%s" does not exist.' % newpath
    
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(request, newpath, fullpath)
        raise Http404, 'Directory indexes are not allowed here.'
    
    statobj = os.stat(fullpath)
    
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return ResponseNotModified()
    
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    contents = open(fullpath, 'rb').read()
    
    response = Response(contents, content_type=mimetype)
    response.headers['Last-Modified'] = '%s GMT' % formatdate(statobj[stat.ST_MTIME])[:25]
    response.headers['Content-Length'] = str(len(contents))
    
    return response

DEFAULT_DIRECTORY_INDEX_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Language" content="en-us" />
    <meta name="robots" content="NONE,NOARCHIVE" />
    <title>Index of {{ directory }}</title>
</head>

<body>
    <h1>Index of {{ directory }}</h1>
    <ul>
      {% ifnotequal directory "/" %}
        <li><a href="../">../</a></li>
      {% endifnotequal %}
      
      {% for f in files %}
        <li><a href="{{ f }}">{{ f }}</a></li>
      {% endfor %}
    </ul>
</body>
"""

def directory_index(request, path, fullpath):
    from django.template import Context, Template
    
    t = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE)
    
    files = []
    for f in os.listdir(fullpath):
        if not f.startswith('.'):
            if os.path.isdir(os.path.join(fullpath, f)):
                f += '/'
            files.append(f)
    
    return Response(str(t.render(Context({
        'directory': path + '/',
        'files': files,
    }))))
