#!/usr/bin/env python3
"""
Umfassende Tests für Prompt Optimizer - Coverage-Verbesserung
Ziel: Coverage von 24% auf mindestens 50% erhöhen
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import time
from typing import List, Dict, Any, Optional

from core.prompt_optimizer import PromptOptimizer
from core.architecture import (
    PromptTemplate, PromptFrame, GenerationResult, EvaluationResult,
    OptimizationResult, ABTestResult, Layer, LayerType, ComponentType
)


class TestPromptOptimizerComprehensive(unittest.TestCase):
    """Umfassende Tests für PromptOptimizer - Coverage-Verbesserung"""
    
    def setUp(self):
        """Setup für umfassende Tests"""
        # Mock die externen Abhängigkeiten
        with patch('core.prompt_optimizer.ClaudeAdapter') as mock_claude, \
             patch('core.prompt_optimizer.OpenAIAdapter') as mock_openai:
            
            self.mock_claude = mock_claude.return_value
            self.mock_openai = mock_openai.return_value
            
            self.optimizer = PromptOptimizer()
        
        # Test-PromptTemplate
        self.template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="Test template for children fantasy",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "Write a children's fantasy story", 1.0),
                Layer(LayerType.GENRE, "fantasy", 1.0),
                Layer(LayerType.TARGET_AUDIENCE, "children", 1.0)
            ]
        )
        
        # Test-PromptFrame
        self.prompt_frame = {
            "age_group": "children",
            "genre": "fantasy",
            "emotion": "joy",
            "language": "de",
            "target_audience": "early_reader"
        }

    # ===== TESTS FÜR OPTIMIZE_PROMPT_WITH_CLAUDE =====
    
    def test_optimize_prompt_with_claude_success(self):
        """Test erfolgreiche Claude-Optimierung"""
        # Mock Claude-Response
        claude_response = """
OPTIMIERTER PROMPT:
[ÄNDERUNG: Verbesserte emotionale Sprache]
Write a magical children's fantasy story that fills young hearts with joy and wonder.

[ÄNDERUNG: Hinzugefügte Charakterbeschreibungen]
Create lovable characters that children can easily relate to and root for.

[ÄNDERUNG: Vereinfachte Wortwahl]
Use simple, clear language that early readers can understand.
"""
        
        self.mock_claude.generate_text.return_value = claude_response
        
        # Mock OpenAI-Tests
        self.mock_openai.generate_text.side_effect = [
            "Test story 1",  # Raw prompt test
            "Test story 2"   # Optimized prompt test
        ]
        
        # Führe Optimierung aus
        result = self.optimizer.optimize_prompt_with_claude(
            self.template, self.prompt_frame, "emotional_depth"
        )
        
        # Assertions
        self.assertIsInstance(result, OptimizationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.optimization_focus, "emotional_depth")
        self.assertIn("prompt_diff", result.prompt_diff)
        self.assertIn("raw_result", result.metadata)
        self.assertIn("optimized_result", result.metadata)
        
        # Überprüfe Claude-Aufruf
        self.mock_claude.generate_text.assert_called_once()
        call_args = self.mock_claude.generate_text.call_args[0][0]
        self.assertIn("OPTIMIERE DIESEN PROMPT", call_args)
        self.assertIn("emotional_depth", call_args)
    
    def test_optimize_prompt_with_claude_failure(self):
        """Test Claude-Optimierung mit Fehler"""
        # Mock Claude-Fehler
        self.mock_claude.generate_text.side_effect = Exception("Claude API error")
        
        # Führe Optimierung aus
        result = self.optimizer.optimize_prompt_with_claude(
            self.template, self.prompt_frame
        )
        
        # Assertions
        self.assertIsInstance(result, OptimizationResult)
        self.assertFalse(result.success)
        self.assertIn("error", result.metadata)
    
    def test_optimize_prompt_with_claude_no_focus(self):
        """Test Claude-Optimierung ohne spezifischen Fokus"""
        claude_response = """
