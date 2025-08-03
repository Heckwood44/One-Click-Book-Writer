#!/usr/bin/env python3
"""
Feedback Intelligence
Erweiterte Feedback-Analyse mit automatischer Feature-Extraktion und Template-Vorschlägen
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter

from core.architecture import FeedbackEntry, PromptTemplate
from core.layered_compiler import LayeredCompositionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FeedbackFeature:
    """Extrahiertes Feedback-Feature"""
    feature_type: str
    feature_name: str
    sentiment: str  # positive, negative, neutral
    confidence: float
    source_text: str
    suggested_adjustment: Dict[str, Any]

@dataclass
class TemplateSuggestion:
    """Template-Vorschlag basierend auf Feedback"""
    suggestion_id: str
    segment: str
    description: str
    adjustments: List[Dict[str, Any]]
    priority: str  # low, medium, high
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]

class FeedbackIntelligence:
    """Erweiterte Feedback-Intelligenz"""
    
    def __init__(self):
        self.compiler = LayeredCompositionEngine()
        self.feedback_history = []
        self.feature_patterns = self._load_feature_patterns()
        self.adjustment_mappings = self._load_adjustment_mappings()
        
    def _load_feature_patterns(self) -> Dict[str, Dict]:
        """Lädt Feature-Erkennungs-Patterns"""
        return {
            "imagery": {
                "patterns": [
                    r"\b(mehr|weniger)\s+(bildhaft|bildsprache|beschreibungen?)\b",
                    r"\b(visuell|anschaulich|lebendig)\b",
                    r"\b(bilder|metaphern|vergleiche)\b"
                ],
                "feature_type": "style",
                "layer": "style"
            },
            "sentence_length": {
                "patterns": [
                    r"\b(kürzere|längere)\s+(sätze?|satzlänge)\b",
                    r"\b(einfache|komplizierte)\s+(wörter?|sprache)\b",
                    r"\b(verständlich|komplex)\b"
                ],
                "feature_type": "readability",
                "layer": "target_audience"
            },
            "emotional_depth": {
                "patterns": [
                    r"\b(mehr|weniger)\s+(gefühle?|emotionen?|herz)\b",
                    r"\b(emotional|gefühlvoll|berührend)\b",
                    r"\b(verbindung|nähe|wärme)\b"
                ],
                "feature_type": "emotion",
                "layer": "emotion_drama"
            },
            "dialogue": {
                "patterns": [
                    r"\b(mehr|weniger)\s+(dialoge?|gespräche?)\b",
                    r"\b(gesprochene|direkte)\s+(sprache|rede)\b",
                    r"\b(unterhaltung|austausch)\b"
                ],
                "feature_type": "dialogue",
                "layer": "style"
            },
            "pacing": {
                "patterns": [
                    r"\b(schneller|langsamer)\s+(tempo|rhythmus)\b",
                    r"\b(spannend|ruhig|dynamisch)\b",
                    r"\b(aufregend|entspannend)\b"
                ],
                "feature_type": "pacing",
                "layer": "genre"
            },
            "character_development": {
                "patterns": [
                    r"\b(charaktere?|figuren?)\s+(entwicklung|tiefe)\b",
                    r"\b(sympathisch|interessant|realistisch)\b",
                    r"\b(identifikation|verbindung)\b"
                ],
                "feature_type": "character",
                "layer": "emotion_drama"
            },
            "plot_structure": {
                "patterns": [
                    r"\b(handlung|story|plot)\s+(struktur|aufbau)\b",
                    r"\b(spannungsbogen|höhepunkt|auflösung)\b",
                    r"\b(logisch|kohärent|schlüssig)\b"
                ],
                "feature_type": "structure",
                "layer": "genre"
            }
        }
    
    def _load_adjustment_mappings(self) -> Dict[str, Dict]:
        """Lädt Anpassungs-Mappings"""
        return {
            "imagery": {
                "positive": {
                    "layer_weight_adjustment": {"style": 1.3},
                    "content_addition": "Erhöhe bildhafte Sprache und Beschreibungen",
                    "few_shot_addition": "style_examples"
                },
                "negative": {
                    "layer_weight_adjustment": {"style": 0.8},
                    "content_addition": "Reduziere übermäßige Beschreibungen",
                    "few_shot_addition": "minimal_style"
                }
            },
            "sentence_length": {
                "positive": {
                    "layer_weight_adjustment": {"target_audience": 1.2},
                    "content_addition": "Verwende kürzere, klarere Sätze",
                    "few_shot_addition": "simple_sentences"
                },
                "negative": {
                    "layer_weight_adjustment": {"target_audience": 0.9},
                    "content_addition": "Erlaube komplexere Satzstrukturen",
                    "few_shot_addition": "complex_sentences"
                }
            },
            "emotional_depth": {
                "positive": {
                    "layer_weight_adjustment": {"emotion_drama": 1.4},
                    "content_addition": "Erhöhe emotionale Tiefe und Charakterverbindungen",
                    "few_shot_addition": "emotional_examples"
                },
                "negative": {
                    "layer_weight_adjustment": {"emotion_drama": 0.8},
                    "content_addition": "Reduziere übermäßige Emotionalität",
                    "few_shot_addition": "balanced_emotion"
                }
            },
            "dialogue": {
                "positive": {
                    "layer_weight_adjustment": {"style": 1.3},
                    "content_addition": "Erhöhe Dialog-Anteil und direkte Rede",
                    "few_shot_addition": "dialogue_examples"
                },
                "negative": {
                    "layer_weight_adjustment": {"style": 0.8},
                    "content_addition": "Reduziere Dialog-Anteil",
                    "few_shot_addition": "narrative_focus"
                }
            },
            "pacing": {
                "positive": {
                    "layer_weight_adjustment": {"genre": 1.2},
                    "content_addition": "Erhöhe Tempo und Spannung",
                    "few_shot_addition": "fast_pacing"
                },
                "negative": {
                    "layer_weight_adjustment": {"genre": 0.9},
                    "content_addition": "Verlangsame Tempo für mehr Tiefe",
                    "few_shot_addition": "slow_pacing"
                }
            },
            "character_development": {
                "positive": {
                    "layer_weight_adjustment": {"emotion_drama": 1.3},
                    "content_addition": "Vertiefe Charakterentwicklung und -verbindungen",
                    "few_shot_addition": "character_development"
                },
                "negative": {
                    "layer_weight_adjustment": {"emotion_drama": 0.8},
                    "content_addition": "Fokussiere mehr auf Handlung als Charaktere",
                    "few_shot_addition": "plot_focus"
                }
            },
            "plot_structure": {
                "positive": {
                    "layer_weight_adjustment": {"genre": 1.3},
                    "content_addition": "Verbessere Handlungsstruktur und Logik",
                    "few_shot_addition": "strong_plot"
                },
                "negative": {
                    "layer_weight_adjustment": {"genre": 0.8},
                    "content_addition": "Lass Handlung natürlicher fließen",
                    "few_shot_addition": "organic_plot"
                }
            }
        }
    
    def analyze_feedback(self, feedback_entries: List[FeedbackEntry]) -> List[FeedbackFeature]:
        """Analysiert Feedback und extrahiert Features"""
        features = []
        
        for entry in feedback_entries:
            # Analysiere Kommentar
            comment_features = self._extract_features_from_text(entry.comment)
            features.extend(comment_features)
            
            # Analysiere Rating
            rating_features = self._extract_features_from_rating(entry.user_rating, entry.comment)
            features.extend(rating_features)
        
        # Gruppiere ähnliche Features
        grouped_features = self._group_similar_features(features)
        
        return grouped_features
    
    def _extract_features_from_text(self, text: str) -> List[FeedbackFeature]:
        """Extrahiert Features aus Text"""
        features = []
        text_lower = text.lower()
        
        for feature_name, pattern_config in self.feature_patterns.items():
            for pattern in pattern_config["patterns"]:
                matches = re.finditer(pattern, text_lower)
                
                for match in matches:
                    # Bestimme Sentiment
                    sentiment = self._determine_sentiment(match.group(), text_lower)
                    
                    # Berechne Confidence
                    confidence = self._calculate_confidence(match.group(), text_lower)
                    
                    # Erstelle Feature
                    feature = FeedbackFeature(
                        feature_type=pattern_config["feature_type"],
                        feature_name=feature_name,
                        sentiment=sentiment,
                        confidence=confidence,
                        source_text=match.group(),
                        suggested_adjustment=self._get_suggested_adjustment(feature_name, sentiment)
                    )
                    
                    features.append(feature)
        
        return features
    
    def _extract_features_from_rating(self, rating: int, comment: str) -> List[FeedbackFeature]:
        """Extrahiert Features aus Rating"""
        features = []
        
        # Rating-basierte Features
        if rating >= 4:
            # Positives Rating - suche nach positiven Aspekten
            positive_patterns = [
                r"\b(gut|toll|super|exzellent|wunderbar)\b",
                r"\b(gefällt|mag|liebe)\b",
                r"\b(perfekt|ideal|optimal)\b"
            ]
            
            for pattern in positive_patterns:
                if re.search(pattern, comment.lower()):
                    features.append(FeedbackFeature(
                        feature_type="general",
                        feature_name="positive_feedback",
                        sentiment="positive",
                        confidence=0.8,
                        source_text="Positives Rating",
                        suggested_adjustment={"action": "maintain_current_approach"}
                    ))
        
        elif rating <= 2:
            # Negatives Rating - suche nach Verbesserungsbereichen
            negative_patterns = [
                r"\b(schlecht|schwierig|kompliziert|langweilig)\b",
                r"\b(verbessern|ändern|anders)\b",
                r"\b(nicht|kein|weniger)\b"
            ]
            
            for pattern in negative_patterns:
                if re.search(pattern, comment.lower()):
                    features.append(FeedbackFeature(
                        feature_type="general",
                        feature_name="improvement_needed",
                        sentiment="negative",
                        confidence=0.7,
                        source_text="Negatives Rating",
                        suggested_adjustment={"action": "investigate_issues"}
                    ))
        
        return features
    
    def _determine_sentiment(self, matched_text: str, full_text: str) -> str:
        """Bestimmt Sentiment des gematchten Texts"""
        positive_indicators = ["mehr", "besser", "gut", "toll", "super", "liebe", "mag"]
        negative_indicators = ["weniger", "schlecht", "nicht", "kein", "schwierig", "kompliziert"]
        
        matched_lower = matched_text.lower()
        
        # Prüfe direkte Indikatoren
        for indicator in positive_indicators:
            if indicator in matched_lower:
                return "positive"
        
        for indicator in negative_indicators:
            if indicator in matched_lower:
                return "negative"
        
        # Prüfe Kontext
        context_words = full_text.split()
        matched_index = -1
        
        for i, word in enumerate(context_words):
            if matched_text.lower() in word.lower():
                matched_index = i
                break
        
        if matched_index >= 0:
            # Prüfe umgebende Wörter
            start = max(0, matched_index - 3)
            end = min(len(context_words), matched_index + 4)
            context = " ".join(context_words[start:end])
            
            positive_count = sum(1 for word in positive_indicators if word in context.lower())
            negative_count = sum(1 for word in negative_indicators if word in context.lower())
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
        
        return "neutral"
    
    def _calculate_confidence(self, matched_text: str, full_text: str) -> float:
        """Berechnet Confidence für Feature-Extraktion"""
        # Basis-Confidence basierend auf Match-Qualität
        base_confidence = 0.6
        
        # Erhöhe Confidence für spezifische Matches
        if len(matched_text.split()) >= 2:
            base_confidence += 0.2
        
        # Erhöhe Confidence für eindeutige Begriffe
        specific_terms = ["bildhaft", "emotionen", "dialoge", "charaktere", "handlung"]
        if any(term in matched_text.lower() for term in specific_terms):
            base_confidence += 0.1
        
        # Reduziere Confidence für vage Begriffe
        vague_terms = ["gut", "schlecht", "besser", "anders"]
        if any(term in matched_text.lower() for term in vague_terms):
            base_confidence -= 0.1
        
        return min(0.95, max(0.3, base_confidence))
    
    def _get_suggested_adjustment(self, feature_name: str, sentiment: str) -> Dict[str, Any]:
        """Gibt vorgeschlagene Anpassung für Feature zurück"""
        if feature_name in self.adjustment_mappings:
            feature_mappings = self.adjustment_mappings[feature_name]
            if sentiment in feature_mappings:
                return feature_mappings[sentiment]
        
        # Default-Anpassung
        return {
            "action": "investigate",
            "layer_weight_adjustment": {},
            "content_addition": "Weitere Analyse erforderlich"
        }
    
    def _group_similar_features(self, features: List[FeedbackFeature]) -> List[FeedbackFeature]:
        """Gruppiert ähnliche Features"""
        if not features:
            return features
        
        # Gruppiere nach Feature-Name und Sentiment
        grouped = {}
        
        for feature in features:
            key = (feature.feature_name, feature.sentiment)
            
            if key not in grouped:
                grouped[key] = feature
            else:
                # Kombiniere Features mit höherer Confidence
                existing = grouped[key]
                if feature.confidence > existing.confidence:
                    grouped[key] = feature
                elif feature.confidence == existing.confidence:
                    # Kombiniere suggested_adjustments
                    existing.suggested_adjustment.update(feature.suggested_adjustment)
        
        return list(grouped.values())
    
    def generate_template_suggestions(self, 
                                    segment: str,
                                    features: List[FeedbackFeature],
                                    current_template: PromptTemplate) -> List[TemplateSuggestion]:
        """Generiert Template-Vorschläge basierend auf Feedback-Features"""
        suggestions = []
        
        # Gruppiere Features nach Priorität
        high_priority_features = [f for f in features if f.confidence >= 0.8]
        medium_priority_features = [f for f in features if 0.6 <= f.confidence < 0.8]
        low_priority_features = [f for f in features if f.confidence < 0.6]
        
        # Erstelle Vorschläge für hohe Priorität
        if high_priority_features:
            suggestions.append(self._create_suggestion(
                segment, high_priority_features, "high", current_template
            ))
        
        # Erstelle Vorschläge für mittlere Priorität
        if medium_priority_features:
            suggestions.append(self._create_suggestion(
                segment, medium_priority_features, "medium", current_template
            ))
        
        # Erstelle Vorschläge für niedrige Priorität
        if low_priority_features:
            suggestions.append(self._create_suggestion(
                segment, low_priority_features, "low", current_template
            ))
        
        return suggestions
    
    def _create_suggestion(self, 
                          segment: str,
                          features: List[FeedbackFeature],
                          priority: str,
                          current_template: PromptTemplate) -> TemplateSuggestion:
        """Erstellt Template-Vorschlag"""
        # Sammle alle Anpassungen
        adjustments = []
        reasoning_parts = []
        
        for feature in features:
            if feature.suggested_adjustment:
                adjustments.append(feature.suggested_adjustment)
                reasoning_parts.append(f"{feature.feature_name}: {feature.sentiment}")
        
        # Berechne durchschnittliche Confidence
        avg_confidence = sum(f.confidence for f in features) / len(features)
        
        # Erstelle Suggestion-ID
        suggestion_id = f"suggestion_{segment}_{priority}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return TemplateSuggestion(
            suggestion_id=suggestion_id,
            segment=segment,
            description=f"Template-Anpassung basierend auf {len(features)} Feedback-Features",
            adjustments=adjustments,
            priority=priority,
            confidence=avg_confidence,
            reasoning="; ".join(reasoning_parts),
            metadata={
                "feature_count": len(features),
                "current_template_hash": current_template.get_hash(),
                "generation_timestamp": datetime.now().isoformat()
            }
        )
    
    def apply_template_suggestion(self, 
                                suggestion: TemplateSuggestion,
                                current_template: PromptTemplate) -> PromptTemplate:
        """Wendet Template-Vorschlag an"""
        # Erstelle neue Layer basierend auf Anpassungen
        new_layers = []
        
        for layer in current_template.layers:
            # Prüfe ob Layer angepasst werden soll
            layer_adjustment = self._find_layer_adjustment(layer.layer_type.value, suggestion.adjustments)
            
            if layer_adjustment:
                # Wende Anpassung an
                adjusted_layer = self._apply_layer_adjustment(layer, layer_adjustment)
                new_layers.append(adjusted_layer)
            else:
                # Behalte Layer unverändert
                new_layers.append(layer)
        
        # Erstelle neues Template
        from core.architecture import PromptTemplate
        return PromptTemplate(
            template_id=f"{current_template.template_id}_suggested_{suggestion.suggestion_id}",
            name=f"{current_template.name} (Vorgeschlagen)",
            description=f"Template basierend auf Feedback-Vorschlag: {suggestion.reasoning}",
            layers=new_layers,
            version=f"{current_template.version}_suggested",
            metadata={
                "original_template": current_template.template_id,
                "suggestion_id": suggestion.suggestion_id,
                "confidence": suggestion.confidence,
                "priority": suggestion.priority,
                "reasoning": suggestion.reasoning
            }
        )
    
    def _find_layer_adjustment(self, layer_type: str, adjustments: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Findet Anpassung für spezifischen Layer"""
        for adjustment in adjustments:
            if "layer_weight_adjustment" in adjustment:
                weight_adjustments = adjustment["layer_weight_adjustment"]
                if layer_type in weight_adjustments:
                    return adjustment
        
        return None
    
    def _apply_layer_adjustment(self, layer, adjustment: Dict[str, Any]) -> Any:
        """Wendet Layer-Anpassung an"""
        # Erstelle neuen Layer mit angepasstem Gewicht
        weight_adjustments = adjustment.get("layer_weight_adjustment", {})
        layer_type = layer.layer_type.value
        
        if layer_type in weight_adjustments:
            new_weight = layer.weight * weight_adjustments[layer_type]
        else:
            new_weight = layer.weight
        
        # Füge Content-Anpassung hinzu
        content_addition = adjustment.get("content_addition", "")
        new_content = layer.content
        
        if content_addition:
            new_content += f"\n\nFEEDBACK-ANPASSUNG:\n{content_addition}"
        
        # Erstelle neuen Layer
        from core.architecture import Layer
        return Layer(
            layer_type=layer.layer_type,
            content=new_content,
            weight=new_weight,
            version=f"{layer.version}_adjusted",
            metadata={
                **layer.metadata,
                "feedback_adjustment": adjustment,
                "adjustment_timestamp": datetime.now().isoformat()
            }
        )
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Gibt Feedback-Zusammenfassung zurück"""
        return {
            "total_feedback_analyzed": len(self.feedback_history),
            "feature_distribution": self._get_feature_distribution(),
            "sentiment_distribution": self._get_sentiment_distribution(),
            "suggestion_count": len([f for f in self.feedback_history if hasattr(f, 'suggestions')]),
            "avg_confidence": self._calculate_avg_confidence()
        }
    
    def _get_feature_distribution(self) -> Dict[str, int]:
        """Gibt Verteilung der Features zurück"""
        distribution = Counter()
        for feedback in self.feedback_history:
            if hasattr(feedback, 'features'):
                for feature in feedback.features:
                    distribution[feature.feature_name] += 1
        return dict(distribution)
    
    def _get_sentiment_distribution(self) -> Dict[str, int]:
        """Gibt Verteilung der Sentiments zurück"""
        distribution = Counter()
        for feedback in self.feedback_history:
            if hasattr(feedback, 'features'):
                for feature in feedback.features:
                    distribution[feature.sentiment] += 1
        return dict(distribution)
    
    def _calculate_avg_confidence(self) -> float:
        """Berechnet durchschnittliche Confidence"""
        confidences = []
        for feedback in self.feedback_history:
            if hasattr(feedback, 'features'):
                for feature in feedback.features:
                    confidences.append(feature.confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.0 