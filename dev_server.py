import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse
import importlib.util
from dotenv import load_dotenv

load_dotenv()

# Add the project root to the path so we can import the API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PORT = 8000
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

class VercelDevHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/generate':
            # Dynamically load the generate.py handler
            spec = importlib.util.spec_from_file_location("generate", "api/generate.py")
            generate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generate_module)
            
            # Create an instance of the handler and pass the request to it
            api_handler = generate_module.handler(self.request, self.client_address, self.server)
        else:
            self.send_error(404, "API endpoint not found")

    def do_OPTIONS(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/generate':
            spec = importlib.util.spec_from_file_location("generate", "api/generate.py")
            generate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generate_module)
            api_handler = generate_module.handler(self.request, self.client_address, self.server)
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

with socketserver.TCPServer(("", PORT), VercelDevHandler) as httpd:
    print(f"Local Dev Server running at http://localhost:{PORT}")
    print(f"Make sure you have your .env file with GOOGLE_API_KEY set!")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