OPTIMIERTER PROMPT:
[ÄNDERUNG: Allgemeine Verbesserung]
Write a children's fantasy story that is engaging and age-appropriate.
"""
        
        self.mock_claude.generate_text.return_value = claude_response
        self.mock_openai.generate_text.side_effect = ["Test 1", "Test 2"]
        
        result = self.optimizer.optimize_prompt_with_claude(
            self.template, self.prompt_frame
        )
        
        self.assertIsInstance(result, OptimizationResult)
        self.assertEqual(result.optimization_focus, "general")
    
    # ===== TESTS FÜR ENSEMBLE-METHODEN =====
    
    def test_create_prompt_ensemble(self):
        """Test Erstellung eines Prompt-Ensembles"""
        variations = 3
        variation_focus = ["emotional_depth", "readability", "engagement"]
        
        result = self.optimizer.create_prompt_ensemble(
            self.template, variations, variation_focus
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), variations)
        
        for template in result:
            self.assertIsInstance(template, PromptTemplate)
            self.assertIn("variation", template.template_id)
    
    def test_create_prompt_ensemble_default_focus(self):
        """Test Ensemble-Erstellung mit Standard-Fokus"""
        result = self.optimizer.create_prompt_ensemble(self.template, 2)
        
        self.assertEqual(len(result), 2)
        for template in result:
            self.assertIsInstance(template, PromptTemplate)
    
    def test_rank_prompt_ensemble(self):
        """Test Ranking eines Prompt-Ensembles"""
        ensemble = [
            PromptTemplate(template_id="t1", name="Template 1", description="", layers=[]),
            PromptTemplate(template_id="t2", name="Template 2", description="", layers=[]),
            PromptTemplate(template_id="t3", name="Template 3", description="", layers=[])
        ]
        
        # Mock OpenAI für Tests
        self.mock_openai.generate_text.return_value = "Test story"
        
        result = self.optimizer.rank_prompt_ensemble(ensemble, self.prompt_frame)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(ensemble))
        
        for template, score in result:
            self.assertIsInstance(template, PromptTemplate)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_create_hybrid_prompt(self):
        """Test Erstellung eines Hybrid-Prompts"""
        top_templates = [
            (PromptTemplate(template_id="t1", name="Template 1", description="", layers=[]), 0.9),
            (PromptTemplate(template_id="t2", name="Template 2", description="", layers=[]), 0.8),
            (PromptTemplate(template_id="t3", name="Template 3", description="", layers=[]), 0.7)
        ]
        
        result = self.optimizer.create_hybrid_prompt(top_templates, max_templates=2)
        
        self.assertIsInstance(result, PromptTemplate)
        self.assertIn("hybrid", result.template_id)
        self.assertIn("Template 1", result.name)
        self.assertIn("Template 2", result.name)
    
    # ===== TESTS FÜR HISTORIE-METHODEN =====
    
    def test_get_optimization_history(self):
        """Test Abruf der Optimierungs-Historie"""
        # Füge einige Test-Optimierungen hinzu
        test_result = OptimizationResult(
            original_prompt_hash="hash1",
            optimized_prompt_hash="hash2",
            quality_score_delta=0.1,
            prompt_diff={"changes": ["test"]},
            optimization_focus="test",
            success=True,
            metadata={}
        )
        
        self.optimizer.optimization_history = [test_result]
        
        history = self.optimizer.get_optimization_history()
        
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], test_result)
    
    def test_get_best_optimizations(self):
        """Test Abruf der besten Optimierungen"""
        # Erstelle Test-Optimierungen mit verschiedenen Verbesserungen
        test_results = [
            OptimizationResult(
                original_prompt_hash="hash1",
                optimized_prompt_hash="hash2",
                quality_score_delta=0.05,
                prompt_diff={"changes": ["small"]},
                optimization_focus="test",
                success=True,
                metadata={}
            ),
            OptimizationResult(
                original_prompt_hash="hash3",
                optimized_prompt_hash="hash4",
                quality_score_delta=0.15,
                prompt_diff={"changes": ["large"]},
                optimization_focus="test",
                success=True,
                metadata={}
            ),
            OptimizationResult(
                original_prompt_hash="hash5",
                optimized_prompt_hash="hash6",
                quality_score_delta=0.25,
                prompt_diff={"changes": ["largest"]},
                optimization_focus="test",
                success=True,
                metadata={}
            )
        ]
        
        self.optimizer.optimization_history = test_results
        
        # Test mit Mindestverbesserung von 0.1
        best = self.optimizer.get_best_optimizations(min_improvement=0.1)
        
        self.assertEqual(len(best), 2)  # Nur die mit delta >= 0.1
        self.assertEqual(best[0].quality_score_delta, 0.25)  # Sortiert nach delta
        self.assertEqual(best[1].quality_score_delta, 0.15)
    
    # ===== TESTS FÜR HILFSMETHODEN =====
    
    def test_generate_raw_prompt(self):
        """Test Generierung des Roh-Prompts"""
        raw_prompt = self.optimizer._generate_raw_prompt(self.template)
        
        self.assertIsInstance(raw_prompt, str)
        self.assertIn("Write a children's fantasy story", raw_prompt)
        self.assertIn("fantasy", raw_prompt)
        self.assertIn("children", raw_prompt)
    
    def test_create_optimization_instruction(self):
        """Test Erstellung der Optimierungs-Instruktion"""
        instruction = self.optimizer._create_optimization_instruction(
            self.prompt_frame, "emotional_depth"
        )
        
        self.assertIsInstance(instruction, str)
        self.assertIn("emotional_depth", instruction)
        self.assertIn("children", instruction)
        self.assertIn("fantasy", instruction)
    
    def test_create_optimization_instruction_no_focus(self):
        """Test Optimierungs-Instruktion ohne Fokus"""
        instruction = self.optimizer._create_optimization_instruction(
            self.prompt_frame, None
        )
        
        self.assertIsInstance(instruction, str)
        self.assertIn("allgemeine Verbesserung", instruction)
    
    def test_extract_optimized_prompt(self):
        """Test Extraktion des optimierten Prompts"""
        claude_response = """
