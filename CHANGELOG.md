# rivr changelog

## TBD

### Breaking Changes

- The `rivr.request` and `rivr.response` modules have been merged into
  `rivr.http`.
- `Request` object's `cookies` is now an instance of
  `http.cookies.SimpleCookie`.

### Enhancements

- `Request` now accepts and contains a query parameter. This change deprecates
  get parameter and `GET` property on `Request`.

## 0.8.0 (2020-10-06)

### Breaking Changes

- Support for Python 2 was removed. Python 3.6 or newer is now required.

### Enhancements

- Added typing support to rivr.
- `Response` objects now include a `.content_type` header accessor.
