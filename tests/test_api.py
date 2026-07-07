"""
PromptWars API - Unit Tests
============================
Tests for input validation, sanitization, and API handler logic.

Run with: python -m pytest tests/test_api.py -v
"""

import json
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.index import handler, sanitize_input, generate_complaint_id

class MockRequest:
    def makefile(self, *args, **kwargs):
        return BytesIO(b"")

class TestSmartBharatAPI(unittest.TestCase):
    """Test suite for the Serverless API."""

    def setUp(self):
        self.mock_wfile = BytesIO()
        self.mock_rfile = BytesIO()
        
    def _create_handler(self, headers, body=None):
        req = handler(MockRequest(), ('127.0.0.1', 8000), None)
        req.headers = headers
        req.requestline = "POST /api HTTP/1.1"
        req.request_version = "HTTP/1.1"
        req.wfile = self.mock_wfile
        if body:
            req.rfile = BytesIO(json.dumps(body).encode('utf-8'))
        return req

    def test_sanitize_input(self):
        """Test HTML escaping and stripping"""
        self.assertEqual(sanitize_input(" <script> "), "&lt;script&gt;")
        self.assertEqual(sanitize_input("hello"), "hello")

    def test_generate_complaint_id(self):
        """Test complaint ID generation format"""
        cid = generate_complaint_id("Pothole")
        self.assertTrue(cid.startswith("SB-"))
        self.assertEqual(len(cid), 13) # SB- + 10 chars

    @patch('api.index.api_key', None)
    def test_missing_api_key(self):
        """Test 503 when API key is missing"""
        req = self._create_handler({'Content-Length': '10'})
        req.do_POST()
        response = self.mock_wfile.getvalue().decode('utf-8')
        self.assertIn('503', response)
        self.assertIn('AI service not configured', response)

    @patch('api.index.api_key', 'test_key')
    def test_empty_body(self):
        """Test 400 when body is empty"""
        req = self._create_handler({'Content-Length': '0'})
        req.do_POST()
        response = self.mock_wfile.getvalue().decode('utf-8')
        self.assertIn('400', response)
        self.assertIn('Empty request body', response)

    @patch('api.index.api_key', 'test_key')
    def test_invalid_input(self):
        """Test 400 when input is missing or empty"""
        req = self._create_handler({'Content-Length': '20'}, body={"input": "   "})
        req.do_POST()
        response = self.mock_wfile.getvalue().decode('utf-8')
        self.assertIn('400', response)
        self.assertIn('Invalid request', response)

    @patch('api.index.api_key', 'test_key')
    @patch('api.index.genai.GenerativeModel')
    def test_successful_chat_request(self, mock_model):
        """Test successful 200 OK request"""
        mock_response = MagicMock()
        mock_response.text = "Hello Citizen"
        mock_model.return_value.generate_content.return_value = mock_response
        
        body = {"input": "Hello", "mode": "chat", "language": "en"}
        req = self._create_handler({'Content-Length': str(len(json.dumps(body)))}, body=body)
        
        req.do_POST()
        response = self.mock_wfile.getvalue().decode('utf-8')
        self.assertIn('200', response)
        self.assertIn('Hello Citizen', response)
        self.assertIn('"success": true', response.lower())

if __name__ == "__main__":
    unittest.main()
