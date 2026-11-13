from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import cycle
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

BACKENDS = cycle([
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002",
    "http://127.0.0.1:8003",
])
backend_lock = Lock()


class LoadBalancerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Try each backend in round-robin order until one responds.
        for _ in range(3):
            with backend_lock:
                backend = next(BACKENDS)

            try:
                with urlopen(backend + self.path, timeout=2) as response:
                    status = response.status
                    body = response.read()
                    content_type = response.headers.get(
                        "Content-Type", "application/json"
                    )
                break
            except HTTPError as error:
                status = error.code
                body = error.read()
                content_type = error.headers.get(
                    "Content-Type", "application/json"
                )
                break
            except (URLError, TimeoutError):
                continue
        else:
            status = 502
            body = b'{"error": "All backend servers are unavailable"}'
            content_type = "application/json"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

        print(f"{self.path} -> {backend}" if status != 502 else self.path)

    def log_message(self, format, *args):
        print(f"Load balancer: {args[0]}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), LoadBalancerHandler)
    print("Load balancer running at http://127.0.0.1:8000")
    server.serve_forever()