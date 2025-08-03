#!/usr/bin/env python3
"""
Security Tests
Tests für Secret Management und Input Validation
"""

import unittest
import logging
from unittest.mock import patch, MagicMock
from core.security import SecretManager, mask_secret, is_secret, validate_api_key
from core.validation import sanitize_input, validate_prompt_frame
from gui.modules.api_client import APIClient

class TestSecretManagement(unittest.TestCase):
    """Tests für Secret Management"""
    
    def setUp(self):
        """Setup für Tests"""
        self.secret_manager = SecretManager()
        self.test_api_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
        self.test_claude_key = "sk-ant-1234567890abcdef1234567890abcdef1234567890abcdef"
    
    def test_mask_secret(self):
        """Test Secret-Maskierung"""
        masked = mask_secret(self.test_api_key)
        
        # Prüfe dass der Key maskiert wurde
        self.assertNotEqual(masked, self.test_api_key)
        self.assertIn("****", masked)
        self.assertTrue(masked.startswith("sk-"))
        
        # Prüfe dass nur die ersten 4 Zeichen sichtbar sind
        self.assertEqual(masked[:4], "sk-1")
        self.assertTrue(masked.endswith("****"))
        
        # Prüfe dass die Länge korrekt ist
        self.assertEqual(len(masked), len(self.test_api_key))
    
    def test_is_secret_detection(self):
        """Test Secret-Erkennung"""
        # Test mit gültigen API Keys
        self.assertTrue(is_secret(self.test_api_key))
        self.assertTrue(is_secret(self.test_claude_key))
        
        # Test mit normalem Text
        self.assertFalse(is_secret("normal text"))
        self.assertFalse(is_secret(""))
        self.assertFalse(is_secret(None))
    
    def test_validate_api_key(self):
        """Test API Key Validierung"""
        # Test gültige Keys
        self.assertTrue(validate_api_key(self.test_api_key, "openai"))
        self.assertTrue(validate_api_key(self.test_claude_key, "anthropic"))
        
        # Test ungültige Keys
        self.assertFalse(validate_api_key("invalid-key", "openai"))
        self.assertFalse(validate_api_key("sk-invalid", "openai"))
        self.assertFalse(validate_api_key("", "openai"))
        self.assertFalse(validate_api_key(None, "openai"))
    
    def test_secure_log_no_exposure(self):
        """Test dass secure_log keine Secrets exponiert"""
        with patch('core.security.logger') as mock_logger:
            # Test mit Secret im Text
            test_message = f"API Key: {self.test_api_key}"
            self.secret_manager.secure_log(test_message)
            
            # Prüfe dass der geloggte Text maskiert wurde
            logged_message = mock_logger.info.call_args[0][0]
            self.assertNotIn(self.test_api_key, logged_message)
            self.assertIn("****", logged_message)

