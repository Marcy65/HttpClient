class HttpResponse:

    def __init__(self, response_bytes: bytes, encoding: str = "utf-8", errors: str = "replace"):

        header_lines, content = response_bytes.split(b"\r\n\r\n", maxsplit=1)

        status_line = header_lines.splitlines()[0]
        version, status_code, status = status_line.split(b" ", maxsplit=2)

        self.version = version.decode(encoding=encoding, errors=errors)
        self.status_code = status_code.decode(encoding=encoding, errors=errors)
        self.status = status.decode(encoding=encoding, errors=errors)

        header_lines = header_lines.splitlines()[1:]

        self.headers = {}

        for line in header_lines:
            
            key, value = line.split(b": ", maxsplit=1)
            key = key.decode(encoding=encoding, errors=errors)
            value = value.decode(encoding=encoding, errors=errors)
            self.headers[key] = value

        self.content = content
        self.raw = response_bytes

        return
    
    def text(self, encoding: str = "utf-8", errors: str = "replace"):
        
        return self.content.decode(encoding=encoding, errors=errors)
    
    def __str__(self) -> str:

        representation = f"{self.version} {self.status_code} {self.status}\r\n\r\n"

        for k, v in self.headers.items():
            representation += f"{k}: {v}\r\n"
        representation += "\r\n"

        representation += self.text()

        return representation