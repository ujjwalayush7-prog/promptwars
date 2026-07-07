from http.server import BaseHTTPRequestHandler
import json
import os
from google import genai

# Gemini client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# 👇 TODO: Update this prompt when the problem drops!
SYSTEM_PROMPT = """You are a helpful AI assistant. 
Analyze the user's input carefully and provide a detailed, well-structured response.

Instructions:
- Be clear and concise
- Use bullet points where helpful
- Provide actionable insights
"""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))

            user_input = body.get("input", "")
            temperature = body.get("temperature", 0.7)

            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=SYSTEM_PROMPT + "\n\nUser Input:\n" + user_input,
                config={
                    "temperature": temperature,
                }
            )

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "result": response.text
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
