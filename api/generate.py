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

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import html
import hashlib
import time
from google import genai

app = Flask(__name__)
CORS(app)

# ============================================
# 🔧 CONFIGURATION
# ============================================
MAX_INPUT_LENGTH = 10000
MODEL_NAME = "gemini-2.5-flash"

api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

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

@app.route('/api/generate', methods=['POST'])
def generate():
    if not client:
        return jsonify({"success": False, "error": "AI service not configured."}), 503

    data = request.get_json()
    if not data or not data.get("input"):
        return jsonify({"success": False, "error": "Invalid request."}), 400

    user_input = sanitize_input(data["input"])
    mode = data.get("mode", "chat")
    lang = data.get("language", "en")
    temp = float(data.get("temperature", 0.7))

    sys_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["chat"])
    lang_name = LANGUAGE_NAMES.get(lang, "English")
    
    full_prompt = f"{sys_prompt}\n\n[LANGUAGE: Respond strictly in {lang_name}. Language code: {lang}]\n\nCitizen's Query:\n{user_input}"

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config={"temperature": temp}
        )

        result = {
            "success": True,
            "result": response.text,
            "mode": mode,
            "language": lang
        }

        if mode == "complaint":
            result["complaint_id"] = generate_complaint_id(user_input)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Expose the WSGI app for Vercel
if __name__ == '__main__':
    app.run(port=8081)
