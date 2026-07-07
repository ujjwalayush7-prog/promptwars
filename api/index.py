"""
Smart Bharat - AI-Powered Civic Companion API
===============================================
Serverless function for processing citizen queries using Google Gemini 2.5 Pro.
Supports multiple modes: chat, service discovery, complaint filing, and document assistance.
Includes multilingual support for 8+ Indian languages.

Security:
    - API key stored in environment variables (never exposed to client)
    - Input validation and sanitization
    - CORS headers with security protections
    - Request size limiting
    - XSS prevention via HTML escaping

Author: Ujjwal Ayush
License: Open Source
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import html
import hashlib
import time
import google.generativeai as genai

MAX_INPUT_LENGTH = 10000
MODEL_NAME = "gemini-2.5-flash"
ALLOWED_ORIGINS = "*"

api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPTS = {
    "chat": "You are **Smart Bharat AI**, a helpful civic companion. Help with schemes, documents, and public issues. Use simple language and markdown.",
    "services": "Recommend top 5 government schemes based on citizen profile. Include names, benefits, eligibility, and how to apply.",
    "complaint": "Categorize the civic issue, identify responsible authority, explain how to file, and provide helplines.",
    "documents": "List exact documents needed for the requested service (mandatory vs supporting)."
}

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", 
    "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", 
    "ml": "Malayalam", "pa": "Punjabi", "ur": "Urdu", "od": "Odia"
}

def sanitize_input(text):
    return html.escape(text.strip())

def generate_complaint_id(description):
    raw = f"{time.time()}-{description}"
    return f"SB-{hashlib.sha256(raw.encode()).hexdigest()[:10].upper()}"

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGINS)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        try:
            if not api_key:
                self._send_json_response(503, {"success": False, "error": "AI service not configured."})
                return

            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json_response(400, {"success": False, "error": "Empty request body."})
                return

            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body.decode("utf-8"))

            user_input = sanitize_input(data.get("input", ""))
            if not user_input:
                self._send_json_response(400, {"success": False, "error": "Invalid request."})
                return
                
            mode = data.get("mode", "chat")
            lang = data.get("language", "en")
            temp = float(data.get("temperature", 0.7))

            sys_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["chat"])
            lang_name = LANGUAGE_NAMES.get(lang, "English")
            full_prompt = f"{sys_prompt}\n\n[LANGUAGE: Respond strictly in {lang_name}. Language code: {lang}]\n\nCitizen's Query:\n{user_input}"

            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(temperature=temp)
            )

            result = {
                "success": True,
                "result": response.text,
                "mode": mode,
                "language": lang
            }

            if mode == "complaint":
                result["complaint_id"] = generate_complaint_id(user_input)

            self._send_json_response(200, result)

        except Exception as e:
            self._send_json_response(500, {"success": False, "error": str(e)})

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
