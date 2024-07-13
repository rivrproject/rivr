import datetime
import mimetypes
import os
import posixpath
import re
import stat
from email.utils import formatdate, mktime_tz, parsedate_tz
from functools import reduce
from typing import List
from urllib.parse import unquote

from rivr.http import Http404, Request, Response, ResponseNotModified, ResponseRedirect
from rivr.views.base import View

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

    def was_modified_since(self, mtime: float) -> bool:
        if_modified_since = self.request.if_modified_since
        if not if_modified_since:
            return True

        modified_time = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
        return modified_time > if_modified_since

    def directory_index(self, request: Request, path: str, fullpath: str) -> Response:
        if not self.show_indexes:
            raise Http404('Directory indexes are not allowed here.')

        directories: List[str] = []
        files: List[str] = []
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

        def render(accumulator: str, path: str) -> str:
            return accumulator + '<li><a href="{0}">{0}</a></li>\n'.format(path)

        context = {
            'directory': path + '/',
            'files': reduce(render, directories + files, ''),
        }

        return Response(DEFAULT_DIRECTORY_INDEX_TEMPLATE.format(**context))

    def get(self, request: Request, path: str = '') -> Response:
        if not self.document_root:
            raise Exception('StaticView document_root must be set')

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

            _, part = os.path.splitdrive(part)
            _, part = os.path.split(part)

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
        mtime = os.stat(fullpath)[stat.ST_MTIME]

        if not self.was_modified_since(mtime):
            return ResponseNotModified()

        mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'

        with open(fullpath, 'rb') as fp:
            contents = fp.read()

        response = Response(contents, content_type=mimetype)
        response.headers['Last-Modified'] = '%s GMT' % (formatdate(mtime)[:25])
        response.headers['Content-Length'] = str(len(contents))

        return response
