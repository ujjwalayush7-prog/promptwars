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
from google import genai

# ============================================
# 🔧 CONFIGURATION
# ============================================
MAX_INPUT_LENGTH = 10000  # Maximum characters allowed
MODEL_NAME = "gemini-2.5-flash"
ALLOWED_ORIGINS = "*"

# Initialize Gemini client securely from environment variable
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ============================================
# 📝 SYSTEM PROMPTS BY MODE
# ============================================
SYSTEM_PROMPTS = {
    "chat": """You are **Smart Bharat AI**, a helpful, friendly, and knowledgeable civic companion for Indian citizens.

Your role is to help citizens with:
1. **Government Services & Schemes** – Explain eligibility, benefits, and application processes for schemes like PM Kisan, Ayushman Bharat, PM Awas Yojana, Ration Card, MGNREGA, Startup India, PM Mudra Yojana, Jan Dhan Yojana, Sukanya Samriddhi, etc.
2. **Document Guidance** – Tell citizens what documents are needed for various government services (Aadhaar, PAN, Passport, Voter ID, Driving License, Birth Certificate, Income Certificate, Caste Certificate, etc.)
3. **Public Issue Reporting** – Guide citizens on how to report civic issues (road damage, water supply, electricity, sanitation, etc.) to the right authorities.
4. **RTI & Grievance Redressal** – Explain the Right to Information process, CPGRAMS, state-level grievance portals.
5. **Digital India Services** – Guide on DigiLocker, UMANG app, mParivahan, e-Shram, etc.

Guidelines:
- Always be polite, patient, and empathetic.
- Give **step-by-step instructions** when explaining processes.
- Mention **official websites and helpline numbers** where applicable.
- Use **simple, easy-to-understand language** suitable for all citizens.
- If asked in Hindi or another Indian language, respond in that same language.
- Use bullet points and numbered lists for clarity.
- Always mention if there are **deadlines** or **fees** involved.
- If you're unsure about specific details, advise the citizen to verify with the official portal or helpline.
- Format your responses with proper headings, bullet points, and sections for readability.
- At the end of important responses, provide a "📞 Helpline" or "🔗 Official Link" section if applicable.

IMPORTANT: You MUST respond in the SAME LANGUAGE the user writes in. If they write in Hindi, reply in Hindi. If in Tamil, reply in Tamil. And so on.""",

    "services": """You are **Smart Bharat AI – Service Recommender**, an expert on Indian government schemes and welfare programs.

Based on the citizen's profile information (age, income, gender, state, category, occupation), recommend the TOP 5 most relevant government schemes they are eligible for.

For EACH scheme, provide:
1. **Scheme Name** (in both English and Hindi)
2. **Brief Description** (2-3 lines)
3. **Key Benefits** (monetary amount, services provided)
4. **Eligibility Criteria** (who qualifies)
5. **How to Apply** (online portal, CSC center, or offline)
6. **Official Website / Helpline**

Format your response clearly with headers and bullet points.
Prioritize schemes by relevance and impact on the citizen's life.
IMPORTANT: Respond in the language specified by the user. If lang=hi, respond in Hindi. If lang=en, respond in English. Etc.""",

    "complaint": """You are **Smart Bharat AI – Civic Issue Assistant**. A citizen is reporting a public issue or civic complaint.

Based on their complaint details, provide:
1. **Issue Classification** – Categorize the issue (infrastructure, water, electricity, sanitation, law & order, etc.)
2. **Responsible Authority** – Which department or body handles this (Municipal Corporation, PWD, Jal Board, DISCOM, etc.)
3. **How to File Formally** – Step-by-step guide to file the complaint through official channels
4. **Online Portals** – Relevant portals like CPGRAMS, state grievance portals, municipal corporation websites, Swachhta App, 311 services
5. **Helpline Numbers** – Relevant toll-free numbers
6. **Expected Resolution Timeline** – Typical timeframe for such issues
7. **Escalation Path** – What to do if the complaint is not resolved

Be empathetic and helpful. The citizen may be frustrated — acknowledge their concern.
IMPORTANT: Respond in the language specified by the user.""",

    "documents": """You are **Smart Bharat AI – Document Requirements Expert**.

The citizen wants to know what documents are required for a specific government service or process.

Provide a COMPREHENSIVE and ACCURATE list of:
1. **Mandatory Documents** – Documents that are absolutely required
2. **Supporting Documents** – Additional documents that may be needed
3. **Document Format** – Whether originals, photocopies, or self-attested copies are needed
4. **Where to Get Each Document** – If a document needs to be obtained first, explain how
5. **Common Mistakes to Avoid** – Typical issues citizens face with documentation
6. **Digital Alternatives** – DigiLocker or other digital options if available

Format as a clear checklist that citizens can print and use.
IMPORTANT: Respond in the language specified by the user."""
}

