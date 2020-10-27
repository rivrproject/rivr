# rivr changelog

## TBD

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
