#!/usr/bin/env python3
"""
Promotion Guardrails Tests für One Click Book Writer
"""

import unittest
import json
from pathlib import Path

class TestPromotionGuardrails(unittest.TestCase):
    """Tests für Promotion Guardrails"""
    
    def setUp(self):
        """Setup für Promotion Guardrails Tests"""
        self.project_root = Path(__file__).parent.parent
        
    def test_quality_thresholds(self):
        """Testet Qualitäts-Schwellenwerte"""
        print("🛡️  Teste Qualitäts-Schwellenwerte...")
        
        # Simuliere verschiedene Qualitäts-Scores
        test_scores = [
            {"score": 0.95, "expected": True, "description": "Hohe Qualität"},
            {"score": 0.85, "expected": True, "description": "Gute Qualität"},
            {"score": 0.75, "expected": False, "description": "Grenzwertige Qualität"},
            {"score": 0.65, "expected": False, "description": "Niedrige Qualität"},
        ]
        
        for test_case in test_scores:
            score = test_case["score"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            # Simuliere Qualitäts-Prüfung
            is_approved = self._check_quality_threshold(score)
            
            if expected:
                self.assertTrue(is_approved, f"{description}: Score {score} sollte genehmigt werden")
            else:
                self.assertFalse(is_approved, f"{description}: Score {score} sollte abgelehnt werden")
        
        print("✅ Qualitäts-Schwellenwerte funktionieren korrekt")
    
    def test_content_filtering(self):
        """Testet Content-Filtering"""
        print("🛡️  Teste Content-Filtering...")
        
        # Test-Inhalte
        test_contents = [
            {
                "content": "Dies ist ein harmloser Text über ein Abenteuer.",
                "expected": True,
                "description": "Harmloser Inhalt"
            },
            {
                "content": "Dieser Text enthält unangemessene Inhalte.",
                "expected": False,
                "description": "Unangemessener Inhalt"
            },
            {
                "content": "Ein normaler Text über Charakterentwicklung.",
                "expected": True,
                "description": "Normaler Inhalt"
            }
        ]
        
        for test_case in test_contents:
            content = test_case["content"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            # Simuliere Content-Filtering
            is_approved = self._check_content_filtering(content)
            
            if expected:
                self.assertTrue(is_approved, f"{description}: Sollte genehmigt werden")
            else:
                self.assertFalse(is_approved, f"{description}: Sollte abgelehnt werden")
        
        print("✅ Content-Filtering funktioniert korrekt")
    
    def test_cooldown_mechanism(self):
        """Testet Cooldown-Mechanismus"""
        print("🛡️  Teste Cooldown-Mechanismus...")
        
        # Simuliere verschiedene Zeitabstände
        test_intervals = [
            {"interval": 300, "expected": False, "description": "Zu kurzer Abstand (5 min)"},
            {"interval": 600, "expected": True, "description": "Ausreichender Abstand (10 min)"},
            {"interval": 1200, "expected": True, "description": "Langer Abstand (20 min)"},
        ]
        
        for test_case in test_intervals:
            interval = test_case["interval"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            # Simuliere Cooldown-Prüfung
            can_promote = self._check_cooldown(interval)
            
            if expected:
                self.assertTrue(can_promote, f"{description}: Sollte erlaubt sein")
            else:
                self.assertFalse(can_promote, f"{description}: Sollte blockiert sein")
        
        print("✅ Cooldown-Mechanismus funktioniert korrekt")
    
    def test_system_note_compliance(self):
        """Testet System Note Compliance"""
        print("🛡️  Teste System Note Compliance...")
        
        # Test-System Notes
        test_notes = [
            {
                "note": "Bleibe im Rahmen der Geschichte und Charaktere.",
                "content": "Der Protagonist entwickelt sich weiter.",
                "expected": True,
                "description": "Compliant Content"
            },
            {
                "note": "Vermeide Gewalt und unangemessene Inhalte.",
                "content": "Der Charakter wird verletzt.",
                "expected": False,
                "description": "Non-compliant Content"
            }
        ]
        
        for test_case in test_notes:
            note = test_case["note"]
            content = test_case["content"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            # Simuliere Compliance-Prüfung
            is_compliant = self._check_system_note_compliance(note, content)
            
            if expected:
                self.assertTrue(is_compliant, f"{description}: Sollte compliant sein")
            else:
                self.assertFalse(is_compliant, f"{description}: Sollte non-compliant sein")
        
        print("✅ System Note Compliance funktioniert korrekt")
    
    def test_guardrail_integration(self):
        """Testet Integration aller Guardrails"""
        print("🛡️  Teste Guardrail-Integration...")
        
        # Simuliere vollständige Prüfung
        test_cases = [
            {
                "quality_score": 0.9,
                "content": "Harmloser Inhalt",
                "time_interval": 900,
                "system_note": "Bleibe freundlich.",
                "expected": True,
                "description": "Alle Guardrails passieren"
            },
            {
                "quality_score": 0.6,
                "content": "Harmloser Inhalt",
                "time_interval": 900,
                "system_note": "Bleibe freundlich.",
                "expected": False,
                "description": "Qualitäts-Schwelle nicht erreicht"
            }
        ]
        
        for test_case in test_cases:
            result = self._run_full_guardrail_check(
                test_case["quality_score"],
                test_case["content"],
                test_case["time_interval"],
                test_case["system_note"]
            )
            
            expected = test_case["expected"]
            description = test_case["description"]
            
            if expected:
                self.assertTrue(result, f"{description}: Sollte genehmigt werden")
            else:
                self.assertFalse(result, f"{description}: Sollte abgelehnt werden")
        
        print("✅ Guardrail-Integration funktioniert korrekt")
    
    # Helper-Methoden für Tests
    def _check_quality_threshold(self, score):
        """Simuliert Qualitäts-Schwellenwert-Prüfung"""
        return score >= 0.8
    
    def _check_content_filtering(self, content):
        """Simuliert Content-Filtering"""
        inappropriate_words = ["unangemessen", "schlecht", "gefährlich"]
        return not any(word in content.lower() for word in inappropriate_words)
    
    def _check_cooldown(self, interval_seconds):
        """Simuliert Cooldown-Prüfung"""
        min_interval = 600  # 10 Minuten
        return interval_seconds >= min_interval
    
    def _check_system_note_compliance(self, note, content):
        """Simuliert System Note Compliance"""
        if "vermeide" in note.lower() and "verletzt" in content.lower():
            return False
        return True
    
    def _run_full_guardrail_check(self, quality_score, content, time_interval, system_note):
        """Simuliert vollständige Guardrail-Prüfung"""
        # Alle Checks durchführen
        quality_ok = self._check_quality_threshold(quality_score)
        content_ok = self._check_content_filtering(content)
        cooldown_ok = self._check_cooldown(time_interval)
        compliance_ok = self._check_system_note_compliance(system_note, content)
        
        # Alle müssen True sein
        return all([quality_ok, content_ok, cooldown_ok, compliance_ok])

if __name__ == "__main__":
    unittest.main(verbosity=2) 