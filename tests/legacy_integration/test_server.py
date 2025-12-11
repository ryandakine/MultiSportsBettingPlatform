#!/usr/bin/env python3
"""
Simple test server for YOLO mode
"""

import http.server
import socketserver
import json
import datetime

class YOLOHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "mode": "yolo_test",
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "error": "YOLO TEST: Endpoint not found",
                "path": self.path
            }
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

if __name__ == "__main__":
    PORT = 8008
    with socketserver.TCPServer(("", PORT), YOLOHandler) as httpd:
        print(f"🚀 YOLO Test Server running on port {PORT}")
        print(f"🔗 Health Check: http://localhost:{PORT}/health")
        httpd.serve_forever() 