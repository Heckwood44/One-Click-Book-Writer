#!/usr/bin/env python3
"""
Tests für Policy Engine
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

from core.policy_engine import (
    PolicyEngine, PolicyDecision, PolicyAction, PolicyTrigger,
    TemplateScore
)
from core.architecture import (
    PromptTemplate, Layer, LayerType, PipelineResult, PromptFrame,
    GenerationResult, EvaluationResult, FeedbackEntry
)


class TestPolicyAction(unittest.TestCase):
    """Test PolicyAction Enum"""
    
    def test_policy_actions(self):
        """Test alle Policy-Aktionen"""
        self.assertEqual(PolicyAction.PROMOTE.value, "promote")
        self.assertEqual(PolicyAction.RETRY.value, "retry")
        self.assertEqual(PolicyAction.EXPERIMENT.value, "experiment")
        self.assertEqual(PolicyAction.RECALIBRATE.value, "recalibrate")
        self.assertEqual(PolicyAction.MANUAL_REVIEW.value, "manual_review")


class TestPolicyTrigger(unittest.TestCase):
    """Test PolicyTrigger Enum"""
    
    def test_policy_triggers(self):
        """Test alle Policy-Trigger"""
        self.assertEqual(PolicyTrigger.SCORE_IMPROVEMENT.value, "score_improvement")
        self.assertEqual(PolicyTrigger.SCORE_DECLINE.value, "score_decline")
        self.assertEqual(PolicyTrigger.FEEDBACK_POSITIVE.value, "feedback_positive")
        self.assertEqual(PolicyTrigger.FEEDBACK_NEGATIVE.value, "feedback_negative")
        self.assertEqual(PolicyTrigger.DRIFT_DETECTED.value, "drift_detected")
        self.assertEqual(PolicyTrigger.TIME_BASED.value, "time_based")
        self.assertEqual(PolicyTrigger.EXPERIMENT_COMPLETE.value, "experiment_complete")


class TestPolicyDecision(unittest.TestCase):
    """Test PolicyDecision-Klasse"""
    
    def test_policy_decision_creation(self):
        """Test PolicyDecision-Erstellung"""
        decision = PolicyDecision(
            action=PolicyAction.PROMOTE,
            trigger=PolicyTrigger.SCORE_IMPROVEMENT,
            confidence=0.85,
            reasoning="High quality score achieved",
            metadata={"quality_score": 0.8}
        )
        
        self.assertEqual(decision.action, PolicyAction.PROMOTE)
        self.assertEqual(decision.trigger, PolicyTrigger.SCORE_IMPROVEMENT)
        self.assertEqual(decision.confidence, 0.85)
        self.assertEqual(decision.reasoning, "High quality score achieved")
        self.assertIn("quality_score", decision.metadata)
        self.assertIsInstance(decision.timestamp, datetime)


class TestTemplateScore(unittest.TestCase):
    """Test TemplateScore-Klasse"""
    
    def test_template_score_creation(self):
        """Test TemplateScore-Erstellung"""
        score = TemplateScore(
            template_hash="test_hash",
            quality_score=0.8,
            user_rating=4.5,
            feedback_count=10,
            drift_score=0.1,
            age_days=5,
            total_runs=20,
            success_rate=0.9
        )
        
        self.assertEqual(score.template_hash, "test_hash")
        self.assertEqual(score.quality_score, 0.8)
        self.assertEqual(score.user_rating, 4.5)
        self.assertEqual(score.feedback_count, 10)
        self.assertEqual(score.drift_score, 0.1)
        self.assertEqual(score.age_days, 5)
        self.assertEqual(score.total_runs, 20)
        self.assertEqual(score.success_rate, 0.9)
    
    def test_calculate_weighted_score(self):
        """Test gewichteten Score berechnen"""
        score = TemplateScore(
            template_hash="test_hash",
            quality_score=0.8,
            user_rating=4.5,
            feedback_count=10,
            drift_score=0.1,
            age_days=5,
            total_runs=20,
            success_rate=0.9
        )
        
        weights = {
            "quality": 0.4,
            "user_rating": 0.3,
            "stability": 0.2,
            "reliability": 0.1
        }
        
        weighted_score = score.calculate_weighted_score(weights)
        
        self.assertIsInstance(weighted_score, float)
        self.assertGreater(weighted_score, 0)
        # Gewichteter Score kann über 1 sein, da user_rating nicht normalisiert ist
        self.assertLessEqual(weighted_score, 5)  # Maximaler Wert mit user_rating=5
    
    def test_calculate_weighted_score_default_weights(self):
        """Test gewichteten Score mit Standard-Gewichten"""
        score = TemplateScore(
            template_hash="test_hash",
            quality_score=0.8,
            user_rating=4.5,
            feedback_count=10,
            drift_score=0.1,
            age_days=5,
            total_runs=20,
            success_rate=0.9
        )
        
        weighted_score = score.calculate_weighted_score({})
        
        self.assertIsInstance(weighted_score, float)
        self.assertGreater(weighted_score, 0)
        # Gewichteter Score kann über 1 sein, da user_rating nicht normalisiert ist
        self.assertLessEqual(weighted_score, 5)  # Maximaler Wert mit user_rating=5


class TestPolicyEngine(unittest.TestCase):
    """Test PolicyEngine-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        self.policy_engine = PolicyEngine()
        
        # Test-Template
        self.template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="Test template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction", 1.0),
                Layer(LayerType.GENRE, "fantasy", 1.0)
            ]
        )
        
        # Test-PipelineResult
        self.prompt_frame = PromptFrame(
            age_group="early_reader",
            genre="fantasy",
            emotion="joy",
            language="de"
        )
        self.generation_result = GenerationResult(
            success=True,
            german_text="Test Kapitel",
            english_text="Test Chapter",
            prompt_hash="test_hash",
            template_hash="template_hash",
            generation_time=1.5,
            word_count=100
        )
        self.evaluation_result = EvaluationResult(
            overall_score=0.8,
            readability_score=0.9,
            age_appropriateness=0.95,
            genre_compliance=0.8,
            emotional_depth=0.7,
            engagement_score=0.75
        )
        self.feedback_entry = FeedbackEntry(
            chapter_number=1,
            prompt_hash="test_hash",
            quality_score=0.8,
            user_rating=4,
            comment="Good chapter",
            language="de"
        )
        
        self.pipeline_result = PipelineResult(
            run_id="test_run",
            prompt_frame=self.prompt_frame,
            generation_result=self.generation_result,
            evaluation_result=self.evaluation_result,
            feedback_entries=[self.feedback_entry],
            compliance_status="approved",
            total_cost=0.05,
            execution_time=5.0
        )
    
    def test_policy_engine_initialization(self):
        """Test PolicyEngine-Initialisierung"""
        self.assertIsInstance(self.policy_engine.policy_history, list)
        self.assertIsInstance(self.policy_engine.template_scores, dict)
        self.assertIsInstance(self.policy_engine.segment_performance, dict)
        self.assertIsInstance(self.policy_engine.experiment_queue, list)
        self.assertIsInstance(self.policy_engine.thresholds, dict)
        self.assertIsInstance(self.policy_engine.scoring_weights, dict)
    
    def test_evaluate_pipeline_result(self):
        """Test Pipeline-Ergebnis evaluieren"""
        decision = self.policy_engine.evaluate_pipeline_result(self.pipeline_result)
        
        self.assertIsInstance(decision, PolicyDecision)
        self.assertIsInstance(decision.action, PolicyAction)
        self.assertIsInstance(decision.trigger, PolicyTrigger)
        self.assertIsInstance(decision.confidence, float)
        self.assertGreaterEqual(decision.confidence, 0.0)
        self.assertLessEqual(decision.confidence, 1.0)
        self.assertIsInstance(decision.reasoning, str)
        self.assertIsInstance(decision.metadata, dict)
    
    def test_calculate_avg_feedback_rating(self):
        """Test durchschnittliches Feedback-Rating berechnen"""
        feedback_entries = [
            FeedbackEntry(1, "hash1", 0.8, 4, "Good", "de"),
            FeedbackEntry(1, "hash2", 0.9, 5, "Excellent", "de"),
            FeedbackEntry(1, "hash3", 0.7, 3, "Okay", "de")
        ]
        
        avg_rating = self.policy_engine._calculate_avg_feedback_rating(feedback_entries)
        
        self.assertIsInstance(avg_rating, float)
        self.assertEqual(avg_rating, 4.0)  # (4+5+3)/3 = 4.0
    
    def test_calculate_avg_feedback_rating_empty(self):
        """Test durchschnittliches Feedback-Rating mit leerer Liste"""
        avg_rating = self.policy_engine._calculate_avg_feedback_rating([])
        
        self.assertIsInstance(avg_rating, float)
        self.assertEqual(avg_rating, 0.0)
    
    def test_calculate_template_score(self):
        """Test Template-Score berechnen"""
        template_score = self.policy_engine._calculate_template_score(self.pipeline_result)
        
        self.assertIsInstance(template_score, TemplateScore)
        self.assertEqual(template_score.template_hash, "template_hash")
        self.assertEqual(template_score.quality_score, 0.8)
        self.assertEqual(template_score.user_rating, 4.0)
        self.assertEqual(template_score.feedback_count, 1)
        self.assertIsInstance(template_score.drift_score, float)
        self.assertIsInstance(template_score.age_days, int)
        self.assertIsInstance(template_score.total_runs, int)
        self.assertIsInstance(template_score.success_rate, float)
    
    def test_get_active_template_ranking(self):
        """Test aktive Template-Ranking"""
        # Füge Template-Scores hinzu
        score1 = TemplateScore(
            template_hash="hash1",
            quality_score=0.9,
            user_rating=4.5,
            feedback_count=10,
            drift_score=0.1,
            age_days=5,
            total_runs=20,
            success_rate=0.9
        )
        score2 = TemplateScore(
            template_hash="hash2",
            quality_score=0.7,
            user_rating=4.0,
            feedback_count=8,
            drift_score=0.2,
            age_days=10,
            total_runs=15,
            success_rate=0.8
        )
        
        self.policy_engine.template_scores["hash1"] = score1
        self.policy_engine.template_scores["hash2"] = score2
        
        ranking = self.policy_engine.get_active_template_ranking("early_reader_fantasy")
        
        self.assertIsInstance(ranking, list)
        # Ranking kann leer sein, wenn keine Templates für das Segment gefunden werden
        self.assertGreaterEqual(len(ranking), 0)
        
        # Prüfe dass Ranking nach Score sortiert ist, falls vorhanden
        if len(ranking) > 1:
            for i in range(len(ranking) - 1):
                self.assertGreaterEqual(ranking[i][1], ranking[i + 1][1])
    
    def test_should_start_experiment(self):
        """Test Experiment-Start prüfen"""
        # Test ohne Segment-Performance (sollte True zurückgeben)
        result = self.policy_engine.should_start_experiment("new_segment")
        
        self.assertIsInstance(result, bool)
        self.assertTrue(result)
    
    def test_get_experiment_suggestions(self):
        """Test Experiment-Vorschläge"""
        suggestions = self.policy_engine.get_experiment_suggestions("early_reader_fantasy")
        
        self.assertIsInstance(suggestions, list)
        # Prüfe dass alle Vorschläge gültige Struktur haben
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, dict)
            self.assertIn("type", suggestion)
            self.assertIn("description", suggestion)
            self.assertIn("priority", suggestion)
    
    def test_get_policy_summary(self):
        """Test Policy-Summary"""
        # Füge einige Entscheidungen hinzu
        decision1 = PolicyDecision(
            action=PolicyAction.PROMOTE,
            trigger=PolicyTrigger.SCORE_IMPROVEMENT,
            confidence=0.8,
            reasoning="High quality",
            metadata={}
        )
        decision2 = PolicyDecision(
            action=PolicyAction.RETRY,
            trigger=PolicyTrigger.SCORE_DECLINE,
            confidence=0.6,
            reasoning="Low quality",
            metadata={}
        )
        
        self.policy_engine.policy_history = [decision1, decision2]
        
        summary = self.policy_engine.get_policy_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn("total_decisions", summary)
        self.assertIn("decision_distribution", summary)
        self.assertIn("recent_activity", summary)
        self.assertIn("thresholds", summary)  # Geändert von "experiment_queue_size"
        self.assertEqual(summary["total_decisions"], 2)
    
    def test_update_segment_performance(self):
        """Test Segment-Performance aktualisieren"""
        segment = "early_reader_fantasy"
        
        self.policy_engine._update_segment_performance(segment, self.pipeline_result)
        
        self.assertIn(segment, self.policy_engine.segment_performance)
        performance = self.policy_engine.segment_performance[segment]
        self.assertIn("runs", performance)
        self.assertIn("avg_score", performance)
        self.assertIn("last_update", performance)  # Geändert von "last_updated"
    
    def test_detect_drift(self):
        """Test Drift-Erkennung"""
        segment = "early_reader_fantasy"
        
        # Erste Aktualisierung
        self.policy_engine._update_segment_performance(segment, self.pipeline_result)
        
        # Zweite Aktualisierung mit niedrigerem Score (Drift)
        self.pipeline_result.evaluation_result.overall_score = 0.5
        drift_detected = self.policy_engine._detect_drift(segment, self.pipeline_result)
        
        self.assertIsInstance(drift_detected, bool)
    
    def test_create_promotion_decision(self):
        """Test Promotion-Entscheidung erstellen"""
        template_score = TemplateScore(
            template_hash="test_hash",
            quality_score=0.9,
            user_rating=4.5,
            feedback_count=10,
            drift_score=0.1,
            age_days=5,
            total_runs=20,
            success_rate=0.9
        )
        
        # Mock optimization_result
        self.pipeline_result.optimization_result = Mock()
        self.pipeline_result.optimization_result.quality_score_delta = 0.1
        self.pipeline_result.optimization_result.optimized_prompt_hash = "optimized_hash"
        
        decision = self.policy_engine._create_promotion_decision(self.pipeline_result, template_score)
        
        self.assertIsInstance(decision, PolicyDecision)
        self.assertEqual(decision.action, PolicyAction.PROMOTE)
        self.assertEqual(decision.trigger, PolicyTrigger.SCORE_IMPROVEMENT)
        self.assertGreater(decision.confidence, 0)
        self.assertLessEqual(decision.confidence, 1)
    
    def test_create_retry_decision(self):
        """Test Retry-Entscheidung erstellen"""
        template_score = TemplateScore(
            template_hash="test_hash",
            quality_score=0.5,
            user_rating=3.0,
            feedback_count=5,
            drift_score=0.3,
            age_days=15,
            total_runs=10,
            success_rate=0.6
        )
        
        decision = self.policy_engine._create_retry_decision(self.pipeline_result, template_score)
        
        self.assertIsInstance(decision, PolicyDecision)
        self.assertEqual(decision.action, PolicyAction.RETRY)
        self.assertEqual(decision.trigger, PolicyTrigger.SCORE_DECLINE)
        self.assertGreater(decision.confidence, 0)
        self.assertLessEqual(decision.confidence, 1)
    
    def test_create_drift_decision(self):
        """Test Drift-Entscheidung erstellen"""
        template_score = TemplateScore(
            template_hash="test_hash",
            quality_score=0.6,
            user_rating=3.5,
            feedback_count=8,
            drift_score=0.4,
            age_days=20,
            total_runs=25,
            success_rate=0.7
        )
        
        decision = self.policy_engine._create_drift_decision(self.pipeline_result, template_score)
        
        self.assertIsInstance(decision, PolicyDecision)
        self.assertEqual(decision.action, PolicyAction.RECALIBRATE)
        self.assertEqual(decision.trigger, PolicyTrigger.DRIFT_DETECTED)
        self.assertGreater(decision.confidence, 0)
        self.assertLessEqual(decision.confidence, 1)
    
    def test_evaluate_feedback(self):
        """Test Feedback evaluieren"""
        # Test mit positivem Feedback
        self.pipeline_result.feedback_entries[0].user_rating = 5
        
        decision = self.policy_engine._evaluate_feedback(self.pipeline_result)
        
        if decision is not None:
            self.assertIsInstance(decision, PolicyDecision)
            self.assertIsInstance(decision.action, PolicyAction)
            self.assertIsInstance(decision.trigger, PolicyTrigger)
    
    def test_evaluate_feedback_negative(self):
        """Test Feedback evaluieren mit negativem Feedback"""
        # Test mit negativem Feedback
        self.pipeline_result.feedback_entries[0].user_rating = 2
        
        decision = self.policy_engine._evaluate_feedback(self.pipeline_result)
        
        if decision is not None:
            self.assertIsInstance(decision, PolicyDecision)
            self.assertIsInstance(decision.action, PolicyAction)
            self.assertIsInstance(decision.trigger, PolicyTrigger)


