barebones implementation of an http client written in python using sockets just for the sake of it

currently only supports GET and POST with HTTP/1.1

todo:
* add methods HEAD, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH
* allow request redirects
* add support for content encoding
* add support for Transfer-Encoding: chunked