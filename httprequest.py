import re

class HttpRequest:

    def __init__(self, method: str, url: str, headers: dict = {}, body: str | bytes = None):
        
        self.method = method.upper()
        self.url = url

        parsed_url = HttpRequest._parse_url(url)

        self.scheme = parsed_url["scheme"]
        self.host = parsed_url["host"]
        self.port = int(parsed_url["port"])
        self.path = parsed_url["path"]
        self.query = parsed_url["query"]

        if self.query is not None:
            self.path_query = self.path + "?" + self.query
        else:
            self.path_query = self.path

        default_headers = {
            "User-Agent": "HttpClient/1.1",
            "Accept": "*/*",
            "Accept-Encoding": "identity"
        }

        self.headers = default_headers

        for k, v in headers.items():
            self.headers[k] = v

        mandatory_headers = {
            "Host": self.host,
            "Connection": "close"
        }

        for k, v in mandatory_headers.items():
            self.headers[k] = v

        self.body = body
        if body is not None:
            self.headers["Content-Length"] = len(body)
            
        self.response = None

        return
    
    def to_bytes(self, encoding: str = "utf-8") -> bytes:

        request = f"{self.method} {self.path_query} HTTP/1.1\r\n"

        for k, v in self.headers.items():
            request += f"{k}: {v}\r\n"
        request += "\r\n"

        request = request.encode(encoding=encoding)

        if self.body is not None:

            if isinstance(self.body, str):
                request += self.body.encode(encoding=encoding)
            elif isinstance(self.body, bytes):
                request += self.body
            else:
                raise ValueError("Request body can only be 'str' or 'bytes'")
        
        return request

    @staticmethod
    def _parse_url(url: str) -> dict:

        pattern = (r"^(?P<scheme>[a-zA-Z0-9+\-.]+)://"
                   r"(?P<host>[a-zA-Z0-9.-]+)"
                   r"(:(?P<port>\d+))?"
                   r"(?P<path>/[a-zA-Z0-9\-._~%!$&\'()*+,;=:@/]*)?"
                   r"(\?(?P<query>[a-zA-Z0-9\-._~%!$&\'()*+,;=:@/?]*))?")

        match = re.search(pattern, url)

        parsed_url = match.groupdict()

        if parsed_url["scheme"] not in ["http", "https"]:
            raise ValueError("Scheme not supported")

        if parsed_url["port"] is None:
            parsed_url["port"] = 80 if parsed_url["scheme"] == "http" else 443

        parsed_url["path"] = "/" if parsed_url["path"] is None else parsed_url["path"]

        return parsed_url
    
    def __str__(self) -> str:

        return self.to_bytes().decode(encoding="utf-8", errors="replace")