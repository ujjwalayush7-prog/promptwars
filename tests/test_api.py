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

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.generate import validate_input, sanitize_input, MAX_INPUT_LENGTH


class TestValidateInput(unittest.TestCase):
    """Test suite for the validate_input function."""

    def test_valid_input(self):
        """Test that a properly formatted input passes validation."""
        data = {"input": "Hello, world!", "temperature": 0.7}
        is_valid, error = validate_input(data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_empty_input_rejected(self):
        """Test that empty or whitespace-only input is rejected."""
        data = {"input": "   ", "temperature": 0.5}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_missing_input_rejected(self):
        """Test that missing input field is rejected."""
        data = {"temperature": 0.5}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)

    def test_input_exceeding_max_length_rejected(self):
        """Test that input exceeding MAX_INPUT_LENGTH is rejected."""
        data = {"input": "x" * (MAX_INPUT_LENGTH + 1), "temperature": 0.5}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)
        self.assertIn("maximum length", error.lower())

    def test_input_at_max_length_accepted(self):
        """Test that input exactly at MAX_INPUT_LENGTH is accepted."""
        data = {"input": "x" * MAX_INPUT_LENGTH, "temperature": 0.5}
        is_valid, error = validate_input(data)
        self.assertTrue(is_valid)

    def test_invalid_temperature_type_rejected(self):
        """Test that non-numeric temperature is rejected."""
        data = {"input": "Hello", "temperature": "hot"}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)
        self.assertIn("temperature", error.lower())

    def test_temperature_below_range_rejected(self):
        """Test that temperature below 0.0 is rejected."""
        data = {"input": "Hello", "temperature": -0.1}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)

    def test_temperature_above_range_rejected(self):
        """Test that temperature above 1.0 is rejected."""
        data = {"input": "Hello", "temperature": 1.5}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)

    def test_temperature_boundary_values_accepted(self):
        """Test that temperature at boundary values (0.0 and 1.0) are accepted."""
        for temp in [0.0, 1.0]:
            data = {"input": "Hello", "temperature": temp}
            is_valid, error = validate_input(data)
            self.assertTrue(is_valid, f"Temperature {temp} should be accepted")

    def test_default_temperature_used(self):
        """Test that missing temperature defaults to valid value."""
        data = {"input": "Hello"}
        is_valid, error = validate_input(data)
        self.assertTrue(is_valid)

    def test_non_string_input_rejected(self):
        """Test that non-string input types are rejected."""
        data = {"input": 12345, "temperature": 0.5}
        is_valid, error = validate_input(data)
        self.assertFalse(is_valid)

    def test_non_dict_data_rejected(self):
        """Test that non-dictionary data is rejected."""
        is_valid, error = validate_input("not a dict")
        self.assertFalse(is_valid)
        self.assertIn("invalid", error.lower())


class TestSanitizeInput(unittest.TestCase):
    """Test suite for the sanitize_input function."""

    def test_html_tags_escaped(self):
        """Test that HTML tags are properly escaped."""
        result = sanitize_input("<script>alert('xss')</script>")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_whitespace_stripped(self):
        """Test that leading/trailing whitespace is removed."""
        result = sanitize_input("  hello world  ")
        self.assertEqual(result, "hello world")

    def test_special_characters_escaped(self):
        """Test that special HTML characters are escaped."""
        result = sanitize_input('He said "hello" & goodbye')
        self.assertIn("&amp;", result)
        self.assertIn("&quot;", result)

    def test_normal_text_unchanged(self):
        """Test that normal text passes through unchanged."""
        result = sanitize_input("Hello world")
        self.assertEqual(result, "Hello world")


if __name__ == "__main__":
    unittest.main()
