#!/usr/bin/env python3
"""
One Click Book Writer - Quality Evaluator
Version: 2.0.0
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class QualityEvaluator:
    """Bewertet die Qualität generierter Kapitel"""
    
    def __init__(self):
        # Gewichtungen für verschiedene Qualitätsaspekte
        self.weights = {
            "word_limit_compliance": 0.25,
            "core_emotion_presence": 0.20,
            "repetition_penalty": 0.15,
            "readability": 0.20,
            "structure_quality": 0.20
        }
        
        # Emotionale Schlüsselwörter (Deutsch/Englisch)
        self.emotion_keywords = {
            "de": {
                "wonder": ["staunen", "wundern", "verwundert", "erstaunt", "fasziniert"],
                "joy": ["freude", "fröhlich", "glücklich", "begeistert", "vergnügt"],
                "courage": ["mut", "mutig", "tapfer", "beherzt", "furchtlos"],
                "friendship": ["freundschaft", "freundlich", "verbunden", "gemeinsam"],
                "growth": ["wachsen", "lernen", "entwickeln", "reifen", "fortschritt"]
            },
            "en": {
                "wonder": ["wonder", "amazed", "astonished", "fascinated", "curious"],
                "joy": ["joy", "happy", "excited", "delighted", "cheerful"],
                "courage": ["courage", "brave", "bold", "fearless", "daring"],
                "friendship": ["friendship", "friendly", "together", "bond"],
                "growth": ["grow", "learn", "develop", "progress", "improve"]
            }
        }
    
    def evaluate_word_limit_compliance(self, text: str, target_words: int) -> Tuple[float, Dict]:
        """Bewertet die Einhaltung der Wortanzahl"""
        actual_words = len(text.split())
        
        if target_words == 0:
            return 1.0, {"actual_words": actual_words, "target_words": target_words}
        
        # Berechne Abweichung
        deviation = abs(actual_words - target_words) / target_words
        
        # Score: 1.0 bei perfekter Einhaltung, 0.0 bei 50%+ Abweichung
        score = max(0.0, 1.0 - (deviation * 2))
        
        return score, {
            "actual_words": actual_words,
            "target_words": target_words,
            "deviation_percent": round(deviation * 100, 2),
            "score": round(score, 3)
        }
    
    def evaluate_core_emotion_presence(self, text: str, target_emotion: str, language: str = "de") -> Tuple[float, Dict]:
        """Bewertet die Präsenz der Kernemotion"""
        if not target_emotion or language not in self.emotion_keywords:
            return 0.5, {"target_emotion": target_emotion, "language": language}
        
        # Normalisiere Emotion
        emotion = target_emotion.lower()
        
        # Finde passende Schlüsselwörter
        keywords = []
        for emotion_type, words in self.emotion_keywords[language].items():
            if emotion in emotion_type or emotion_type in emotion:
                keywords.extend(words)
        
        if not keywords:
            # Fallback: verwende alle Emotionen
            keywords = [word for words in self.emotion_keywords[language].values() for word in words]
        
        # Zähle Vorkommen
        text_lower = text.lower()
        word_count = Counter(text_lower.split())
        
        emotion_count = sum(word_count.get(keyword, 0) for keyword in keywords)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0, {"emotion_count": 0, "total_words": 0}
        
        # Score basierend auf Häufigkeit (optimal: 1-3% der Wörter)
        emotion_ratio = emotion_count / total_words
        optimal_ratio = 0.02  # 2%
        
        if emotion_ratio >= optimal_ratio:
            score = 1.0
        else:
            score = emotion_ratio / optimal_ratio
        
        return score, {
            "target_emotion": target_emotion,
            "emotion_count": emotion_count,
            "total_words": total_words,
            "emotion_ratio": round(emotion_ratio * 100, 3),
            "optimal_ratio": round(optimal_ratio * 100, 3),
            "score": round(score, 3)
        }
    
    def evaluate_repetition_penalty(self, text: str) -> Tuple[float, Dict]:
        """Bewertet Wiederholungen (Penalty)"""
        words = text.lower().split()
        
        if len(words) < 10:
            return 1.0, {"repetition_score": 1.0, "reason": "Text zu kurz"}
        
        # Zähle Wortwiederholungen
        word_count = Counter(words)
        total_words = len(words)
        
        # Berechne Wiederholungsrate
        unique_words = len(word_count)
        repetition_ratio = 1 - (unique_words / total_words)
        
        # Score: 1.0 bei wenig Wiederholungen, 0.0 bei vielen
        # Optimal: 20-30% Wiederholungen
        optimal_repetition = 0.25
        
        if repetition_ratio <= optimal_repetition:
            score = 1.0
        else:
            # Penalty für zu viele Wiederholungen
            penalty = (repetition_ratio - optimal_repetition) / (1 - optimal_repetition)
            score = max(0.0, 1.0 - penalty)
        
        return score, {
            "unique_words": unique_words,
            "total_words": total_words,
            "repetition_ratio": round(repetition_ratio * 100, 2),
            "optimal_repetition": round(optimal_repetition * 100, 2),
            "score": round(score, 3)
        }
    
    def evaluate_readability(self, text: str, target_audience: str = "children") -> Tuple[float, Dict]:
        """Bewertet die Lesbarkeit für die Zielgruppe"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0, {"readability_score": 0.0, "reason": "Keine Sätze gefunden"}
        
        # Durchschnittliche Satzlänge
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Zielgruppen-spezifische Bewertung
        if target_audience == "children":
            # Kinder: kurze Sätze (5-15 Wörter optimal)
            if avg_sentence_length <= 15:
                score = 1.0
            elif avg_sentence_length <= 25:
                score = 0.7
            else:
                score = 0.3
        else:
            # Erwachsene: flexibler (10-25 Wörter optimal)
            if 10 <= avg_sentence_length <= 25:
                score = 1.0
            elif 5 <= avg_sentence_length <= 35:
                score = 0.8
            else:
                score = 0.4
        
        return score, {
            "target_audience": target_audience,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "sentence_count": len(sentences),
            "score": round(score, 3)
        }
    
    def evaluate_structure_quality(self, text: str) -> Tuple[float, Dict]:
        """Bewertet die Strukturqualität"""
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            return 0.0, {"structure_score": 0.0, "reason": "Keine Absätze gefunden"}
        
        # Bewerte Absatzlänge
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraphs)
        
        # Optimal: 50-150 Wörter pro Absatz
        if 50 <= avg_paragraph_length <= 150:
            length_score = 1.0
        elif 30 <= avg_paragraph_length <= 200:
            length_score = 0.8
        else:
            length_score = 0.4
        
        # Bewerte Absatzanzahl (nicht zu wenig, nicht zu viele)
        if 2 <= len(paragraphs) <= 8:
            count_score = 1.0
        elif 1 <= len(paragraphs) <= 12:
            count_score = 0.7
        else:
            count_score = 0.3
        
        # Gesamtscore
        structure_score = (length_score + count_score) / 2
        
        return structure_score, {
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": round(avg_paragraph_length, 2),
            "length_score": round(length_score, 3),
            "count_score": round(count_score, 3),
            "structure_score": round(structure_score, 3)
        }
    
    def calculate_overall_quality_score(self, 
                                      text: str, 
                                      target_words: int,
                                      target_emotion: str,
                                      target_audience: str = "children",
                                      language: str = "de") -> Dict:
        """Berechnet den Gesamt-Qualitäts-Score"""
        
        # Einzelbewertungen
        word_limit_score, word_limit_details = self.evaluate_word_limit_compliance(text, target_words)
        emotion_score, emotion_details = self.evaluate_core_emotion_presence(text, target_emotion, language)
        repetition_score, repetition_details = self.evaluate_repetition_penalty(text)
        readability_score, readability_details = self.evaluate_readability(text, target_audience)
        structure_score, structure_details = self.evaluate_structure_quality(text)
        
        # Gewichteter Gesamtscore
        overall_score = (
            word_limit_score * self.weights["word_limit_compliance"] +
            emotion_score * self.weights["core_emotion_presence"] +
            repetition_score * self.weights["repetition_penalty"] +
            readability_score * self.weights["readability"] +
            structure_score * self.weights["structure_quality"]
        )
        
        # Qualitätsstufe bestimmen
        if overall_score >= 0.8:
            quality_level = "Excellent"
        elif overall_score >= 0.6:
            quality_level = "Good"
        elif overall_score >= 0.4:
            quality_level = "Fair"
        else:
            quality_level = "Poor"
        
        # Review-Gates und Schwellen
        review_required = overall_score < 0.7  # Review bei Score < 0.7
        critical_issues = overall_score < 0.5   # Kritische Probleme bei Score < 0.5
        
        # Spezifische Problem-Flags
        flags = []
        if word_limit_score < 0.6:
            flags.append("WORTLIMIT_PROBLEM")
        if emotion_score < 0.5:
            flags.append("EMOTION_PROBLEM")
        if repetition_score < 0.6:
            flags.append("REPETITION_PROBLEM")
        if readability_score < 0.6:
            flags.append("READABILITY_PROBLEM")
        if structure_score < 0.6:
            flags.append("STRUCTURE_PROBLEM")
        
        # Verbesserungsvorschläge
        suggestions = self._generate_improvement_suggestions({
            "word_limit": word_limit_score,
            "emotion": emotion_score,
            "repetition": repetition_score,
            "readability": readability_score,
            "structure": structure_score
        })
        
        return {
            "overall_score": round(overall_score, 3),
            "quality_level": quality_level,
            "review_required": review_required,
            "critical_issues": critical_issues,
            "flags": flags,
            "weights": self.weights,
            "individual_scores": {
                "word_limit_compliance": {
                    "score": round(word_limit_score, 3),
                    "details": word_limit_details
                },
                "core_emotion_presence": {
                    "score": round(emotion_score, 3),
                    "details": emotion_details
                },
                "repetition_penalty": {
                    "score": round(repetition_score, 3),
                    "details": repetition_details
                },
                "readability": {
                    "score": round(readability_score, 3),
                    "details": readability_details
                },
                "structure_quality": {
                    "score": round(structure_score, 3),
                    "details": structure_details
                }
            },
            "improvement_suggestions": suggestions
        }
    
    def _generate_improvement_suggestions(self, scores: Dict) -> List[str]:
        """Generiert Verbesserungsvorschläge basierend auf den Scores"""
        suggestions = []
        
        if scores["word_limit"] < 0.7:
            suggestions.append("Wortanzahl anpassen - Ziel besser einhalten")
        
        if scores["emotion"] < 0.6:
            suggestions.append("Kernemotion stärker hervorheben")
        
        if scores["repetition"] < 0.7:
            suggestions.append("Wortwiederholungen reduzieren")
        
        if scores["readability"] < 0.7:
            suggestions.append("Satzlänge für Zielgruppe optimieren")
        
        if scores["structure"] < 0.7:
            suggestions.append("Absatzstruktur verbessern")
        
        if not suggestions:
            suggestions.append("Text ist bereits von guter Qualität")
        
        return suggestions
    
    def evaluate_bilingual_content(self, 
                                 german_text: str, 
                                 english_text: str,
                                 prompt_frame: Dict) -> Dict:
        """Bewertet bilinguale Inhalte"""
        
        # Extrahiere Parameter aus PromptFrame
        target_words = prompt_frame.get('input', {}).get('chapter', {}).get('length_words', 800)
        target_emotion = prompt_frame.get('input', {}).get('emotions', {}).get('primary_emotion', 'wonder')
        target_audience = prompt_frame.get('input', {}).get('book', {}).get('target_audience', 'children')
        
        # Bewerte deutsche Version
        german_evaluation = self.calculate_overall_quality_score(
            german_text, target_words, target_emotion, target_audience, "de"
        )
        
        # Bewerte englische Version
        english_evaluation = self.calculate_overall_quality_score(
            english_text, target_words, target_emotion, target_audience, "en"
        )
        
        # Konsistenz zwischen den Versionen bewerten
        consistency_score = self._evaluate_translation_consistency(german_text, english_text)
        
        return {
            "german_evaluation": german_evaluation,
            "english_evaluation": english_evaluation,
            "consistency_score": consistency_score,
            "overall_bilingual_score": round(
                (german_evaluation["overall_score"] + english_evaluation["overall_score"] + consistency_score) / 3, 3
            )
        }
    
    def _evaluate_translation_consistency(self, german_text: str, english_text: str) -> float:
        """Bewertet die Konsistenz zwischen deutschen und englischen Versionen"""
        # Einfache Metriken für Konsistenz
        german_words = len(german_text.split())
        english_words = len(english_text.split())
        
        # Wortanzahl-Verhältnis
        if german_words == 0 or english_words == 0:
            return 0.0
        
        word_ratio = min(german_words, english_words) / max(german_words, english_words)
        
        # Absatzanzahl-Verhältnis
        german_paragraphs = len([p for p in german_text.split('\n\n') if p.strip()])
        english_paragraphs = len([p for p in english_text.split('\n\n') if p.strip()])
        
        if german_paragraphs == 0 or english_paragraphs == 0:
            paragraph_ratio = 0.0
        else:
            paragraph_ratio = min(german_paragraphs, english_paragraphs) / max(german_paragraphs, english_paragraphs)
        
        # Gesamtkonsistenz-Score
        consistency_score = (word_ratio + paragraph_ratio) / 2
        
        return round(consistency_score, 3) 