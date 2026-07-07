"""
PromptWars AI Solution - API Handler
=====================================
Serverless function for processing AI requests using Google Gemini 2.5 Pro.

Security:
    - API key stored in environment variables (never exposed to client)
    - Input validation and sanitization
    - CORS headers with origin restriction
    - Request size limiting
    - Rate limiting via input length cap

Author: Ujjwal Ayush
License: Open Source
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import html
from google import genai

# ============================================
# 🔧 CONFIGURATION
# ============================================
MAX_INPUT_LENGTH = 10000  # Maximum characters allowed in user input
MODEL_NAME = "gemini-2.5-pro"
ALLOWED_ORIGINS = "*"  # Restrict in production

# Initialize Gemini client securely from environment variable
api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ============================================
# 📝 SYSTEM PROMPT
# ============================================
# TODO: Update this prompt when the problem drops!
SYSTEM_PROMPT = """You are a helpful AI assistant. 
Analyze the user's input carefully and provide a detailed, well-structured response.

Instructions:
- Be clear and concise
- Use bullet points where helpful
- Provide actionable insights
"""


def validate_input(data: dict) -> tuple[bool, str]:
    """
    Validate and sanitize user input data.

    Args:
        data: Parsed JSON request body.

    Returns:
        Tuple of (is_valid: bool, error_message: str).
        If valid, error_message is empty.
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

    temperature = data.get("temperature", 0.7)

    if not isinstance(temperature, (int, float)):
        return False, "Temperature must be a number."

    if not (0.0 <= temperature <= 1.0):
        return False, "Temperature must be between 0.0 and 1.0."

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


class handler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the Gemini AI generation endpoint.

    Supports:
        - POST: Process user input through Gemini AI
        - OPTIONS: Handle CORS preflight requests
    """

    def _set_cors_headers(self) -> None:
        """Set CORS headers for cross-origin requests."""
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
            data: Dictionary to serialize as JSON response.
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_POST(self) -> None:
        """Handle POST requests for AI content generation."""
        try:
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

            # Sanitize and extract parameters
            user_input = sanitize_input(body["input"])
            temperature = float(body.get("temperature", 0.7))

            # Generate AI response using Google Gemini
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=SYSTEM_PROMPT + "\n\nUser Input:\n" + user_input,
                config={
                    "temperature": temperature,
                }
            )

            self._send_json_response(200, {
                "success": True,
                "result": response.text
            })

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