# ============================================
# 🌐 LANGUAGE MAPPING
# ============================================
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "ta": "Tamil (தமிழ்)",
    "te": "Telugu (తెలుగు)",
    "bn": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "gu": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "ur": "Urdu (اردو)",
    "od": "Odia (ଓଡ଼ିଆ)"
}


def validate_input(data: dict) -> tuple[bool, str]:
    """
    Validate and sanitize user input data.

    Args:
        data: Parsed JSON request body containing 'input', 'mode', 'language', and 'temperature'.

    Returns:
        Tuple of (is_valid: bool, error_message: str).
    """
    if not isinstance(data, dict):
        return False, "Invalid request format. Expected JSON object."

    user_input = data.get("input", "")
    if not isinstance(user_input, str):
        return False, "Input must be a string."
    if not user_input.strip():
        return False, "Input cannot be empty."
    if len(user_input) > MAX_INPUT_LENGTH:
        return False, f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters."

    mode = data.get("mode", "chat")
    if mode not in SYSTEM_PROMPTS:
        return False, f"Invalid mode. Must be one of: {', '.join(SYSTEM_PROMPTS.keys())}"

    temperature = data.get("temperature", 0.7)
    if not isinstance(temperature, (int, float)):
        return False, "Temperature must be a number."
    if not (0.0 <= temperature <= 1.0):
        return False, "Temperature must be between 0.0 and 1.0."

    language = data.get("language", "en")
    if language not in LANGUAGE_NAMES:
        return False, f"Unsupported language code: {language}"

    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Raw user input string.

    Returns:
        Sanitized string safe for processing.
    """
    return html.escape(text.strip())


def generate_complaint_id(description: str) -> str:
    """
    Generate a unique complaint tracking ID based on timestamp and content hash.

    Args:
        description: The complaint description text.

    Returns:
        A unique complaint ID string in format SB-XXXXXXXXXX.
    """
    raw = f"{time.time()}-{description}"
    hash_digest = hashlib.sha256(raw.encode()).hexdigest()[:10].upper()
    return f"SB-{hash_digest}"


class handler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the Smart Bharat AI Civic Companion API.

    Supports:
        - POST: Process citizen queries through Gemini AI
        - OPTIONS: Handle CORS preflight requests
    """

    def _set_cors_headers(self) -> None:
        """Set CORS and security headers."""
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGINS)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def _send_json_response(self, status_code: int, data: dict) -> None:
        """
        Send a JSON response with appropriate headers.

        Args:
            status_code: HTTP status code.
            data: Dictionary to serialize as JSON response body.
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_POST(self) -> None:
        """Handle POST requests for AI civic assistance."""
        try:
            # Check if API client is configured
            if not client:
                self._send_json_response(503, {
                    "success": False,
                    "error": "AI service is not configured. Please set GOOGLE_API_KEY."
                })
                return

            # Parse request body
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_json_response(400, {
                    "success": False,
                    "error": "Empty request body."
                })
                return

            raw_body = self.rfile.read(content_length)
            body = json.loads(raw_body.decode("utf-8"))

            # Validate input
            is_valid, error_msg = validate_input(body)
            if not is_valid:
                self._send_json_response(400, {
                    "success": False,
                    "error": error_msg
                })
                return

            # Extract and sanitize parameters
            user_input = sanitize_input(body["input"])
            mode = body.get("mode", "chat")
            temperature = float(body.get("temperature", 0.7))
            language = body.get("language", "en")

            # Build the full prompt with language instruction
            system_prompt = SYSTEM_PROMPTS[mode]
            lang_name = LANGUAGE_NAMES.get(language, "English")
            language_instruction = f"\n\n[LANGUAGE: Respond in {lang_name}. Language code: {language}]"

            full_prompt = system_prompt + language_instruction + "\n\nCitizen's Query:\n" + user_input

            # Generate AI response using Google Gemini
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                }
            )

            # Build response payload
            result = {
                "success": True,
                "result": response.text,
                "mode": mode,
                "language": language
            }

            # Add complaint ID if in complaint mode
            if mode == "complaint":
                result["complaint_id"] = generate_complaint_id(user_input)

            self._send_json_response(200, result)

        except json.JSONDecodeError:
            self._send_json_response(400, {
                "success": False,
                "error": "Invalid JSON in request body."
            })
        except Exception as e:
            self._send_json_response(500, {
                "success": False,
                "error": f"Server error: {str(e)}"
            })

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