OPTIMIERTER PROMPT:
Write a magical story for children.

[ÄNDERUNG: Verbesserte Sprache]
Use simple words that children understand.
"""
        
        extracted = self.optimizer._extract_optimized_prompt(claude_response)
        
        self.assertIsInstance(extracted, str)
        self.assertIn("Write a magical story", extracted)
        self.assertIn("Use simple words", extracted)
    
    def test_generate_prompt_diff(self):
        """Test Generierung des Prompt-Diffs"""
        raw_prompt = "Write a simple story."
        optimized_prompt = "Write a magical story with simple words."
        
        diff = self.optimizer._generate_prompt_diff(raw_prompt, optimized_prompt)
        
        self.assertIsInstance(diff, dict)
        self.assertIn("changes", diff)
        self.assertIn("word_changes", diff)
        self.assertIn("structural_changes", diff)
        self.assertIn("change_percentage", diff)
    
    def test_analyze_word_changes(self):
        """Test Analyse der Wortänderungen"""
        raw_prompt = "Write a simple story for children."
        optimized_prompt = "Write a magical story for young readers."
        
        changes = self.optimizer._analyze_word_changes(raw_prompt, optimized_prompt)
        
        self.assertIsInstance(changes, dict)
        self.assertIn("added_words", changes)
        self.assertIn("removed_words", changes)
        self.assertIn("modified_words", changes)
    
    def test_analyze_structural_changes(self):
        """Test Analyse der Strukturänderungen"""
        raw_prompt = "Write a story. Make it simple."
        optimized_prompt = "Write a magical story. Make it simple and engaging."
        
        changes = self.optimizer._analyze_structural_changes(raw_prompt, optimized_prompt)
        
        self.assertIsInstance(changes, dict)
        self.assertIn("sentence_changes", changes)
        self.assertIn("paragraph_changes", changes)
    
    def test_calculate_change_percentage(self):
        """Test Berechnung der Änderungs-Prozentzahl"""
        raw_prompt = "Write a story."
        optimized_prompt = "Write a magical story with characters."
        
        percentage = self.optimizer._calculate_change_percentage(raw_prompt, optimized_prompt)
        
        self.assertIsInstance(percentage, float)
        self.assertGreater(percentage, 0.0)
        self.assertLessEqual(percentage, 100.0)
    
    def test_test_prompt(self):
        """Test Prompt-Testung"""
        prompt = "Write a children's story."
        
        # Mock OpenAI
        self.mock_openai.generate_text.return_value = "Once upon a time..."
        
        result = self.optimizer._test_prompt(prompt, self.prompt_frame)
        
        self.assertIsInstance(result, dict)
        self.assertIn("quality_score", result)
        self.assertIn("generation_time", result)
        self.assertIn("word_count", result)
    
    def test_test_prompt_failure(self):
        """Test Prompt-Testung mit Fehler"""
        prompt = "Write a children's story."
        
        # Mock OpenAI-Fehler
        self.mock_openai.generate_text.side_effect = Exception("API error")
        
        result = self.optimizer._test_prompt(prompt, self.prompt_frame)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("quality_score", 0), 0)
        self.assertIn("error", result)
    
    # ===== TESTS FÜR TEMPLATE-VARIATIONEN =====
    
    def test_create_template_variation(self):
        """Test Erstellung einer Template-Variation"""
        variation = self.optimizer._create_template_variation(
            self.template, "emotional_depth", 1
        )
        
        self.assertIsInstance(variation, PromptTemplate)
        self.assertIn("variation", variation.template_id)
        self.assertIn("emotional_depth", variation.name)
    
    def test_adjust_layer_for_focus(self):
        """Test Anpassung einer Layer für einen Fokus"""
        layer = Layer(LayerType.SYSTEM_NOTE, "Write a story", 1.0)
        
        adjusted = self.optimizer._adjust_layer_for_focus(layer, "emotional_depth")
        
        self.assertIsInstance(adjusted, str)
        self.assertIn("emotional", adjusted.lower())
    
    def test_adjust_layer_for_focus_readability(self):
        """Test Layer-Anpassung für Readability-Fokus"""
        layer = Layer(LayerType.SYSTEM_NOTE, "Write a complex story", 1.0)
        
        adjusted = self.optimizer._adjust_layer_for_focus(layer, "readability")
        
        self.assertIsInstance(adjusted, str)
        self.assertIn("simple", adjusted.lower())


if __name__ == '__main__':
    unittest.main() 