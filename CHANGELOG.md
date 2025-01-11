# rivr changelog

## TBD

### Breaking Changes

- Support for Python < 3.9 has been removed.

- `Request` and `Response` `content_type` properties now return `MediaType`
  instead of a string. Use `str(request.content_type)` for former behaviour.

### Enhancements

- `Request` contains `text()` method for decoding a request body.
- `Request` is now available for import from the `rivr` module.

### Bug Fixes

- Support unicode paths and query strings from WSGI.

## 0.10.0 (2024/07/14)

### Enhancements

- `rivr.Request` provides accessors for parsing header values:
    - `authorization`
    - `if_match`
    - `if_not_match`
    - `if_modified_since`
    - `if_unmodified_since`

### Bug Fixes

- StaticView respects If-Modified-Since request header.

## 0.9.0

### Breaking Changes

- The `rivr.request` and `rivr.response` modules have been merged into
  `rivr.http`.
- `Request` object's `cookies` is now an instance of
  `http.cookies.SimpleCookie`.
- `Request`/`Response` object's `headers` is now an instance of
  `wsgiref.headers.Headers`.
- `_` in `Request`s headers are now replaced by dashes (`-`), thus the header
  `Content-Type` is named as `Content-Type` instead of `Content_Type`.
- `RESTResponse` has been removed.
- `rivr.tests.TestClient` has been renamed to `rivr.test.Client`

### Enhancements

- `Request` now accepts and contains a query parameter. This change deprecates
  get parameter and `GET` property on `Request`.

## 0.8.0 (2020-10-06)

### Breaking Changes

- Support for Python 2 was removed. Python 3.6 or newer is now required.

### Enhancements

- Added typing support to rivr.
- `Response` objects now include a `.content_type` header accessor.
