import http.server
import socketserver

PORT = 8001

handler = http.server.CGIHTTPRequestHandler
handler.cgi_directories = ["/cgi-bin"]

class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    def server_bind(self):
        super().server_bind()
        self.server_name = "localhost"
        self.server_port = self.server_address[1]

with TCPServer(("", PORT), handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()