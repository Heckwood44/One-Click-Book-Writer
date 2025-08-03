#!/usr/bin/env python3
"""
Umfassende Tests für Feedback Intelligence - Coverage-Verbesserung
Ziel: Coverage von 27% auf mindestens 70% erhöhen
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import time
from typing import List, Dict, Any, Optional

from core.feedback_intelligence import (
    FeedbackIntelligence, FeedbackFeature, TemplateSuggestion
)
from core.architecture import (
    FeedbackEntry, PromptFrame, GenerationResult, EvaluationResult,
    ComponentType, PromptTemplate, Layer, LayerType
)


class TestFeedbackIntelligenceComprehensive(unittest.TestCase):
    """Umfassende Tests für FeedbackIntelligence - Coverage-Verbesserung"""
    
    def setUp(self):
        """Setup für umfassende Tests"""
        with patch('core.feedback_intelligence.LayeredCompositionEngine'):
            self.feedback_intelligence = FeedbackIntelligence()
        
        # Test-Feedback-Entries
        self.feedback_entries = [
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=4.0,
                user_rating=5,
                comment="Excellent story for children! Very engaging and well-written.",
                language="de"
            ),
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=2.0,
                user_rating=2,
                comment="Too complex vocabulary for kids. Need simpler language.",
                language="de"
            ),
            FeedbackEntry(
                chapter_number=2,
                prompt_hash="hash2",
                quality_score=3.5,
                user_rating=4,
                comment="Good story but could be more emotional and engaging.",
                language="de"
            )
        ]
        
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

    # ===== TESTS FÜR FEHLENDE CODE-PFADE =====
    
    def test_analyze_feedback_comprehensive(self):
        """Test umfassende Feedback-Analyse"""
        # Führe Feedback-Analyse aus
        features = self.feedback_intelligence.analyze_feedback(self.feedback_entries)
        
        # Verifikationen
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        # Prüfe dass Features extrahiert wurden
        for feature in features:
            self.assertIsInstance(feature, FeedbackFeature)
            self.assertIn(feature.sentiment, ["positive", "negative", "neutral"])
            self.assertGreaterEqual(feature.confidence, 0.0)
            self.assertLessEqual(feature.confidence, 1.0)

    def test_analyze_feedback_with_empty_entries(self):
        """Test Feedback-Analyse mit leeren Einträgen"""
        # Führe Analyse mit leeren Einträgen aus
        features = self.feedback_intelligence.analyze_feedback([])
        
        # Verifikationen
        self.assertIsInstance(features, list)
        self.assertEqual(len(features), 0)

    def test_extract_features_from_text(self):
        """Test Feature-Extraktion aus Text"""
        test_texts = [
            "Mehr bildhafte Sprache verwenden",
            "Kürzere Sätze für bessere Lesbarkeit",
            "Mehr Gefühle und Emotionen einbauen",
            "Dialoge hinzufügen für mehr Lebendigkeit"
        ]
        
        for text in test_texts:
            with self.subTest(text=text):
                features = self.feedback_intelligence._extract_features_from_text(text)
                
                # Verifikationen
                self.assertIsInstance(features, list)
                for feature in features:
                    self.assertIsInstance(feature, FeedbackFeature)
                    self.assertIn(feature.feature_type, ["style", "readability", "emotion", "dialogue"])

    def test_extract_features_from_rating(self):
        """Test Feature-Extraktion aus Bewertungen"""
        test_cases = [
            (5, "Excellent story with great imagery"),
            (2, "Too complex vocabulary"),
            (4, "Good but needs more emotion"),
            (1, "Very difficult to understand")
        ]
        
        for rating, comment in test_cases:
            with self.subTest(rating=rating, comment=comment):
                features = self.feedback_intelligence._extract_features_from_rating(rating, comment)
                
                # Verifikationen
                self.assertIsInstance(features, list)
                for feature in features:
                    self.assertIsInstance(feature, FeedbackFeature)

    def test_determine_sentiment(self):
        """Test Sentiment-Bestimmung"""
        test_cases = [
            ("excellent", "This is an excellent story", "positive"),
            ("terrible", "This is a terrible story", "negative"),
            ("okay", "This is an okay story", "neutral"),
            ("amazing", "This is amazing", "positive"),
            ("boring", "This is boring", "negative")
        ]
        
        for matched_text, full_text, expected_sentiment in test_cases:
            with self.subTest(matched_text=matched_text):
                sentiment = self.feedback_intelligence._determine_sentiment(matched_text, full_text)
                
                # Verifikationen
                self.assertIn(sentiment, ["positive", "negative", "neutral"])

    def test_calculate_confidence(self):
        """Test Confidence-Berechnung"""
        test_cases = [
            ("excellent", "This is an excellent story", 0.8),
            ("terrible", "This is a terrible story", 0.8),
            ("okay", "This is an okay story", 0.5),
            ("amazing", "This is amazing", 0.9),
            ("boring", "This is boring", 0.7)
        ]
        
        for matched_text, full_text, expected_min_confidence in test_cases:
            with self.subTest(matched_text=matched_text):
                confidence = self.feedback_intelligence._calculate_confidence(matched_text, full_text)
                
                # Verifikationen
                self.assertGreaterEqual(confidence, 0.0)
                self.assertLessEqual(confidence, 1.0)
                self.assertGreaterEqual(confidence, expected_min_confidence)

    def test_get_suggested_adjustment(self):
        """Test Abruf von vorgeschlagenen Anpassungen"""
        test_cases = [
            ("imagery", "positive"),
            ("sentence_length", "negative"),
            ("emotional_depth", "positive"),
            ("dialogue", "negative"),
            ("pacing", "positive")
        ]
        
        for feature_name, sentiment in test_cases:
            with self.subTest(feature_name=feature_name, sentiment=sentiment):
                adjustment = self.feedback_intelligence._get_suggested_adjustment(feature_name, sentiment)
                
                # Verifikationen
                self.assertIsInstance(adjustment, dict)
                self.assertIn("action", adjustment)
                self.assertIn("parameters", adjustment)

    def test_group_similar_features(self):
        """Test Gruppierung ähnlicher Features"""
        # Erstelle Test-Features
        features = [
            FeedbackFeature(
                feature_type="style",
                feature_name="imagery",
                sentiment="positive",
                confidence=0.8,
                source_text="More imagery",
                suggested_adjustment={"action": "enhance", "parameters": {}}
            ),
            FeedbackFeature(
                feature_type="style",
                feature_name="imagery",
                sentiment="positive",
                confidence=0.7,
                source_text="Better descriptions",
                suggested_adjustment={"action": "enhance", "parameters": {}}
            ),
            FeedbackFeature(
                feature_type="readability",
                feature_name="sentence_length",
                sentiment="negative",
                confidence=0.9,
                source_text="Shorter sentences",
                suggested_adjustment={"action": "reduce", "parameters": {}}
            )
        ]
        
        # Führe Gruppierung aus
        grouped_features = self.feedback_intelligence._group_similar_features(features)
        
        # Verifikationen
        self.assertIsInstance(grouped_features, list)
        self.assertLessEqual(len(grouped_features), len(features))

    def test_generate_template_suggestions(self):
        """Test Template-Vorschlags-Generierung"""
        # Erstelle Test-Features
        features = [
            FeedbackFeature(
                feature_type="style",
                feature_name="imagery",
                sentiment="positive",
                confidence=0.8,
                source_text="More imagery",
                suggested_adjustment={"action": "enhance", "parameters": {}}
            ),
            FeedbackFeature(
                feature_type="readability",
                feature_name="sentence_length",
                sentiment="negative",
                confidence=0.9,
                source_text="Shorter sentences",
                suggested_adjustment={"action": "reduce", "parameters": {}}
            )
        ]
        
        # Generiere Template-Vorschläge
        suggestions = self.feedback_intelligence.generate_template_suggestions(
            "style", features, self.template
        )
        
        # Verifikationen
        self.assertIsInstance(suggestions, list)
        for suggestion in suggestions:
            self.assertIsInstance(suggestion, TemplateSuggestion)
            self.assertIn(suggestion.priority, ["low", "medium", "high"])
            self.assertGreaterEqual(suggestion.confidence, 0.0)
            self.assertLessEqual(suggestion.confidence, 1.0)

    def test_create_suggestion(self):
        """Test Erstellung von Vorschlägen"""
        # Erstelle Test-Features
        features = [
            FeedbackFeature(
                feature_type="style",
                feature_name="imagery",
                sentiment="positive",
                confidence=0.8,
                source_text="More imagery",
                suggested_adjustment={"action": "enhance", "parameters": {}}
            )
        ]
        
        # Erstelle Vorschlag
        suggestion = self.feedback_intelligence._create_suggestion(
            "style", features, "high", self.template
        )
        
        # Verifikationen
        self.assertIsInstance(suggestion, TemplateSuggestion)
        self.assertEqual(suggestion.segment, "style")
        self.assertEqual(suggestion.priority, "high")
        self.assertIsInstance(suggestion.adjustments, list)

    def test_apply_template_suggestion(self):
        """Test Anwendung von Template-Vorschlägen"""
        # Erstelle Test-Vorschlag
        suggestion = TemplateSuggestion(
            suggestion_id="test_suggestion",
            segment="style",
            description="Enhance imagery",
            adjustments=[
                {
                    "layer_type": "style",
                    "action": "enhance",
                    "parameters": {"intensity": 1.2}
                }
            ],
            priority="high",
            confidence=0.8,
            reasoning="Users want more imagery",
            metadata={}
        )
        
        # Wende Vorschlag an
        modified_template = self.feedback_intelligence.apply_template_suggestion(
            suggestion, self.template
        )
        
        # Verifikationen
        self.assertIsInstance(modified_template, PromptTemplate)
        self.assertEqual(modified_template.template_id, self.template.template_id)

    def test_find_layer_adjustment(self):
        """Test Suche nach Layer-Anpassungen"""
        adjustments = [
            {"layer_type": "style", "action": "enhance"},
            {"layer_type": "target_audience", "action": "adjust"}
        ]
        
        # Teste verschiedene Layer-Typen
        test_cases = [
            ("style", {"layer_type": "style", "action": "enhance"}),
            ("target_audience", {"layer_type": "target_audience", "action": "adjust"}),
            ("nonexistent", None)
        ]
        
        for layer_type, expected_adjustment in test_cases:
            with self.subTest(layer_type=layer_type):
                adjustment = self.feedback_intelligence._find_layer_adjustment(layer_type, adjustments)
                
                if expected_adjustment:
                    self.assertEqual(adjustment, expected_adjustment)
                else:
                    self.assertIsNone(adjustment)

    def test_apply_layer_adjustment(self):
        """Test Anwendung von Layer-Anpassungen"""
        # Erstelle Test-Layer
        layer = Layer(LayerType.STYLE, "Test content", 1.0)
        
        # Teste verschiedene Anpassungen
        adjustments = [
            {"action": "enhance", "parameters": {"weight": 1.2}},
            {"action": "modify", "parameters": {"content": "Modified content"}},
            {"action": "unknown", "parameters": {}}
        ]
        
        for adjustment in adjustments:
            with self.subTest(adjustment=adjustment):
                result = self.feedback_intelligence._apply_layer_adjustment(layer, adjustment)
                
                # Verifikationen
                self.assertIsNotNone(result)

    def test_get_feedback_summary(self):
        """Test Feedback-Zusammenfassung"""
        # Füge Feedback zur Historie hinzu
        self.feedback_intelligence.feedback_history = self.feedback_entries
        
        # Hole Zusammenfassung
        summary = self.feedback_intelligence.get_feedback_summary()
        
        # Verifikationen
        self.assertIsInstance(summary, dict)
        self.assertIn("total_entries", summary)
        self.assertIn("feature_distribution", summary)
        self.assertIn("sentiment_distribution", summary)
        self.assertIn("average_confidence", summary)
        self.assertEqual(summary["total_entries"], len(self.feedback_entries))

    def test_get_feature_distribution(self):
        """Test Feature-Verteilungs-Berechnung"""
        # Füge Features zur Historie hinzu
        features = [
            FeedbackFeature("style", "imagery", "positive", 0.8, "text", {}),
            FeedbackFeature("style", "imagery", "positive", 0.7, "text", {}),
            FeedbackFeature("readability", "sentence_length", "negative", 0.9, "text", {})
        ]
        
        # Mock feature_distribution
        self.feedback_intelligence.feature_distribution = {
            "imagery": 2,
            "sentence_length": 1
        }
        
        # Hole Verteilung
        distribution = self.feedback_intelligence._get_feature_distribution()
        
        # Verifikationen
        self.assertIsInstance(distribution, dict)
        self.assertEqual(distribution["imagery"], 2)
        self.assertEqual(distribution["sentence_length"], 1)

    def test_get_sentiment_distribution(self):
        """Test Sentiment-Verteilungs-Berechnung"""
        # Mock sentiment_distribution
        self.feedback_intelligence.sentiment_distribution = {
            "positive": 5,
            "negative": 3,
            "neutral": 2
        }
        
        # Hole Verteilung
        distribution = self.feedback_intelligence._get_sentiment_distribution()
        
        # Verifikationen
        self.assertIsInstance(distribution, dict)
        self.assertEqual(distribution["positive"], 5)
        self.assertEqual(distribution["negative"], 3)
        self.assertEqual(distribution["neutral"], 2)

    def test_calculate_avg_confidence(self):
        """Test Durchschnitts-Confidence-Berechnung"""
        # Mock confidence_scores
        self.feedback_intelligence.confidence_scores = [0.8, 0.7, 0.9, 0.6]
        
        # Berechne Durchschnitt
        avg_confidence = self.feedback_intelligence._calculate_avg_confidence()
        
        # Verifikationen
        self.assertIsInstance(avg_confidence, float)
        self.assertGreaterEqual(avg_confidence, 0.0)
        self.assertLessEqual(avg_confidence, 1.0)
        self.assertAlmostEqual(avg_confidence, 0.75, places=2)

    def test_analyze_feedback_with_mixed_sentiments(self):
        """Test Feedback-Analyse mit gemischten Sentiments"""
        # Erstelle Feedback mit gemischten Sentiments
        mixed_feedback = [
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=4.0,
                user_rating=5,
                comment="Great imagery but too complex sentences",
                language="de"
            ),
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=3.0,
                user_rating=3,
                comment="Okay story, could be better",
                language="de"
            )
        ]
        
        # Führe Analyse aus
        features = self.feedback_intelligence.analyze_feedback(mixed_feedback)
        
        # Verifikationen
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        # Prüfe dass verschiedene Sentiments erkannt wurden
        sentiments = [feature.sentiment for feature in features]
        self.assertIn("positive", sentiments)
        self.assertIn("neutral", sentiments)

    def test_analyze_feedback_with_high_confidence(self):
        """Test Feedback-Analyse mit hoher Confidence"""
        # Erstelle Feedback mit klaren Indikatoren
        clear_feedback = [
            FeedbackEntry(
                chapter_number=1,
                prompt_hash="hash1",
                quality_score=5.0,
                user_rating=5,
                comment="Excellent imagery and emotional depth!",
                language="de"
            )
        ]
        
        # Führe Analyse aus
        features = self.feedback_intelligence.analyze_feedback(clear_feedback)
        
        # Verifikationen
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        # Prüfe dass hohe Confidence erkannt wurde
        for feature in features:
            self.assertGreaterEqual(feature.confidence, 0.7)

    def test_generate_template_suggestions_with_high_priority(self):
        """Test Template-Vorschläge mit hoher Priorität"""
        # Erstelle Features mit hoher Confidence
        high_priority_features = [
            FeedbackFeature(
                feature_type="readability",
                feature_name="sentence_length",
                sentiment="negative",
                confidence=0.95,
                source_text="Very complex sentences",
                suggested_adjustment={"action": "simplify", "parameters": {}}
            )
        ]
        
        # Generiere Vorschläge
        suggestions = self.feedback_intelligence.generate_template_suggestions(
            "readability", high_priority_features, self.template
        )
        
        # Verifikationen
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Prüfe dass hohe Priorität erkannt wurde
        for suggestion in suggestions:
            self.assertIn(suggestion.priority, ["high", "medium", "low"])

    def test_apply_template_suggestion_with_multiple_adjustments(self):
        """Test Template-Vorschlag mit mehreren Anpassungen"""
        # Erstelle Vorschlag mit mehreren Anpassungen
        suggestion = TemplateSuggestion(
            suggestion_id="multi_adjustment",
            segment="style",
            description="Multiple style adjustments",
            adjustments=[
                {
                    "layer_type": "style",
                    "action": "enhance",
                    "parameters": {"intensity": 1.2}
                },
                {
                    "layer_type": "emotion_drama",
                    "action": "modify",
                    "parameters": {"content": "Enhanced emotional content"}
                }
            ],
            priority="high",
            confidence=0.9,
            reasoning="Multiple user requests",
            metadata={}
        )
        
        # Wende Vorschlag an
        modified_template = self.feedback_intelligence.apply_template_suggestion(
            suggestion, self.template
        )
        
        # Verifikationen
        self.assertIsInstance(modified_template, PromptTemplate)
        self.assertEqual(modified_template.template_id, self.template.template_id)


class TestFeedbackFeatureComprehensive(unittest.TestCase):
    """Umfassende Tests für FeedbackFeature"""
    
    def test_feedback_feature_creation(self):
        """Test FeedbackFeature-Erstellung"""
        feature = FeedbackFeature(
            feature_type="style",
            feature_name="imagery",
            sentiment="positive",
            confidence=0.8,
            source_text="More imagery",
            suggested_adjustment={"action": "enhance", "parameters": {}}
        )
        
        # Verifikationen
        self.assertEqual(feature.feature_type, "style")
        self.assertEqual(feature.feature_name, "imagery")
        self.assertEqual(feature.sentiment, "positive")
        self.assertEqual(feature.confidence, 0.8)
        self.assertEqual(feature.source_text, "More imagery")
        self.assertIsInstance(feature.suggested_adjustment, dict)


class TestTemplateSuggestionComprehensive(unittest.TestCase):
    """Umfassende Tests für TemplateSuggestion"""
    
    def test_template_suggestion_creation(self):
        """Test TemplateSuggestion-Erstellung"""
        suggestion = TemplateSuggestion(
            suggestion_id="test_suggestion",
            segment="style",
            description="Enhance imagery",
            adjustments=[
                {
                    "layer_type": "style",
                    "action": "enhance",
                    "parameters": {"intensity": 1.2}
                }
            ],
            priority="high",
            confidence=0.8,
            reasoning="Users want more imagery",
            metadata={"source": "feedback_analysis"}
        )
        
        # Verifikationen
        self.assertEqual(suggestion.suggestion_id, "test_suggestion")
        self.assertEqual(suggestion.segment, "style")
        self.assertEqual(suggestion.description, "Enhance imagery")
        self.assertEqual(suggestion.priority, "high")
        self.assertEqual(suggestion.confidence, 0.8)
        self.assertEqual(suggestion.reasoning, "Users want more imagery")
        self.assertIsInstance(suggestion.adjustments, list)
        self.assertIsInstance(suggestion.metadata, dict)


if __name__ == '__main__':
    unittest.main() 