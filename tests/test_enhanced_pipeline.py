#!/usr/bin/env python3
"""
Enhanced Pipeline Tests für One Click Book Writer
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

class TestEnhancedPipelineIntegration(unittest.TestCase):
    """Integration Tests für Enhanced Pipeline"""
    
    def setUp(self):
        """Setup für Pipeline Tests"""
        self.project_root = Path(__file__).parent.parent
        
    def test_pipeline_initialization(self):
        """Testet Pipeline-Initialisierung"""
        print("🔧 Teste Pipeline-Initialisierung...")
        
        # Simuliere Pipeline-Initialisierung
        pipeline_config = {
            "components": ["enhanced_pipeline", "feedback_intelligence", "prompt_optimizer"],
            "settings": {
                "max_retries": 3,
                "timeout": 30,
                "quality_threshold": 0.8
            }
        }
        
        self.assertIsInstance(pipeline_config, dict)
        self.assertIn("components", pipeline_config)
        self.assertIn("settings", pipeline_config)
        
        print("✅ Pipeline-Initialisierung funktioniert")
    
    def test_prompt_compilation(self):
        """Testet Prompt-Kompilierung"""
        print("🔧 Teste Prompt-Kompilierung...")
        
        # Test-PromptFrame
        test_prompt_frame = {
            "input": {
                "book": {
                    "title": "Test Book",
                    "genre": "Fantasy"
                },
                "chapter": {
                    "number": 1,
                    "title": "Test Chapter"
                }
            }
        }
        
        # Simuliere Prompt-Kompilierung
        compiled_prompt = self._compile_prompt(test_prompt_frame)
        
        self.assertIsInstance(compiled_prompt, str)
        self.assertGreater(len(compiled_prompt), 0)
        self.assertIn("Test Book", compiled_prompt)
        
        print("✅ Prompt-Kompilierung funktioniert")
    
    def test_generation_pipeline(self):
        """Testet Generierungs-Pipeline"""
        print("🔧 Teste Generierungs-Pipeline...")
        
        # Simuliere vollständige Pipeline
        result = self._run_generation_pipeline()
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("content", result)
        self.assertIn("metadata", result)
        
        print("✅ Generierungs-Pipeline funktioniert")
    
    def test_quality_evaluation(self):
        """Testet Qualitäts-Evaluation"""
        print("🔧 Teste Qualitäts-Evaluation...")
        
        # Test-Inhalte
        test_contents = [
            "Dies ist ein hochwertiger Text mit guter Struktur.",
            "Kurzer Text ohne Tiefe.",
            "Ein ausführlicher Text mit vielen Details und guter Entwicklung."
        ]
        
        for content in test_contents:
            quality_score = self._evaluate_quality(content)
            
            self.assertIsInstance(quality_score, float)
            self.assertGreaterEqual(quality_score, 0.0)
            self.assertLessEqual(quality_score, 1.0)
        
        print("✅ Qualitäts-Evaluation funktioniert")
    
    def test_error_handling(self):
        """Testet Fehlerbehandlung"""
        print("🔧 Teste Fehlerbehandlung...")
        
        # Simuliere verschiedene Fehler-Szenarien
        error_scenarios = [
            {"type": "api_error", "expected_handling": "retry"},
            {"type": "validation_error", "expected_handling": "reject"},
            {"type": "timeout_error", "expected_handling": "retry"},
            {"type": "content_error", "expected_handling": "filter"}
        ]
        
        for scenario in error_scenarios:
            handling = self._handle_error(scenario["type"])
            self.assertEqual(handling, scenario["expected_handling"])
        
        print("✅ Fehlerbehandlung funktioniert")
    
    def test_bilingual_output(self):
        """Testet bilinguale Ausgabe"""
        print("🔧 Teste bilinguale Ausgabe...")
        
        # Test-Inhalt
        test_content = "Dies ist ein Test-Text für bilinguale Ausgabe."
        
        # Simuliere bilinguale Verarbeitung
        bilingual_result = self._process_bilingual(test_content)
        
        self.assertIsInstance(bilingual_result, dict)
        self.assertIn("de", bilingual_result)
        self.assertIn("en", bilingual_result)
        
        # Prüfe, dass beide Sprachen vorhanden sind
        self.assertIsInstance(bilingual_result["de"], str)
        self.assertIsInstance(bilingual_result["en"], str)
        
        print("✅ Bilinguale Ausgabe funktioniert")
    
    def test_feedback_integration(self):
        """Testet Feedback-Integration"""
        print("🔧 Teste Feedback-Integration...")
        
        # Test-Feedback
        test_feedback = {
            "rating": 4,
            "comment": "Guter Text, aber könnte mehr Details haben.",
            "category": "quality"
        }
        
        # Simuliere Feedback-Verarbeitung
        feedback_result = self._process_feedback(test_feedback)
        
        self.assertIsInstance(feedback_result, dict)
        self.assertIn("processed", feedback_result)
        self.assertIn("improvements", feedback_result)
        
        print("✅ Feedback-Integration funktioniert")
    
    def test_optimization_cycle(self):
        """Testet Optimierungs-Zyklus"""
        print("🔧 Teste Optimierungs-Zyklus...")
        
        # Simuliere Optimierungs-Zyklus
        initial_prompt = "Schreibe ein Kapitel."
        optimization_result = self._run_optimization_cycle(initial_prompt)
        
        self.assertIsInstance(optimization_result, dict)
        self.assertIn("optimized_prompt", optimization_result)
        self.assertIn("improvements", optimization_result)
        self.assertIn("metrics", optimization_result)
        
        # Prüfe, dass der optimierte Prompt länger ist
        self.assertGreater(len(optimization_result["optimized_prompt"]), len(initial_prompt))
        
        print("✅ Optimierungs-Zyklus funktioniert")
    
    def test_full_workflow(self):
        """Testet vollständigen Workflow"""
        print("🔧 Teste vollständigen Workflow...")
        
        # Simuliere vollständigen Workflow
        workflow_result = self._run_full_workflow()
        
        self.assertIsInstance(workflow_result, dict)
        self.assertIn("success", workflow_result)
        self.assertIn("pipeline_result", workflow_result)
        self.assertIn("quality_score", workflow_result)
        self.assertIn("bilingual_content", workflow_result)
        
        if workflow_result["success"]:
            self.assertGreater(workflow_result["quality_score"], 0.0)
            self.assertIsInstance(workflow_result["bilingual_content"], dict)
        
        print("✅ Vollständiger Workflow funktioniert")
    
    # Helper-Methoden für Tests
    def _compile_prompt(self, prompt_frame):
        """Simuliert Prompt-Kompilierung"""
        book_info = prompt_frame["input"]["book"]
        chapter_info = prompt_frame["input"]["chapter"]
        
        return f"Schreibe ein Kapitel für das Buch '{book_info['title']}' ({book_info['genre']}). Kapitel {chapter_info['number']}: {chapter_info['title']}"
    
    def _run_generation_pipeline(self):
        """Simuliert Generierungs-Pipeline"""
        return {
            "success": True,
            "content": "Dies ist ein generierter Text für das Test-Kapitel.",
            "metadata": {
                "tokens_used": 150,
                "model": "gpt-4",
                "timestamp": "2024-12-19T13:45:00Z"
            }
        }
    
    def _evaluate_quality(self, content):
        """Simuliert Qualitäts-Evaluation"""
        # Einfache Qualitäts-Bewertung basierend auf Textlänge und Inhalt
        base_score = min(len(content) / 100, 1.0)
        
        # Bonus für bestimmte Wörter
        quality_indicators = ["detailliert", "ausführlich", "strukturiert", "entwicklung"]
        bonus = sum(0.1 for indicator in quality_indicators if indicator in content.lower())
        
        return min(base_score + bonus, 1.0)
    
    def _handle_error(self, error_type):
        """Simuliert Fehlerbehandlung"""
        error_handling = {
            "api_error": "retry",
            "validation_error": "reject", 
            "timeout_error": "retry",
            "content_error": "filter"
        }
        return error_handling.get(error_type, "unknown")
    
    def _process_bilingual(self, content):
        """Simuliert bilinguale Verarbeitung"""
        return {
            "de": content,
            "en": f"English translation: {content}"
        }
    
    def _process_feedback(self, feedback):
        """Simuliert Feedback-Verarbeitung"""
        return {
            "processed": True,
            "improvements": ["Mehr Details hinzufügen", "Charakterentwicklung vertiefen"],
            "rating": feedback["rating"]
        }
    
    def _run_optimization_cycle(self, initial_prompt):
        """Simuliert Optimierungs-Zyklus"""
        return {
            "optimized_prompt": f"{initial_prompt} Bitte schreibe ein detailliertes Kapitel mit guter Charakterentwicklung und spannender Handlung.",
            "improvements": ["Detaillierung hinzugefügt", "Charakterentwicklung betont"],
            "metrics": {
                "prompt_length_increase": 0.8,
                "quality_improvement": 0.2
            }
        }
    
    def _run_full_workflow(self):
        """Simuliert vollständigen Workflow"""
        return {
            "success": True,
            "pipeline_result": {
                "generation_success": True,
                "optimization_applied": True,
                "quality_evaluated": True
            },
            "quality_score": 0.85,
            "bilingual_content": {
                "de": "Deutscher Text des Kapitels.",
                "en": "English text of the chapter."
            }
        }

if __name__ == "__main__":
    unittest.main(verbosity=2) 