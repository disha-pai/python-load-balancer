from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys


class BackendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            response = {"status": "healthy", "server": self.server.server_name}
        else:
            response = {
                "message": "Hello from a backend server",
                "server": self.server.server_name,
                "path": self.path,
            }

        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    server = HTTPServer(("127.0.0.1", port), BackendHandler)
    server.server_name = f"backend-{port}"
    print(f"Backend running at http://127.0.0.1:{port}")
    server.serve_forever()