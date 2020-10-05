import os
import posixpath
from urllib.parse import unquote
from functools import reduce
import mimetypes
import stat
import re
from email.utils import formatdate, parsedate_tz, mktime_tz

from rivr.views.base import View
from rivr.request import Request
from rivr.response import Response, ResponseRedirect, ResponseNotModified, Http404


DEFAULT_DIRECTORY_INDEX_TEMPLATE = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Language" content="en-us" />
    <meta name="robots" content="NONE,NOARCHIVE" />
    <title>Index of {directory}</title>
</head>

<body>
    <h1>Index of {directory}</h1>
    <ul>
        {files}
    </ul>
</body>
"""


class StaticView(View):
    """
    Usage in the router:

        (r'(?P<path>.*)$', StaticView.as_view(document_root='.',
                                              show_indexes=True))
    """

    document_root = None
    show_indexes = False
    use_request_path = False
    index = None

    def was_modified_since(self, mtime=0, size=0):
        header = self.request.headers.get('HTTP_IF_MODIFIED_SINCE')
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

    def directory_index(self, request: Request, path: str, fullpath: str) -> Response:
        if not self.show_indexes:
            raise Http404('Directory indexes are not allowed here.')

        directories = []
        files = []
        for f in os.listdir(fullpath):
            if not f.startswith('.'):
                if os.path.isdir(os.path.join(fullpath, f)):
                    directories.append(f + '/')
                else:
                    files.append(f)

        if path != '':
            directories.append('../')

        directories.sort()
        files.sort()

        def render(accumulator, path):
            return accumulator + '<li><a href="{0}">{0}</a></li>\n'.format(path)

        context = {
            'directory': path + '/',
            'files': reduce(render, directories + files, ''),
        }

        return Response(DEFAULT_DIRECTORY_INDEX_TEMPLATE.format(**context))

    def get(self, request: Request, path: str = '') -> Response:
        if not self.document_root:
            raise Exception('Improperly configured view')

        if self.use_request_path:
            path = request.path

        # Clean up given path to only allow serving files below document_root.
        path = posixpath.normpath(unquote(path))
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

        fullpath = os.path.join(self.document_root, newpath)

        if not os.path.exists(fullpath):
            raise Http404('"%s" does not exist.' % newpath)

        if os.path.isdir(fullpath):
            if self.index:
                index = os.path.join(fullpath, self.index)

                if os.path.exists(index) and not os.path.isdir(index):
                    return self.file(index)

            return self.directory_index(request, newpath, fullpath)

        return self.file(fullpath)

    def file(self, fullpath: str) -> Response:
        statobj = os.stat(fullpath)

        if not self.was_modified_since(statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
            return ResponseNotModified()

        mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'

        with open(fullpath, 'rb') as fp:
            contents = fp.read()

        response = Response(contents, content_type=mimetype)
        response.headers['Last-Modified'] = '%s GMT' % (
            formatdate(statobj[stat.ST_MTIME])[:25]
        )
        response.headers['Content-Length'] = str(len(contents))

        return response