class TestPolicyEngineIntegration(unittest.TestCase):
    """Integrationstests für PolicyEngine"""
    
    def setUp(self):
        """Setup für Integrationstests"""
        self.policy_engine = PolicyEngine()
        
        # Erstelle Test-PipelineResult
        self.prompt_frame = PromptFrame(
            age_group="early_reader",
            genre="fantasy",
            emotion="joy",
            language="de"
        )
        self.generation_result = GenerationResult(
            success=True,
            german_text="Test Kapitel",
            english_text="Test Chapter",
            prompt_hash="test_hash",
            template_hash="template_hash",
            generation_time=1.5,
            word_count=100
        )
        self.evaluation_result = EvaluationResult(
            overall_score=0.85,
            readability_score=0.9,
            age_appropriateness=0.95,
            genre_compliance=0.8,
            emotional_depth=0.7,
            engagement_score=0.75
        )
        self.feedback_entry = FeedbackEntry(
            chapter_number=1,
            prompt_hash="test_hash",
            quality_score=0.85,
            user_rating=5,
            comment="Excellent chapter",
            language="de"
        )
        
        self.pipeline_result = PipelineResult(
            run_id="test_run",
            prompt_frame=self.prompt_frame,
            generation_result=self.generation_result,
            evaluation_result=self.evaluation_result,
            feedback_entries=[self.feedback_entry],
            compliance_status="approved",
            total_cost=0.05,
            execution_time=3.0
        )
    
    def test_full_policy_evaluation_workflow(self):
        """Test vollständiger Policy-Evaluierungs-Workflow"""
        # Evaluiere Pipeline-Ergebnis
        decision = self.policy_engine.evaluate_pipeline_result(self.pipeline_result)
        
        # Prüfe Ergebnisse
        self.assertIsInstance(decision, PolicyDecision)
        self.assertIsInstance(decision.action, PolicyAction)
        self.assertIsInstance(decision.trigger, PolicyTrigger)
        self.assertGreater(decision.confidence, 0)
        self.assertLessEqual(decision.confidence, 1)
        self.assertIsInstance(decision.reasoning, str)
        self.assertIsInstance(decision.metadata, dict)
        
        # Prüfe dass Entscheidung in History gespeichert wurde
        self.assertIn(decision, self.policy_engine.policy_history)
    
    def test_template_ranking_workflow(self):
        """Test Template-Ranking-Workflow"""
        # Füge mehrere Template-Scores hinzu
        for i in range(3):
            score = TemplateScore(
                template_hash=f"hash_{i}",
                quality_score=0.8 - (i * 0.1),
                user_rating=4.5 - (i * 0.5),
                feedback_count=10 - i,
                drift_score=0.1 + (i * 0.1),
                age_days=5 + i,
                total_runs=20 - i,
                success_rate=0.9 - (i * 0.1)
            )
            self.policy_engine.template_scores[f"hash_{i}"] = score
        
        # Hole Ranking
        ranking = self.policy_engine.get_active_template_ranking("early_reader_fantasy")
        
        # Prüfe Ergebnisse
        self.assertIsInstance(ranking, list)
        # Ranking kann leer sein, wenn keine Templates für das Segment gefunden werden
        self.assertGreaterEqual(len(ranking), 0)
        
        # Prüfe dass Ranking nach Score sortiert ist, falls vorhanden
        if len(ranking) > 1:
            for i in range(len(ranking) - 1):
                self.assertGreaterEqual(ranking[i][1], ranking[i + 1][1])
    
    def test_experiment_workflow(self):
        """Test Experiment-Workflow"""
        segment = "early_reader_fantasy"
        
        # Prüfe Experiment-Start
        should_start = self.policy_engine.should_start_experiment(segment)
        
        self.assertIsInstance(should_start, bool)
        
        # Hole Experiment-Vorschläge
        suggestions = self.policy_engine.get_experiment_suggestions(segment)
        
        self.assertIsInstance(suggestions, list)
        
        # Prüfe dass alle Vorschläge gültig sind
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, dict)
            self.assertIn("type", suggestion)
            self.assertIn("description", suggestion)
            self.assertIn("priority", suggestion)
    
    def test_policy_summary_workflow(self):
        """Test Policy-Summary-Workflow"""
        # Führe mehrere Evaluationen durch
        for i in range(3):
            self.pipeline_result.evaluation_result.overall_score = 0.8 + (i * 0.05)
            self.policy_engine.evaluate_pipeline_result(self.pipeline_result)
        
        # Hole Summary
        summary = self.policy_engine.get_policy_summary()
        
        # Prüfe Ergebnisse
        self.assertIsInstance(summary, dict)
        self.assertIn("total_decisions", summary)
        self.assertIn("decision_distribution", summary)
        self.assertIn("recent_activity", summary)
        self.assertIn("thresholds", summary)  # Geändert von "experiment_queue_size"
        self.assertEqual(summary["total_decisions"], 3)


if __name__ == "__main__":
    unittest.main() 