#!/usr/bin/env python3
"""
Umfassende Tests für Enhanced Pipeline - Coverage-Verbesserung
Ziel: Coverage von 22% auf mindestens 60% erhöhen
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import json
import time
import hashlib
from typing import List, Optional

from core.enhanced_pipeline import EnhancedPipeline, EnhancedPipelineComponent
from core.architecture import (
    PromptFrame, PromptTemplate, GenerationResult, EvaluationResult,
    OptimizationResult, ABTestResult, PipelineResult, FeedbackEntry,
    Layer, LayerType, ComponentType
)


class TestEnhancedPipelineComprehensive(unittest.TestCase):
    """Umfassende Tests für EnhancedPipeline - Coverage-Verbesserung"""
    
    def setUp(self):
        """Setup für umfassende Tests"""
        # Mock alle externen Komponenten
        with patch('core.enhanced_pipeline.LayeredCompositionEngine'), \
             patch('core.enhanced_pipeline.PromptOptimizer'), \
             patch('core.enhanced_pipeline.RobustnessManager'), \
             patch('core.enhanced_pipeline.TargetGroupEvaluator'), \
             patch('core.enhanced_pipeline.UserFeedbackSystem'), \
             patch('core.enhanced_pipeline.OpenAIAdapter'), \
             patch('core.enhanced_pipeline.ARCHITECTURE_REGISTRY'):
            
            self.pipeline = EnhancedPipeline()
        
        # Mock-Komponenten mit detaillierten Responses
        self.pipeline.compiler = Mock()
        self.pipeline.optimizer = Mock()
        self.pipeline.robustness_manager = Mock()
        self.pipeline.evaluator = Mock()
        self.pipeline.feedback_system = Mock()
        self.pipeline.generator = Mock()
        
        # Test-PromptFrame
        self.prompt_frame = PromptFrame(
            age_group="children",
            genre="fantasy",
            emotion="joy",
            language="de",
            target_audience="early_reader"
        )
        
        # Test-Template
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
        
        # Test-GenerationResult
        self.generation_result = GenerationResult(
            success=True,
            german_text="Es war einmal ein kleiner Drache...",
            english_text="Once upon a time there was a little dragon...",
            prompt_hash="test_hash",
            template_hash="template_hash",
            generation_time=1.5,
            word_count=100
        )
        
        # Test-EvaluationResult
        self.evaluation_result = EvaluationResult(
            overall_score=0.85,
            readability_score=0.9,
            age_appropriateness=0.95,
            genre_compliance=0.8,
            emotional_depth=0.7,
            engagement_score=0.75
        )
        
        # Test-OptimizationResult
        self.optimization_result = OptimizationResult(
            original_prompt_hash="original_hash",
            optimized_prompt_hash="optimized_hash",
            quality_score_delta=0.1,
            prompt_diff={"changes": ["Added more descriptive language"]},
            optimization_focus="emotional_depth",
            success=True,
            metadata={"cost_savings": 0.05}
        )
        
        # Test-ABTestResult
        self.ab_test_result = ABTestResult(
            test_id="test_ab_1",
            segment="optimized",
            original_result=self.generation_result,
            optimized_result=self.generation_result,
            comparison={"score_delta": 0.07},
            significant_improvement=True,
            recommendation="Use optimized version"
        )

    # ===== TESTS FÜR FEHLENDE CODE-PFADE =====
    
    def test_run_enhanced_pipeline_with_feedback_collection_disabled(self):
        """Test Pipeline ohne Feedback-Sammlung"""
        # Setup Mocks
        self.pipeline.compiler.compile_template.return_value = self.template
        self.pipeline.compiler.generate_prompt.return_value = "Test prompt"
        self.pipeline.compiler.calculate_template_hash.return_value = "hash123"
        self.pipeline.generator.generate_text.return_value = self.generation_result
        self.pipeline.evaluator.evaluate_text.return_value = self.evaluation_result
        
        # Führe Pipeline aus ohne Feedback-Sammlung
        result = self.pipeline.run_enhanced_pipeline(
            self.prompt_frame,
            enable_optimization=False,
            enable_ab_testing=False,
            enable_feedback_collection=False
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.assertIsNone(result.optimization_result)
        self.assertIsNone(result.ab_test_result)
        self.assertEqual(len(result.feedback_entries), 0)
        
        # Prüfe dass Feedback-System nicht aufgerufen wurde
        self.pipeline.feedback_system.collect_feedback.assert_not_called()

    def test_run_enhanced_pipeline_with_optimization_failure(self):
        """Test Pipeline mit fehlgeschlagener Optimierung"""
        # Setup Mocks
        self.pipeline.compiler.compile_template.return_value = self.template
        self.pipeline.compiler.generate_prompt.return_value = "Test prompt"
        self.pipeline.compiler.calculate_template_hash.return_value = "hash123"
        self.pipeline.generator.generate_text.return_value = self.generation_result
        self.pipeline.evaluator.evaluate_text.return_value = self.evaluation_result
        
        # Mock fehlgeschlagene Optimierung
        failed_optimization = OptimizationResult(
            original_prompt_hash="original_hash",
            optimized_prompt_hash="",
            quality_score_delta=0.0,
            prompt_diff={},
            optimization_focus="",
            success=False,
            metadata={"error_message": "Optimization failed"}
        )
        self.pipeline.optimizer.optimize_prompt.return_value = failed_optimization
        
        # Führe Pipeline aus
        result = self.pipeline.run_enhanced_pipeline(
            self.prompt_frame,
            enable_optimization=True
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.assertFalse(result.optimization_result.success)
        self.assertEqual(result.optimization_result.metadata["error_message"], "Optimization failed")

    def test_run_enhanced_pipeline_with_ab_testing_failure(self):
        """Test Pipeline mit fehlgeschlagenem A/B-Testing"""
        # Setup Mocks
        self.pipeline.compiler.compile_template.return_value = self.template
        self.pipeline.compiler.generate_prompt.return_value = "Test prompt"
        self.pipeline.compiler.calculate_template_hash.return_value = "hash123"
        self.pipeline.generator.generate_text.return_value = self.generation_result
        self.pipeline.evaluator.evaluate_text.return_value = self.evaluation_result
        self.pipeline.optimizer.optimize_prompt.return_value = self.optimization_result
        
        # Mock fehlgeschlagenes A/B-Testing
        failed_ab_test = ABTestResult(
            test_id="test_ab_failed",
            segment="original",
            original_result=self.generation_result,
            optimized_result=self.generation_result,
            comparison={"score_delta": -0.03},
            significant_improvement=False,
            recommendation="Keep original version",
            metadata={"error_message": "Insufficient sample size"}
        )
        self.pipeline.evaluator.run_ab_test.return_value = failed_ab_test
        
        # Führe Pipeline aus
        result = self.pipeline.run_enhanced_pipeline(
            self.prompt_frame,
            enable_optimization=True,
            enable_ab_testing=True
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.assertEqual(result.ab_test_result.segment, "original")
        self.assertEqual(result.ab_test_result.metadata["error_message"], "Insufficient sample size")

    def test_generate_with_retry_partial_failures(self):
        """Test Retry-Mechanismus mit teilweisen Fehlern"""
        # Mock verschiedene Generator-Responses
        success_result = GenerationResult(
            success=True,
            german_text="Erfolgreicher Text",
            english_text="Successful text",
            prompt_hash="hash123",
            template_hash="template_hash",
            generation_time=1.0,
            word_count=50
        )
        
        failure_result = GenerationResult(
            success=False,
            german_text="",
            english_text="",
            prompt_hash="hash123",
            template_hash="template_hash",
            generation_time=0.5,
            word_count=0,
            errors=["API timeout"]
        )
        
        # Mock sequentielle Responses: 2 Fehler, dann Erfolg
        self.pipeline.generator.generate_text.side_effect = [
            failure_result, failure_result, success_result
        ]
        
        # Führe Retry aus
        result = self.pipeline._generate_with_retry(
            "Test prompt", self.prompt_frame, self.template, max_retries=3
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.assertEqual(result.german_text, "Erfolgreicher Text")
        self.assertEqual(self.pipeline.generator.generate_text.call_count, 3)

    def test_generate_with_retry_with_robustness_manager(self):
        """Test Retry-Mechanismus mit RobustnessManager-Integration"""
        # Mock RobustnessManager
        self.pipeline.robustness_manager.should_retry.return_value = True
        self.pipeline.robustness_manager.get_retry_delay.return_value = 0.1
        
        # Mock Generator-Responses
        failure_result = GenerationResult(
            success=False,
            german_text="",
            english_text="",
            prompt_hash="hash123",
            template_hash="template_hash",
            generation_time=0.5,
            word_count=0,
            errors=["Rate limit exceeded"]
        )
        
        success_result = GenerationResult(
            success=True,
            german_text="Erfolgreicher Text nach Retry",
            english_text="Successful text after retry",
            prompt_hash="hash123",
            template_hash="template_hash",
            generation_time=1.0,
            word_count=50
        )
        
        self.pipeline.generator.generate_text.side_effect = [failure_result, success_result]
        
        # Führe Retry aus
        result = self.pipeline._generate_with_retry(
            "Test prompt", self.prompt_frame, self.template, max_retries=2
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.pipeline.robustness_manager.should_retry.assert_called_once()
        self.pipeline.robustness_manager.get_retry_delay.assert_called_once()

    def test_parse_bilingual_response_complex_format(self):
        """Test Parsing komplexer bilingualer Responses"""
        # Test verschiedene Response-Formate
        test_cases = [
            {
                "input": "DEUTSCH:\nEs war einmal ein Drache.\n\nENGLISH:\nOnce upon a time there was a dragon.",
                "expected_de": "Es war einmal ein Drache.",
                "expected_en": "Once upon a time there was a dragon."
            },
            {
                "input": "German: Ein Märchen\nEnglish: A fairy tale",
                "expected_de": "Ein Märchen",
                "expected_en": "A fairy tale"
            },
            {
                "input": "🇩🇪 Ein Abenteuer\n🇺🇸 An adventure",
                "expected_de": "Ein Abenteuer",
                "expected_en": "An adventure"
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(input=test_case["input"]):
                de_text, en_text = self.pipeline._parse_bilingual_response(test_case["input"])
                self.assertEqual(de_text.strip(), test_case["expected_de"])
                self.assertEqual(en_text.strip(), test_case["expected_en"])

    def test_parse_bilingual_response_fallback(self):
        """Test Parsing-Fallback für nicht-formatierte Responses"""
        # Test Response ohne klare Trennung
        response = "This is a mixed response with German and English content."
        de_text, en_text = self.pipeline._parse_bilingual_response(response)
        
        # Sollte Fallback-Verhalten zeigen
        self.assertIsInstance(de_text, str)
        self.assertIsInstance(en_text, str)

    def test_evaluate_generation_with_detailed_metrics(self):
        """Test Evaluation mit detaillierten Metriken"""
        # Mock detaillierte Evaluation
        detailed_evaluation = EvaluationResult(
            overall_score=0.92,
            readability_score=0.95,
            age_appropriateness=0.98,
            genre_compliance=0.88,
            emotional_depth=0.85,
            engagement_score=0.90
        )
        
        self.pipeline.evaluator.evaluate_text.return_value = detailed_evaluation
        
        # Führe Evaluation aus
        result = self.pipeline._evaluate_generation(self.generation_result, self.prompt_frame)
        
        # Verifikationen
        self.assertEqual(result.overall_score, 0.92)
        self.assertEqual(result.readability_score, 0.95)
        self.assertEqual(result.age_appropriateness, 0.98)

    def test_optimize_prompt_with_specific_focus(self):
        """Test Prompt-Optimierung mit spezifischem Fokus"""
        # Mock Evaluation mit niedrigem emotional_depth Score
        low_emotional_evaluation = EvaluationResult(
            overall_score=0.75,
            readability_score=0.8,
            age_appropriateness=0.9,
            genre_compliance=0.85,
            emotional_depth=0.3,  # Niedrig - sollte optimiert werden
            engagement_score=0.7
        )
        
        self.pipeline.evaluator.evaluate_text.return_value = low_emotional_evaluation
        
        # Mock Optimierung mit emotional_depth Fokus
        emotional_optimization = OptimizationResult(
            original_prompt_hash="original_hash",
            optimized_prompt_hash="optimized_hash",
            quality_score_delta=0.15,
            prompt_diff={"changes": ["Enhanced emotional language", "Added descriptive adjectives"]},
            optimization_focus="emotional_depth",
            success=True,
            metadata={"focus_area": "emotional_depth"}
        )
        
        self.pipeline.optimizer.optimize_prompt.return_value = emotional_optimization
        
        # Führe Optimierung aus
        result = self.pipeline._optimize_prompt(
            self.template, self.prompt_frame, low_emotional_evaluation
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.assertEqual(result.optimization_focus, "emotional_depth")
        self.assertIn("Enhanced emotional language", result.prompt_diff["changes"])

    def test_optimize_prompt_with_readability_focus(self):
        """Test Prompt-Optimierung mit Readability-Fokus"""
        # Mock Evaluation mit niedrigem readability Score
        low_readability_evaluation = EvaluationResult(
            overall_score=0.65,
            readability_score=0.4,  # Niedrig - sollte optimiert werden
            age_appropriateness=0.8,
            genre_compliance=0.7,
            emotional_depth=0.6,
            engagement_score=0.5
        )
        
        # Mock Optimierung mit readability Fokus
        readability_optimization = OptimizationResult(
            original_prompt_hash="original_hash",
            optimized_prompt_hash="optimized_hash",
            quality_score_delta=0.2,
            prompt_diff={"changes": ["Simplified sentence structure", "Reduced vocabulary complexity"]},
            optimization_focus="readability",
            success=True,
            metadata={"focus_area": "readability"}
        )
        
        self.pipeline.optimizer.optimize_prompt.return_value = readability_optimization
        
        # Führe Optimierung aus
        result = self.pipeline._optimize_prompt(
            self.template, self.prompt_frame, low_readability_evaluation
        )
        
        # Verifikationen
        self.assertTrue(result.success)
        self.assertEqual(result.optimization_focus, "readability")
        self.assertIn("Simplified sentence structure", result.prompt_diff["changes"])

    def test_determine_optimization_focus_all_areas(self):
        """Test Bestimmung des Optimierungsfokus für alle Bereiche"""
        test_cases = [
            {
                "evaluation": EvaluationResult(
                    overall_score=0.7,
                    readability_score=0.3,  # Niedrigster Score
                    age_appropriateness=0.8,
                    genre_compliance=0.7,
                    emotional_depth=0.6,
                    engagement_score=0.5
                ),
                "expected_focus": "readability"
            },
            {
                "evaluation": EvaluationResult(
                    overall_score=0.7,
                    readability_score=0.8,
                    age_appropriateness=0.3,  # Niedrigster Score
                    genre_compliance=0.7,
                    emotional_depth=0.6,
                    engagement_score=0.5
                ),
                "expected_focus": "age_appropriateness"
            },
            {
                "evaluation": EvaluationResult(
                    overall_score=0.7,
                    readability_score=0.8,
                    age_appropriateness=0.8,
                    genre_compliance=0.3,  # Niedrigster Score
                    emotional_depth=0.6,
                    engagement_score=0.5
                ),
                "expected_focus": "genre_compliance"
            },
            {
                "evaluation": EvaluationResult(
                    overall_score=0.7,
                    readability_score=0.8,
                    age_appropriateness=0.8,
                    genre_compliance=0.7,
                    emotional_depth=0.3,  # Niedrigster Score
                    engagement_score=0.5
                ),
                "expected_focus": "emotional_depth"
            },
            {
                "evaluation": EvaluationResult(
                    overall_score=0.7,
                    readability_score=0.8,
                    age_appropriateness=0.8,
                    genre_compliance=0.7,
                    emotional_depth=0.6,
                    engagement_score=0.3  # Niedrigster Score
                ),
                "expected_focus": "engagement"
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(expected_focus=test_case["expected_focus"]):
                focus = self.pipeline._determine_optimization_focus(test_case["evaluation"])
                self.assertEqual(focus, test_case["expected_focus"])

    def test_get_target_words_all_age_groups(self):
        """Test Target Words für alle Altersgruppen"""
        test_cases = [
            ("toddler", 50),
            ("preschool", 100),
            ("early_reader", 200),
            ("middle_reader", 400),
            ("young_adult", 800),
            ("adult", 1200),
            ("unknown_age", 400)  # Default
        ]
        
        for age_group, expected_words in test_cases:
            with self.subTest(age_group=age_group):
                target_words = self.pipeline._get_target_words(age_group)
                self.assertEqual(target_words, expected_words)

    def test_run_ab_test_with_detailed_comparison(self):
        """Test A/B-Testing mit detailliertem Vergleich"""
        # Mock detaillierte A/B-Test-Ergebnisse
        detailed_ab_test = ABTestResult(
            test_id="detailed_test",
            segment="optimized",
            original_result=self.generation_result,
            optimized_result=self.generation_result,
            comparison={
                "readability": 0.8,
                "engagement": 0.7,
                "emotional_depth": 0.6,
                "confidence_level": 0.95,
                "sample_size": 100
            },
            significant_improvement=True,
            recommendation="Use optimized version"
        )
        
        self.pipeline.evaluator.run_ab_test.return_value = detailed_ab_test
        
        # Führe A/B-Test aus
        result = self.pipeline._run_ab_test(
            self.generation_result, self.optimization_result, self.prompt_frame
        )
        
        # Verifikationen
        self.assertEqual(result.segment, "optimized")
        self.assertEqual(result.comparison["confidence_level"], 0.95)
        self.assertTrue(result.significant_improvement)
        self.assertEqual(result.comparison["readability"], 0.8)

    def test_run_ab_test_with_tie(self):
        """Test A/B-Testing mit Unentschieden"""
        # Mock A/B-Test mit Unentschieden
        tie_ab_test = ABTestResult(
            test_id="tie_test",
            segment="tie",
            original_result=self.generation_result,
            optimized_result=self.generation_result,
            comparison={"score_delta": 0.0},
            significant_improvement=False,
            recommendation="No clear winner"
        )
        
        self.pipeline.evaluator.run_ab_test.return_value = tie_ab_test
        
        # Führe A/B-Test aus
        result = self.pipeline._run_ab_test(
            self.generation_result, self.optimization_result, self.prompt_frame
        )
        
        # Verifikationen
        self.assertEqual(result.segment, "tie")
        self.assertFalse(result.significant_improvement)

    def test_create_template_from_hash(self):
        """Test Template-Erstellung aus Hash"""
        template_hash = "test_hash_123"
        
        # Mock Template-Erstellung
        created_template = PromptTemplate(
            template_id="hash_template",
            name="Template from Hash",
            description="Template created from hash",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "Generated template", 1.0)
            ]
        )
        
        self.pipeline.compiler.create_template_from_hash.return_value = created_template
        
        # Führe Template-Erstellung aus
        result = self.pipeline._create_template_from_hash(template_hash)
        
        # Verifikationen
        self.assertEqual(result.template_id, "hash_template")
        self.assertEqual(result.name, "Template from Hash")
        self.pipeline.compiler.create_template_from_hash.assert_called_once_with(template_hash)

    def test_collect_feedback_with_multiple_entries(self):
        """Test Feedback-Sammlung mit mehreren Einträgen"""
        # Mock Feedback-System mit mehreren Einträgen
        feedback_entries = [
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=4.0,
                user_rating=4,
                comment="Great story for children",
                language="de"
            ),
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=2.0,
                user_rating=2,
                comment="Too complex vocabulary",
                language="de"
            )
        ]
        
        self.pipeline.feedback_system.collect_feedback.return_value = feedback_entries
        
        # Führe Feedback-Sammlung aus
        result = self.pipeline._collect_feedback(
            self.generation_result, self.evaluation_result, self.prompt_frame
        )
        
        # Verifikationen
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].user_rating, 4)
        self.assertEqual(result[1].user_rating, 2)

    def test_collect_feedback_with_empty_response(self):
        """Test Feedback-Sammlung mit leerer Response"""
        # Mock leere Feedback-Response
        self.pipeline.feedback_system.collect_feedback.return_value = []
        
        # Führe Feedback-Sammlung aus
        result = self.pipeline._collect_feedback(
            self.generation_result, self.evaluation_result, self.prompt_frame
        )
        
        # Verifikationen
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, list)

    def test_check_compliance_all_scenarios(self):
        """Test Compliance-Check für alle Szenarien"""
        test_cases = [
            {
                "evaluation": EvaluationResult(
                    overall_score=0.95,
                    readability_score=0.9,
                    age_appropriateness=0.98,
                    genre_compliance=0.9,
                    emotional_depth=0.8,
                    engagement_score=0.85
                ),
                "expected_compliance": "compliant"
            },
            {
                "evaluation": EvaluationResult(
                    overall_score=0.4,
                    readability_score=0.3,
                    age_appropriateness=0.2,
                    genre_compliance=0.4,
                    emotional_depth=0.3,
                    engagement_score=0.2
                ),
                "expected_compliance": "non_compliant"
            },
            {
                "evaluation": EvaluationResult(
                    overall_score=0.7,
                    readability_score=0.6,
                    age_appropriateness=0.8,
                    genre_compliance=0.7,
                    emotional_depth=0.6,
                    engagement_score=0.5
                ),
                "expected_compliance": "needs_review"
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(expected_compliance=test_case["expected_compliance"]):
                compliance = self.pipeline._check_compliance(
                    self.generation_result, test_case["evaluation"], self.prompt_frame
                )
                self.assertEqual(compliance, test_case["expected_compliance"])

    def test_calculate_costs_with_all_components(self):
        """Test Kostenberechnung mit allen Komponenten"""
        # Mock Kosten für verschiedene Komponenten
        self.pipeline.generator.calculate_cost.return_value = 0.05
        self.pipeline.optimizer.calculate_cost.return_value = 0.02
        self.pipeline.evaluator.calculate_cost.return_value = 0.01
        
        # Führe Kostenberechnung aus
        total_cost = self.pipeline._calculate_costs(
            self.generation_result, self.optimization_result, self.ab_test_result
        )
        
        # Verifikationen
        self.assertEqual(total_cost, 0.08)  # 0.05 + 0.02 + 0.01
        self.pipeline.generator.calculate_cost.assert_called_once()
        self.pipeline.optimizer.calculate_cost.assert_called_once()
        self.pipeline.evaluator.calculate_cost.assert_called_once()

    def test_calculate_costs_without_optimization(self):
        """Test Kostenberechnung ohne Optimierung"""
        # Mock Kosten nur für Generator
        self.pipeline.generator.calculate_cost.return_value = 0.05
        
        # Führe Kostenberechnung aus ohne Optimierung
        total_cost = self.pipeline._calculate_costs(
            self.generation_result, None, None
        )
        
        # Verifikationen
        self.assertEqual(total_cost, 0.05)
        self.pipeline.generator.calculate_cost.assert_called_once()

    def test_update_pipeline_stats_comprehensive(self):
        """Test umfassende Pipeline-Statistik-Updates"""
        # Erstelle Pipeline-Result
        pipeline_result = PipelineResult(
            run_id="test_run",
            prompt_frame=self.prompt_frame,
            generation_result=self.generation_result,
            evaluation_result=self.evaluation_result,
            optimization_result=self.optimization_result,
            ab_test_result=self.ab_test_result,
            feedback_entries=[],
            compliance_status="compliant",
            execution_time=2.5,
            total_cost=0.08
        )
        
        # Initialisiere Pipeline-Statistiken
        self.pipeline.pipeline_stats = {
            "total_runs": 5,
            "successful_runs": 4,
            "failed_runs": 1,
            "average_execution_time": 2.0,
            "total_cost": 0.25
        }
        
        # Führe Update aus
        self.pipeline._update_pipeline_stats(pipeline_result)
        
        # Verifikationen
        self.assertEqual(self.pipeline.pipeline_stats["total_runs"], 6)
        self.assertEqual(self.pipeline.pipeline_stats["successful_runs"], 5)
        self.assertEqual(self.pipeline.pipeline_stats["failed_runs"], 1)
        self.assertAlmostEqual(self.pipeline.pipeline_stats["average_execution_time"], 2.25, places=2)
        self.assertEqual(self.pipeline.pipeline_stats["total_cost"], 0.33)

    def test_update_pipeline_stats_failed_run(self):
        """Test Pipeline-Statistik-Update für fehlgeschlagene Runs"""
        # Erstelle fehlgeschlagenes Pipeline-Result
        failed_result = PipelineResult(
            run_id="failed_run",
            prompt_frame=self.prompt_frame,
            generation_result=None,
            evaluation_result=None,
            optimization_result=None,
            ab_test_result=None,
            feedback_entries=[],
            compliance_status="failed",
            execution_time=1.0,
            total_cost=0.02
        )
        
        # Initialisiere Pipeline-Statistiken
        self.pipeline.pipeline_stats = {
            "total_runs": 3,
            "successful_runs": 3,
            "failed_runs": 0,
            "average_execution_time": 2.0,
            "total_cost": 0.15
        }
        
        # Führe Update aus
        self.pipeline._update_pipeline_stats(failed_result)
        
        # Verifikationen
        self.assertEqual(self.pipeline.pipeline_stats["total_runs"], 4)
        self.assertEqual(self.pipeline.pipeline_stats["successful_runs"], 3)
        self.assertEqual(self.pipeline.pipeline_stats["failed_runs"], 1)
        self.assertAlmostEqual(self.pipeline.pipeline_stats["average_execution_time"], 1.75, places=2)
        self.assertEqual(self.pipeline.pipeline_stats["total_cost"], 0.17)

    def test_get_pipeline_stats_detailed(self):
        """Test detaillierte Pipeline-Statistiken"""
        # Setze detaillierte Statistiken
        self.pipeline.pipeline_stats = {
            "total_runs": 10,
            "successful_runs": 8,
            "failed_runs": 2,
            "average_execution_time": 2.5,
            "total_cost": 0.45,
            "success_rate": 0.8,
            "average_cost_per_run": 0.045
        }
        
        # Hole Statistiken
        stats = self.pipeline.get_pipeline_stats()
        
        # Verifikationen
        self.assertEqual(stats["total_runs"], 10)
        self.assertEqual(stats["successful_runs"], 8)
        self.assertEqual(stats["failed_runs"], 2)
        self.assertEqual(stats["average_execution_time"], 2.5)
        self.assertEqual(stats["total_cost"], 0.45)
        self.assertEqual(stats["success_rate"], 0.8)
        self.assertEqual(stats["average_cost_per_run"], 0.045)

    def test_run_batch_pipeline_comprehensive(self):
        """Test umfassende Batch-Pipeline"""
        # Erstelle mehrere PromptFrames
        prompt_frames = [
            PromptFrame(age_group="children", genre="fantasy", emotion="joy", language="de"),
            PromptFrame(age_group="adult", genre="mystery", emotion="suspense", language="en"),
            PromptFrame(age_group="young_adult", genre="romance", emotion="love", language="de")
        ]
        
        # Mock erfolgreiche Pipeline-Results
        successful_results = [
            PipelineResult(
                run_id="batch_1",
                prompt_frame=prompt_frames[0],
                generation_result=self.generation_result,
                evaluation_result=self.evaluation_result,
                optimization_result=None,
                ab_test_result=None,
                feedback_entries=[],
                compliance_status="compliant",
                execution_time=2.0,
                total_cost=0.05
            ),
            PipelineResult(
                run_id="batch_2",
                prompt_frame=prompt_frames[1],
                generation_result=self.generation_result,
                evaluation_result=self.evaluation_result,
                optimization_result=self.optimization_result,
                ab_test_result=None,
                feedback_entries=[],
                compliance_status="compliant",
                execution_time=3.0,
                total_cost=0.08
            ),
            PipelineResult(
                run_id="batch_3",
                prompt_frame=prompt_frames[2],
                generation_result=None,
                evaluation_result=None,
                optimization_result=None,
                ab_test_result=None,
                feedback_entries=[],
                compliance_status="failed",
                execution_time=1.0,
                total_cost=0.02
            )
        ]
        
        # Mock run_enhanced_pipeline für jeden Frame
        self.pipeline.run_enhanced_pipeline.side_effect = successful_results
        
        # Führe Batch-Pipeline aus
        results = self.pipeline.run_batch_pipeline(prompt_frames)
        
        # Verifikationen
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].compliance_status == "compliant")
        self.assertTrue(results[1].compliance_status == "compliant")
        self.assertTrue(results[2].compliance_status == "failed")
        
        # Prüfe dass run_enhanced_pipeline für jeden Frame aufgerufen wurde
        self.assertEqual(self.pipeline.run_enhanced_pipeline.call_count, 3)

    def test_run_batch_pipeline_with_custom_options(self):
        """Test Batch-Pipeline mit benutzerdefinierten Optionen"""
        # Erstelle PromptFrames
        prompt_frames = [
            PromptFrame(age_group="children", genre="fantasy", emotion="joy", language="de"),
            PromptFrame(age_group="adult", genre="mystery", emotion="suspense", language="en")
        ]
        
        # Mock erfolgreiche Results
        successful_results = [
            PipelineResult(
                run_id="custom_1",
                prompt_frame=prompt_frames[0],
                generation_result=self.generation_result,
                evaluation_result=self.evaluation_result,
                feedback_entries=[],
                compliance_status="compliant",
                execution_time=2.0,
                total_cost=0.05
            ),
            PipelineResult(
                run_id="custom_2",
                prompt_frame=prompt_frames[1],
                generation_result=self.generation_result,
                evaluation_result=self.evaluation_result,
                feedback_entries=[],
                compliance_status="compliant",
                execution_time=2.5,
                total_cost=0.06
            )
        ]
        
        self.pipeline.run_enhanced_pipeline.side_effect = successful_results
        
        # Führe Batch-Pipeline mit benutzerdefinierten Optionen aus
        results = self.pipeline.run_batch_pipeline(
            prompt_frames,
            enable_optimization=True,
            enable_ab_testing=True,
            enable_feedback_collection=True,
            max_retries=5
        )
        
        # Verifikationen
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.compliance_status == "compliant" for result in results))
        
        # Prüfe dass run_enhanced_pipeline mit korrekten Optionen aufgerufen wurde
        expected_calls = [
            call(prompt_frames[0], enable_optimization=True, enable_ab_testing=True,
                 enable_feedback_collection=True, max_retries=5),
            call(prompt_frames[1], enable_optimization=True, enable_ab_testing=True,
                 enable_feedback_collection=True, max_retries=5)
        ]
        self.pipeline.run_enhanced_pipeline.assert_has_calls(expected_calls)


class TestEnhancedPipelineComponentComprehensive(unittest.TestCase):
    """Umfassende Tests für EnhancedPipelineComponent"""
    
    def setUp(self):
        """Setup für Component-Tests"""
        with patch('core.enhanced_pipeline.LayeredCompositionEngine'), \
             patch('core.enhanced_pipeline.PromptOptimizer'), \
             patch('core.enhanced_pipeline.RobustnessManager'), \
             patch('core.enhanced_pipeline.TargetGroupEvaluator'), \
             patch('core.enhanced_pipeline.UserFeedbackSystem'), \
             patch('core.enhanced_pipeline.OpenAIAdapter'), \
             patch('core.enhanced_pipeline.ARCHITECTURE_REGISTRY'):
            
            self.component = EnhancedPipelineComponent()
    
    def test_enhanced_pipeline_component_initialization(self):
        """Test EnhancedPipelineComponent-Initialisierung"""
        self.assertEqual(self.component.component_type.value, "router")
        self.assertEqual(self.component.version, "2.0.0")
        self.assertIsInstance(self.component.pipeline_stats, dict)


if __name__ == '__main__':
    unittest.main() 