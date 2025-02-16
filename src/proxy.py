import socketserver
import http.server
import http.client

# Configuration
LISTEN_HOST = "0.0.0.0"  # Allow connections from other VMs
LISTEN_PORT = 8888
TARGET_HOST = "localhost"
TARGET_PORT = 8080

class ReverseProxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request("GET")

    def do_POST(self):
        self.forward_request("POST")

    def forward_request(self, method):
        """Forwards the request to the target server and sends back the response."""
        try:
            conn = http.client.HTTPConnection(TARGET_HOST, TARGET_PORT)
            conn.request(method, self.path, headers=self.headers)
            response = conn.getresponse()

            # Send response back to the client
            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() != "connection":  # Avoid keep-alive issues
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.read())

            conn.close()
        except Exception as e:
            self.send_error(502, f"Proxy error: {str(e)}")

if __name__ == "__main__":
    with socketserver.ThreadingTCPServer((LISTEN_HOST, LISTEN_PORT), ReverseProxy) as server:
        print(f"Proxy running on {LISTEN_HOST}:{LISTEN_PORT} → Forwarding to {TARGET_HOST}:{TARGET_PORT}")
        server.serve_forever()
