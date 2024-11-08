import socket
import ssl
import re
from .httpresponse import HttpResponse

class HttpClient:

    def __init__(self):
        
        self.last_sent_request = None

        return
    
    def get(self, url: str, headers: dict = {}) -> HttpResponse:

        parsed_url = parsed_url = HttpClient._parse_url(url)

        if parsed_url["query"] is not None:
            parsed_url["path"] = parsed_url["path"] + "?" + parsed_url["query"]

        request = HttpClient._build_request(
            method="GET",
            host=parsed_url["host"],
            path=parsed_url["path"],
            headers=headers,
            )
        
        if parsed_url["scheme"] == "http":
            secure = False

        if parsed_url["scheme"] == "https":
            secure = True

        self.last_sent_request = request

        response = self._send_request(request, parsed_url["host"], parsed_url["port"], secure=secure)

        return response
    
    def post(self, url: str, headers: dict = {}, body: bytes | str = None) -> HttpResponse:

        parsed_url = parsed_url = HttpClient._parse_url(url)

        if parsed_url["query"] is not None:
            parsed_url["path"] = parsed_url["path"] + "?" + parsed_url["query"]

        if body is not None:
            headers["Content-Length"] = len(body)
        else:
            headers["Content-Length"] = 0

        request = HttpClient._build_request(
            method="POST",
            host=parsed_url["host"],
            path=parsed_url["path"],
            headers=headers,
            body=body
            )

        if parsed_url["scheme"] == "http":
            secure = False

        if parsed_url["scheme"] == "https":
            secure = True

        self.last_sent_request = request

        response = self._send_request(request, parsed_url["host"], parsed_url["port"], secure=secure)

        return response
    
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

    @staticmethod
    def _build_request(method: str, host: str, path: str, headers: dict = {}, body: bytes | str = None, version: str = "1.1") -> bytes:
        
        ALLOWED_METHODS = ["GET", "POST"]

        method = method.upper()
        if method not in ALLOWED_METHODS:
            raise ValueError("Method not allowed")

        request = f"{method} {path} HTTP/{version}\r\n"

        mandatory_headers = {
            "Host": host,
            "Connection": "close"
        }
        
        for key, value in mandatory_headers.items():
            request += f"{key}: {value}\r\n"

        default_headers = {
            "User-Agent": "HttpClient/1.0",
            "Accept": "*/*",
            "Accept-Encoding": "identity"
        }

        for key, value in default_headers.items():
            if key not in headers.keys():
                request += f"{key}: {value}\r\n"

        for key, value in headers.items():
            if key not in mandatory_headers.keys():
                request += f"{key}: {value}\r\n"

        request += "\r\n"

        request = request.encode(encoding="utf-8")

        if body is not None:

            if isinstance(body, bytes):
                pass
            elif isinstance(body, str):
                body = body.encode(encoding="utf-8")
            else:
                raise TypeError("Body can only be 'bytes' or 'str'")

            request = request + body

        return request
    
    def _send_request(self, request: bytes, host: str, port: int, secure: bool = False) -> HttpResponse:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if secure:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)

        try:
            ip_address = socket.gethostbyname(host)
            sock.connect((ip_address, port))
            sock.sendall(request)

            chunk_size = 4096
            response_bytes = bytearray()
            while True:
                chunk = sock.recv(chunk_size)
                if chunk:
                    response_bytes.extend(chunk)
                else:
                    break
        except socket.gaierror:
            raise SystemExit(f"Hostname \"{host}\" could not be resolved")
        finally:
            sock.close()

        response = HttpResponse(bytes(response_bytes))

        return response