from typing import Dict, Optional, Union
from wsgiref.headers import Headers

from rivr.http.media_type import MediaType


class HTTPMessage:
    def __init__(self, headers: Optional[Union[Headers, Dict[str, str]]] = None):
        if headers:
            if isinstance(headers, dict):
                self.headers = Headers()

                for name, value in headers.items():
                    self.headers[name] = value

            elif isinstance(headers, Headers):
                self.headers = headers
        else:
            self.headers = Headers()

    @property
    def content_type(self) -> Optional[MediaType]:
        content_type = self.headers['Content-Type']
        if content_type:
            return MediaType.parse(content_type)
        return None

    @content_type.setter
    def content_type(self, value: Union[str, MediaType]):
        self.headers['Content-Type'] = str(value)

    @property
    def content_length(self) -> Optional[int]:
        content_length = self.headers['Content-Length']
        if content_length:
            try:
                return int(content_length)
            except TypeError:
                return None

        return None

    @content_length.setter
    def content_length(self, value: int):
        self.headers['Content-Length'] = str(value)