class TestInputValidation(unittest.TestCase):
    """Tests für Input Validation"""
    
    def test_sanitize_input(self):
        """Test Input-Sanitization"""
        # Test HTML-Tags entfernen
        dirty_input = "<script>alert('xss')</script>Hello World"
        clean_input = sanitize_input(dirty_input)
        self.assertEqual(clean_input, "Hello World")
        
        # Test gefährliche Zeichen entfernen
        dangerous_input = "Hello<>\"'World"
        clean_input = sanitize_input(dangerous_input)
        self.assertEqual(clean_input, "HelloWorld")
        
        # Test leere Eingabe
        self.assertEqual(sanitize_input(""), "")
        self.assertEqual(sanitize_input(None), "")
    
    def test_sanitize_input_extended(self):
        """Test erweiterte Input-Sanitization"""
        # Test verschiedene HTML-Tags
        test_cases = [
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("<div>Content</div>", "Content"),
            ("<p>Text</p>", "Text"),
            ("<img src='x' onerror='alert(1)'>", ""),
            ("<a href='javascript:alert(1)'>Link</a>", "Link"),
            ("<input onfocus='alert(1)'>", ""),
            ("Normal text", "Normal text"),
            ("Text with < and > symbols", "Text with symbols"),
            ("", ""),
            (None, ""),
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            self.assertEqual(result, expected, f"Failed for input: {input_text}")
    
    def test_validate_prompt_frame(self):
        """Test PromptFrame Validierung"""
        # Test gültige Daten
        valid_data = {
            "input": {
                "book": {
                    "title": "Test Book",
                    "genre": "fantasy",
                    "target_audience": "early_reader"
                },
                "chapter": {
                    "number": 1,
                    "title": "Test Chapter",
                    "narrative_purpose": "Introduction"
                }
            }
        }
        
        result = validate_prompt_frame(valid_data)
        self.assertTrue(result.valid)
        
        # Test ungültige Daten
        invalid_data = {
            "input": {
                "book": {
                    "title": ""  # Leerer Titel
                }
            }
        }
        
        result = validate_prompt_frame(invalid_data)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_prompt_frame_extended(self):
        """Test erweiterte PromptFrame Validierung"""
        # Test verschiedene gültige Strukturen
        valid_cases = [
            {
                "input": {
                    "book": {
                        "title": "Test Book",
                        "genre": "fantasy",
                        "target_audience": "early_reader"
                    }
                }
            },
            {
                "input": {
                    "chapter": {
                        "number": 1,
                        "title": "Test Chapter",
                        "narrative_purpose": "Introduction"
                    }
                }
            },
            {
                "book": {
                    "title": "Direct Book",
                    "genre": "adventure",
                    "target_audience": "middle_reader"
                }
            }
        ]
        
        for test_data in valid_cases:
            result = validate_prompt_frame(test_data)
            self.assertTrue(result.valid, f"Should be valid: {test_data}")
        
        # Test ungültige Strukturen
        invalid_cases = [
            {"invalid": "data"},
            {"input": {}},
            {"input": {"book": {"title": ""}}},
            {"input": {"chapter": {"number": 0}}},
        ]
        
        for test_data in invalid_cases:
            result = validate_prompt_frame(test_data)
            self.assertFalse(result.valid, f"Should be invalid: {test_data}")
    
    def test_mask_secret_consistency(self):
        """Test dass mask_secret konsistent ist"""
        test_secrets = [
            "sk-1234567890abcdef1234567890abcdef1234567890abcdef",
            "sk-ant-1234567890abcdef1234567890abcdef1234567890abcdef",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        ]
        
        for secret in test_secrets:
            masked1 = mask_secret(secret)
            masked2 = mask_secret(secret)
            
            # Konsistenz prüfen
            self.assertEqual(masked1, masked2)
            
            # Sicherheit prüfen
            self.assertNotIn(secret, masked1)
            self.assertIn("****", masked1)
            
            # Länge prüfen
            self.assertEqual(len(masked1), len(secret))

class TestAPIClientSecurity(unittest.TestCase):
    """Tests für API Client Security"""
    
    def setUp(self):
        """Setup für Tests"""
        self.test_api_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
        self.test_claude_key = "sk-ant-1234567890abcdef1234567890abcdef1234567890abcdef"
    
    @patch('os.getenv')
    @patch('core.security.secure_log')
    def test_api_client_no_secret_exposure(self, mock_secure_log, mock_getenv):
        """Test dass API Client keine Secrets exponiert"""
        # Mock Umgebungsvariablen
        mock_getenv.side_effect = lambda key: {
            'OPENAI_API_KEY': self.test_api_key,
            'ANTHROPIC_API_KEY': self.test_claude_key
        }.get(key)
        
        # Erstelle API Client
        with patch('openai.api_key'), patch('anthropic.Anthropic'):
            client = APIClient()
        
        # Prüfe dass secure_log mit maskierten Keys aufgerufen wurde
        logged_messages = [call[0][0] for call in mock_secure_log.call_args_list]
        
        for message in logged_messages:
            # Prüfe dass keine unverschlüsselten API Keys im Log sind
            self.assertNotIn(self.test_api_key, message)
            self.assertNotIn(self.test_claude_key, message)
            
            # Prüfe dass maskierte Keys verwendet wurden
            if "Key:" in message:
                self.assertIn("****", message)
    
    def test_api_key_validation_in_client(self):
        """Test API Key Validierung im Client"""
        with patch('os.getenv', return_value=None):
            client = APIClient()
            
            # Prüfe dass Clients nicht verfügbar sind ohne gültige Keys
            self.assertFalse(client.is_openai_available())
            self.assertFalse(client.is_claude_available())

class TestSecurityRegression(unittest.TestCase):
    """Regression Tests für Security"""
    
    def test_no_secret_in_logs(self):
        """Test dass niemals Secrets in Logs erscheinen"""
        test_secrets = [
            "sk-1234567890abcdef1234567890abcdef1234567890abcdef",
            "sk-ant-1234567890abcdef1234567890abcdef1234567890abcdef",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        ]
        
        for secret in test_secrets:
            # Test mask_secret
            masked = mask_secret(secret)
            self.assertNotEqual(masked, secret)
            self.assertIn("****", masked)
            
            # Test is_secret
            self.assertTrue(is_secret(secret))
            
            # Test dass maskierter Text nicht als Secret erkannt wird
            self.assertFalse(is_secret(masked))

if __name__ == "__main__":
    unittest.main() 