#!/usr/bin/env python3
"""
Tests für Promotion Guardrails
"""

import unittest
import time
from unittest.mock import Mock, patch
from core.promotion_guardrails import (
    PromotionGuardrails, 
    PromotionRequest, 
    PromotionResult, 
    PromotionStatus,
    check_promotion_eligibility,
    get_promotion_stats
)

class TestPromotionGuardrails(unittest.TestCase):
    """Tests für Promotion Guardrails"""
    
    def setUp(self):
        """Setup für Tests"""
        self.guardrails = PromotionGuardrails()
        self.test_template_id = "test_template_001"
        self.test_request = PromotionRequest(
            template_id=self.test_template_id,
            template_version="v1.0.0",
            quality_score=0.8,
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={"test": True}
        )
    
    def test_cooldown_check(self):
        """Test Cooldown-Check"""
        # Erste Promotion sollte erlaubt sein
        result = self.guardrails.check_promotion_eligibility(self.test_request)
        self.assertTrue(result.approved)
        self.assertEqual(result.status, PromotionStatus.APPROVED)
        
        # Zweite Promotion sollte blockiert sein (Cooldown)
        result2 = self.guardrails.check_promotion_eligibility(self.test_request)
        self.assertFalse(result2.approved)
        self.assertEqual(result2.status, PromotionStatus.COOLDOWN)
        self.assertIsNotNone(result2.cooldown_remaining)
    
    def test_quality_score_check(self):
        """Test Quality-Score-Check"""
        # Test mit zu niedrigem Score
        low_score_request = PromotionRequest(
            template_id="low_score_template",
            template_version="v1.0.0",
            quality_score=0.5,  # Unter Minimum (0.7)
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(low_score_request)
        self.assertFalse(result.approved)
        self.assertEqual(result.status, PromotionStatus.INSUFFICIENT_SCORE)
        self.assertIsNotNone(result.score_delta)
        self.assertLess(result.score_delta, 0)
    
    def test_stability_check(self):
        """Test Stabilitäts-Check"""
        # Füge instabile Scores hinzu
        unstable_scores = [0.9, 0.3, 0.8, 0.2, 0.7]  # Hohe Varianz
        self.guardrails.score_history[self.test_template_id] = unstable_scores
        
        # Erstelle Request mit hohem Score
        high_score_request = PromotionRequest(
            template_id=self.test_template_id,
            template_version="v1.0.0",
            quality_score=0.9,
            user_feedback_score=0.8,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(high_score_request)
        self.assertFalse(result.approved)
        self.assertEqual(result.status, PromotionStatus.UNSTABLE)
        self.assertIsNotNone(result.stability_score)
    
    def test_combined_score_check(self):
        """Test kombinierter Score-Check"""
        # Test mit niedrigem Feedback-Score
        low_feedback_request = PromotionRequest(
            template_id="low_feedback_template",
            template_version="v1.0.0",
            quality_score=0.8,
            user_feedback_score=0.3,  # Unter Minimum (0.6)
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(low_feedback_request)
        self.assertFalse(result.approved)
        self.assertEqual(result.status, PromotionStatus.INSUFFICIENT_SCORE)
    
    def test_successful_promotion(self):
        """Test erfolgreiche Promotion"""
        # Erstelle Request mit guten Scores
        good_request = PromotionRequest(
            template_id="good_template",
            template_version="v1.0.0",
            quality_score=0.85,
            user_feedback_score=0.75,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(good_request)
        self.assertTrue(result.approved)
        self.assertEqual(result.status, PromotionStatus.APPROVED)
        self.assertIsNotNone(result.recommendations)
    
    def test_promotion_stats(self):
        """Test Promotions-Statistiken"""
        # Führe mehrere Promotions durch
        for i in range(3):
            request = PromotionRequest(
                template_id=self.test_template_id,
                template_version=f"v1.0.{i}",
                quality_score=0.8 + (i * 0.05),
                user_feedback_score=0.7 + (i * 0.05),
                timestamp=time.time() + i,
                segment="fantasy_early_reader",
                metadata={}
            )
            self.guardrails.check_promotion_eligibility(request)
        
        stats = self.guardrails.get_promotion_stats(self.test_template_id)
        self.assertEqual(stats["total_promotions"], 3)
        self.assertGreater(stats["avg_quality_score"], 0.8)
        self.assertGreater(stats["avg_feedback_score"], 0.7)
    
    def test_promotion_attempt_tracking(self):
        """Test dass alle Promotion-Versuche aufgezeichnet werden"""
        # Erste Promotion sollte genehmigt werden
        request1 = PromotionRequest(
            template_id="test_tracking_template",
            template_version="v1.0.0",
            quality_score=0.85,
            user_feedback_score=0.75,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        result1 = self.guardrails.check_promotion_eligibility(request1)
        self.assertTrue(result1.approved)
        
        # Zweite Promotion sollte abgelehnt werden (Cooldown)
        request2 = PromotionRequest(
            template_id="test_tracking_template",
            template_version="v1.0.1",
            quality_score=0.9,
            user_feedback_score=0.8,
            timestamp=time.time() + 1,
            segment="fantasy_early_reader",
            metadata={}
        )
        result2 = self.guardrails.check_promotion_eligibility(request2)
        self.assertFalse(result2.approved)
        self.assertEqual(result2.status, PromotionStatus.COOLDOWN)
        
        # Prüfe dass beide Versuche aufgezeichnet wurden
        stats = self.guardrails.get_promotion_stats("test_tracking_template")
        self.assertEqual(stats["total_promotions"], 2)
        
        # Prüfe dass die History beide Versuche enthält
        history = self.guardrails.promotion_history["test_tracking_template"]
        self.assertEqual(len(history), 2)
        
        # Prüfe dass der erste Versuch als genehmigt markiert ist
        self.assertTrue(history[0].metadata.get("approved", False))
        
        # Prüfe dass der zweite Versuch als abgelehnt markiert ist
        self.assertFalse(history[1].metadata.get("approved", True))
        self.assertEqual(history[1].metadata.get("rejection_reason"), "cooldown")
    
    def test_score_history_tracking(self):
        """Test dass Score-History für alle Versuche aktualisiert wird"""
        template_id = "test_score_tracking"
        
        # Führe mehrere Promotions durch
        for i in range(3):
            request = PromotionRequest(
                template_id=template_id,
                template_version=f"v1.0.{i}",
                quality_score=0.8 + (i * 0.1),
                user_feedback_score=0.7 + (i * 0.1),
                timestamp=time.time() + i,
                segment="fantasy_early_reader",
                metadata={}
            )
            self.guardrails.check_promotion_eligibility(request)
        
        # Prüfe dass Score-History aktualisiert wurde
        self.assertIn(template_id, self.guardrails.score_history)
        scores = self.guardrails.score_history[template_id]
        self.assertEqual(len(scores), 3)
        
        # Prüfe dass die Scores korrekt sind
        expected_scores = [0.8, 0.9, 1.0]
        for i, score in enumerate(scores):
            self.assertAlmostEqual(score, expected_scores[i], places=1)
    
    def test_rejection_reasons_tracking(self):
        """Test dass Ablehnungsgründe korrekt aufgezeichnet werden"""
        # Test mit zu niedrigem Score
        low_score_request = PromotionRequest(
            template_id="test_rejection_reasons",
            template_version="v1.0.0",
            quality_score=0.5,  # Unter Minimum
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        result = self.guardrails.check_promotion_eligibility(low_score_request)
        self.assertFalse(result.approved)
        self.assertEqual(result.status, PromotionStatus.INSUFFICIENT_SCORE)
        
        # Prüfe dass der Ablehnungsgrund aufgezeichnet wurde
        history = self.guardrails.promotion_history["test_rejection_reasons"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].metadata.get("rejection_reason"), "insufficient_score")
        self.assertFalse(history[0].metadata.get("approved", True))
    
    def test_reset_cooldown(self):
        """Test Cooldown-Reset"""
        # Führe Promotion durch
        result = self.guardrails.check_promotion_eligibility(self.test_request)
        self.assertTrue(result.approved)
        
        # Prüfe dass Cooldown aktiv ist
        result2 = self.guardrails.check_promotion_eligibility(self.test_request)
        self.assertFalse(result2.approved)
        self.assertEqual(result2.status, PromotionStatus.COOLDOWN)
        
        # Reset Cooldown
        success = self.guardrails.reset_cooldown(self.test_template_id)
        self.assertTrue(success)
        
        # Prüfe dass Promotion wieder erlaubt ist
        result3 = self.guardrails.check_promotion_eligibility(self.test_request)
        self.assertTrue(result3.approved)
    
    def test_config_update(self):
        """Test Konfigurations-Update"""
        # Ändere Mindest-Quality-Score
        new_config = {"min_quality_score": 0.9}
        success = self.guardrails.update_config(new_config)
        self.assertTrue(success)
        
        # Test mit Score der vorher OK war, jetzt aber zu niedrig ist
        request = PromotionRequest(
            template_id="config_test_template",
            template_version="v1.0.0",
            quality_score=0.85,  # Über 0.7, aber unter 0.9
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(request)
        self.assertFalse(result.approved)
        self.assertEqual(result.status, PromotionStatus.INSUFFICIENT_SCORE)

class TestGlobalFunctions(unittest.TestCase):
    """Tests für globale Funktionen"""
    
    def setUp(self):
        """Setup für Tests"""
        self.test_request = PromotionRequest(
            template_id="global_test_template",
            template_version="v1.0.0",
            quality_score=0.8,
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
    
    def test_check_promotion_eligibility_global(self):
        """Test globale Promotion-Check-Funktion"""
        result = check_promotion_eligibility(self.test_request)
        self.assertIsInstance(result, PromotionResult)
        self.assertTrue(result.approved)
    
    def test_get_promotion_stats_global(self):
        """Test globale Stats-Funktion"""
        # Führe Promotion durch
        check_promotion_eligibility(self.test_request)
        
        # Hole Statistiken
        stats = get_promotion_stats(self.test_request.template_id)
        self.assertIsInstance(stats, dict)
        self.assertIn("total_promotions", stats)
        self.assertIn("avg_quality_score", stats)

class TestEdgeCases(unittest.TestCase):
    """Tests für Edge Cases"""
    
    def setUp(self):
        """Setup für Tests"""
        self.guardrails = PromotionGuardrails()
    
    def test_empty_score_history(self):
        """Test mit leerer Score-History"""
        request = PromotionRequest(
            template_id="empty_history_template",
            template_version="v1.0.0",
            quality_score=0.8,
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(request)
        self.assertTrue(result.approved)
    
    def test_single_score_history(self):
        """Test mit nur einem Score in History"""
        template_id = "single_score_template"
        self.guardrails.score_history[template_id] = [0.8]
        
        request = PromotionRequest(
            template_id=template_id,
            template_version="v1.0.0",
            quality_score=0.8,
            user_feedback_score=0.7,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(request)
        self.assertTrue(result.approved)
    
    def test_extreme_scores(self):
        """Test mit extremen Scores"""
        # Test mit perfektem Score
        perfect_request = PromotionRequest(
            template_id="perfect_template",
            template_version="v1.0.0",
            quality_score=1.0,
            user_feedback_score=1.0,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result = self.guardrails.check_promotion_eligibility(perfect_request)
        self.assertTrue(result.approved)
        
        # Test mit sehr niedrigen Scores
        low_request = PromotionRequest(
            template_id="low_template",
            template_version="v1.0.0",
            quality_score=0.0,
            user_feedback_score=0.0,
            timestamp=time.time(),
            segment="fantasy_early_reader",
            metadata={}
        )
        
        result2 = self.guardrails.check_promotion_eligibility(low_request)
        self.assertFalse(result2.approved)

if __name__ == "__main__":
    unittest.main() 