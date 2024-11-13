import socket
import ssl
from .httprequest import HttpRequest
from .httpresponse import HttpResponse

class HttpClient:
    
    def get(self, url: str, headers: dict = {}) -> HttpResponse:

        request = HttpRequest(
            method="GET",
            url=url,
            headers=headers
        )

        response = self._send_request(request)

        request.response = response
        response.request = request

        return response
    
    def post(self, url: str, headers: dict = {}, body: str | bytes = None) -> HttpResponse:

        request = HttpRequest(
        method="POST",
        url=url,
        headers=headers,
        body=body
        )
        
        response = self._send_request(request)

        request.response = response
        response.request = request

        return response
    
    def _send_request(self, request: HttpRequest) -> HttpResponse:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if request.scheme == "https":
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=request.host)

        try:
            ip_address = socket.gethostbyname(request.host)
            sock.connect((ip_address, request.port))
            sock.sendall(request.to_bytes())

            chunk_size = 4096
            response_bytes = b""
            while True:
                chunk = sock.recv(chunk_size)
                if chunk:
                    response_bytes += chunk
                else:
                    break
        except socket.gaierror:
            raise SystemExit(f"Hostname \"{request.host}\" could not be resolved")
        finally:
            sock.close()

        response = HttpResponse(response_bytes)
        
        return response