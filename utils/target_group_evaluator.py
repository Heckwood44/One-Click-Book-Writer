#!/usr/bin/env python3
"""
Target Group Evaluator
Zielgruppenspezifische Evaluatoren für verschiedene Altersklassen und Genres
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EvaluationCriteria:
    """Evaluationskriterien für Zielgruppen"""
    readability_score: float
    age_appropriateness: float
    genre_compliance: float
    emotional_depth: float
    engagement_score: float
    overall_score: float
    flags: List[str]
    recommendations: List[str]

class TargetGroupEvaluator:
    """Zielgruppenspezifischer Evaluator"""
    
    def __init__(self):
        self.age_profiles = self._load_age_profiles()
        self.genre_profiles = self._load_genre_profiles()
    
    def _load_age_profiles(self) -> Dict:
        """Lädt Altersklassen-Profile"""
        try:
            with open("profiles/age_group_profiles.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Altersklassen-Profile: {e}")
            return {}
    
    def _load_genre_profiles(self) -> Dict:
        """Lädt Genre-Profile"""
        try:
            with open("profiles/genre_profiles.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Genre-Profile: {e}")
            return {}
    
    def evaluate_for_target_group(self, 
                                text: str,
                                age_group: str,
                                genre: str,
                                language: str = "de") -> EvaluationCriteria:
        """
        Evaluiert Text für spezifische Zielgruppe
        
        Args:
            text: Zu evaluierender Text
            age_group: Altersklasse (preschool, early_reader, middle_grade, young_adult, adult)
            genre: Genre (adventure, fantasy, self_discovery, mystery, friendship, educational, self_help)
            language: Sprache (de, en)
        """
        try:
            # Lade Profile
            age_profile = self.age_profiles.get("age_groups", {}).get(age_group, {})
            genre_profile = self.genre_profiles.get("genres", {}).get(genre, {})
            
            if not age_profile or not genre_profile:
                raise ValueError(f"Profil nicht gefunden: age_group={age_group}, genre={genre}")
            
            # Führe zielgruppenspezifische Evaluationen durch
            readability_score = self._evaluate_readability(text, age_profile, language)
            age_appropriateness = self._evaluate_age_appropriateness(text, age_profile, language)
            genre_compliance = self._evaluate_genre_compliance(text, genre_profile, language)
            emotional_depth = self._evaluate_emotional_depth(text, age_profile, genre_profile, language)
            engagement_score = self._evaluate_engagement(text, age_profile, genre_profile, language)
            
            # Berechne Gesamtscore
            overall_score = self._calculate_overall_score(
                readability_score, age_appropriateness, genre_compliance, 
                emotional_depth, engagement_score, age_group, genre
            )
            
            # Generiere Flags und Empfehlungen
            flags = self._generate_flags(
                readability_score, age_appropriateness, genre_compliance,
                emotional_depth, engagement_score, age_group, genre
            )
            
            recommendations = self._generate_recommendations(
                readability_score, age_appropriateness, genre_compliance,
                emotional_depth, engagement_score, age_group, genre
            )
            
            return EvaluationCriteria(
                readability_score=readability_score,
                age_appropriateness=age_appropriateness,
                genre_compliance=genre_compliance,
                emotional_depth=emotional_depth,
                engagement_score=engagement_score,
                overall_score=overall_score,
                flags=flags,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Fehler bei zielgruppenspezifischer Evaluation: {e}")
            return EvaluationCriteria(
                readability_score=0.0,
                age_appropriateness=0.0,
                genre_compliance=0.0,
                emotional_depth=0.0,
                engagement_score=0.0,
                overall_score=0.0,
                flags=["EVALUATION_ERROR"],
                recommendations=[f"Evaluation-Fehler: {str(e)}"]
            )
    
    def _evaluate_readability(self, text: str, age_profile: Dict, language: str) -> float:
        """Evaluiert Lesbarkeit für Altersgruppe"""
        readability = age_profile.get("readability", {})
        target_words = readability.get("target_words", 800)
        max_sentence_length = readability.get("max_sentence_length", 20)
        vocabulary_level = readability.get("vocabulary_level", "intermediate")
        
        # Wortanzahl-Evaluation
        word_count = len(text.split())
        word_count_score = self._calculate_word_count_score(word_count, target_words)
        
        # Satzlängen-Evaluation
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        sentence_length_score = self._calculate_sentence_length_score(avg_sentence_length, max_sentence_length)
        
        # Vokabular-Evaluation
        vocabulary_score = self._evaluate_vocabulary_complexity(text, vocabulary_level, language)
        
        # Gewichtete Summe
        readability_score = (
            word_count_score * 0.3 +
            sentence_length_score * 0.4 +
            vocabulary_score * 0.3
        )
        
        return min(readability_score, 1.0)
    
    def _calculate_word_count_score(self, actual_words: int, target_words: int) -> float:
        """Berechnet Wortanzahl-Score"""
        if target_words == 0:
            return 1.0
        
        ratio = actual_words / target_words
        
        if 0.8 <= ratio <= 1.2:  # Optimaler Bereich
            return 1.0
        elif 0.6 <= ratio <= 1.4:  # Akzeptabler Bereich
            return 0.8
        elif 0.4 <= ratio <= 1.6:  # Tolerierbarer Bereich
            return 0.6
        else:  # Zu kurz oder zu lang
            return 0.3
    
    def _calculate_sentence_length_score(self, avg_length: float, max_length: int) -> float:
        """Berechnet Satzlängen-Score"""
        if avg_length <= max_length:
            # Kürzere Sätze sind besser für jüngere Leser
            optimal_length = max_length * 0.7
            if avg_length <= optimal_length:
                return 1.0
            else:
                # Lineare Abnahme
                return 1.0 - ((avg_length - optimal_length) / (max_length - optimal_length)) * 0.3
        else:
            # Zu lange Sätze
            return max(0.0, 1.0 - ((avg_length - max_length) / max_length) * 0.7)
    
    def _evaluate_vocabulary_complexity(self, text: str, target_level: str, language: str) -> float:
        """Evaluiert Vokabular-Komplexität"""
        # Einfache Komplexitäts-Bewertung basierend auf Wortlänge
        words = text.split()
        if not words:
            return 1.0
        
        # Zähle komplexe Wörter (basierend auf Länge)
        complex_word_thresholds = {
            "basic": 8,      # Vorschule
            "elementary": 10, # Erstleser
            "intermediate": 12, # Mittelstufe
            "advanced": 15,   # Jugendliche
            "sophisticated": 18 # Erwachsene
        }
        
        threshold = complex_word_thresholds.get(target_level, 12)
        complex_words = [w for w in words if len(w) > threshold]
        complexity_ratio = len(complex_words) / len(words)
        
        # Bewerte basierend auf Zielgruppe
        if target_level == "basic":
            return max(0.0, 1.0 - complexity_ratio * 5)  # Wenige komplexe Wörter
        elif target_level == "elementary":
            return max(0.0, 1.0 - complexity_ratio * 3)
        elif target_level == "intermediate":
            return max(0.0, 1.0 - complexity_ratio * 2)
        elif target_level == "advanced":
            return max(0.0, 1.0 - complexity_ratio * 1.5)
        else:  # sophisticated
            return max(0.0, 1.0 - complexity_ratio)  # Mehr komplexe Wörter erlaubt
    
    def _evaluate_age_appropriateness(self, text: str, age_profile: Dict, language: str) -> float:
        """Evaluiert Altersgerechtheit"""
        constraints = age_profile.get("content_constraints", {})
        avoid_items = constraints.get("avoid", [])
        emphasize_items = constraints.get("emphasize", [])
        
        score = 1.0
        
        # Prüfe auf zu vermeidende Elemente
        for avoid_item in avoid_items:
            if self._contains_inappropriate_content(text, avoid_item, language):
                score -= 0.2  # Strafpunkte für unangemessene Inhalte
        
        # Prüfe auf zu betonende Elemente
        emphasize_count = 0
        for emphasize_item in emphasize_items:
            if self._contains_appropriate_content(text, emphasize_item, language):
                emphasize_count += 1
        
        # Bonus für angemessene Inhalte
        if emphasize_items:
            emphasize_ratio = emphasize_count / len(emphasize_items)
            score += emphasize_ratio * 0.3
        
        return max(0.0, min(score, 1.0))
    
    def _contains_inappropriate_content(self, text: str, content_type: str, language: str) -> bool:
        """Prüft auf unangemessene Inhalte"""
        inappropriate_patterns = {
            "complex_emotions": [r"\b(verzweiflung|despair|hoffnungslos|hopeless)\b"],
            "abstract_concepts": [r"\b(philosophie|philosophy|metaphysik|metaphysics)\b"],
            "explicit_violence": [r"\b(blut|blood|gewalt|violence|kampf|fight)\b"],
            "romantic_relationships": [r"\b(kuss|kiss|verliebt|in love|beziehung|relationship)\b"],
            "cynical_views": [r"\b(hoffnungslos|hopeless|sinnlos|meaningless|nutzlos|useless)\b"]
        }
        
        patterns = inappropriate_patterns.get(content_type, [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_appropriate_content(self, text: str, content_type: str, language: str) -> bool:
        """Prüft auf angemessene Inhalte"""
        appropriate_patterns = {
            "safety": [r"\b(sicher|safe|geschützt|protected|geborgen|secure)\b"],
            "friendship": [r"\b(freundschaft|friendship|freund|friend|verbunden|connected)\b"],
            "discovery": [r"\b(entdecken|discover|neugierig|curious|erforschen|explore)\b"],
            "colors": [r"\b(rot|red|blau|blue|grün|green|gelb|yellow|bunt|colorful)\b"],
            "animals": [r"\b(tier|animal|hund|dog|katze|cat|vogel|bird)\b"],
            "problem_solving": [r"\b(lösen|solve|finden|find|herausfinden|figure out)\b"],
            "courage": [r"\b(mut|courage|tapfer|brave|stark|strong)\b"],
            "learning": [r"\b(lernen|learn|verstehen|understand|wissen|know)\b"]
        }
        
        patterns = appropriate_patterns.get(content_type, [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _evaluate_genre_compliance(self, text: str, genre_profile: Dict, language: str) -> float:
        """Evaluiert Genre-Compliance"""
        conventions = genre_profile.get("conventions", {})
        tropes = conventions.get("tropes", [])
        emotional_focus = genre_profile.get("emotional_focus", [])
        
        score = 0.0
        total_elements = 0
        
        # Prüfe Genre-Tropes
        for trope in tropes:
            total_elements += 1
            if self._contains_genre_trope(text, trope, language):
                score += 1
        
        # Prüfe emotionale Schwerpunkte
        for emotion in emotional_focus:
            total_elements += 1
            if self._contains_emotion(text, emotion, language):
                score += 1
        
        # Prüfe Genre-spezifische Stilrichtlinien
        style_guidelines = genre_profile.get("style_guidelines", {})
        tone = style_guidelines.get("tone", "")
        if self._matches_genre_tone(text, tone, language):
            score += 1
            total_elements += 1
        
        return score / max(total_elements, 1)
    
    def _contains_genre_trope(self, text: str, trope: str, language: str) -> bool:
        """Prüft auf Genre-Tropes"""
        trope_patterns = {
            "quest": [r"\b(suche|quest|mission|auftrag|task)\b"],
            "journey": [r"\b(reise|journey|weg|way|unterwegs|on the way)\b"],
            "obstacles": [r"\b(hindernis|obstacle|herausforderung|challenge|problem)\b"],
            "magic": [r"\b(magie|magic|zauber|spell|magisch|magical)\b"],
            "prophecy": [r"\b(prophezeiung|prophecy|vorhersage|prediction)\b"],
            "clues": [r"\b(hinweis|clue|spur|trace|beweis|evidence)\b"],
            "detective_work": [r"\b(ermittlung|investigation|detektiv|detective)\b"],
            "learning_experience": [r"\b(lernerfahrung|learning experience|experiment|experiment)\b"]
        }
        
        patterns = trope_patterns.get(trope, [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_emotion(self, text: str, emotion: str, language: str) -> bool:
        """Prüft auf emotionale Elemente"""
        emotion_patterns = {
            "courage": [r"\b(mut|courage|tapfer|brave|stark|strong)\b"],
            "determination": [r"\b(entschlossen|determined|beharrlich|persistent)\b"],
            "friendship": [r"\b(freundschaft|friendship|freund|friend)\b"],
            "overcoming_fears": [r"\b(angst überwinden|overcome fear|mutig werden|become brave)\b"],
            "wonder": [r"\b(wunder|wonder|erstaunlich|amazing|magisch|magical)\b"],
            "awe": [r"\b(ehrfurcht|awe|beeindruckend|impressive)\b"],
            "curiosity": [r"\b(neugierig|curious|interessiert|interested)\b"],
            "suspense": [r"\b(spannung|suspense|spannend|exciting)\b"]
        }
        
        patterns = emotion_patterns.get(emotion, [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _matches_genre_tone(self, text: str, tone: str, language: str) -> bool:
        """Prüft auf Genre-typischen Ton"""
        tone_patterns = {
            "exciting": [r"\b(spannend|exciting|aufregend|thrilling)\b"],
            "suspenseful": [r"\b(spannungsvoll|suspenseful|gespannt|tense)\b"],
            "wondrous": [r"\b(wunderbar|wondrous|magisch|magical)\b"],
            "mystical": [r"\b(mystisch|mystical|geheimnisvoll|mysterious)\b"],
            "reflective": [r"\b(nachdenklich|reflective|überlegend|contemplative)\b"],
            "authentic": [r"\b(authentisch|authentic|echt|genuine)\b"],
            "warm": [r"\b(warm|warm|herzlich|heartfelt)\b"],
            "supportive": [r"\b(unterstützend|supportive|hilfreich|helpful)\b"]
        }
        
        patterns = tone_patterns.get(tone, [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _evaluate_emotional_depth(self, text: str, age_profile: Dict, genre_profile: Dict, language: str) -> float:
        """Evaluiert emotionale Tiefe"""
        # Zähle emotionale Wörter
        emotional_words = self._count_emotional_words(text, language)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        emotional_ratio = emotional_words / total_words
        
        # Bewerte basierend auf Altersgruppe
        age_group = age_profile.get("age_range", "")
        if "3-5" in age_group or "6-8" in age_group:
            # Jüngere Leser: Moderate emotionale Tiefe
            target_ratio = 0.03
        elif "9-12" in age_group:
            # Mittelstufe: Erhöhte emotionale Tiefe
            target_ratio = 0.05
        elif "13-17" in age_group:
            # Jugendliche: Hohe emotionale Tiefe
            target_ratio = 0.08
        else:
            # Erwachsene: Sehr hohe emotionale Tiefe
            target_ratio = 0.10
        
        # Berechne Score
        if emotional_ratio >= target_ratio:
            return 1.0
        else:
            return emotional_ratio / target_ratio
    
    def _count_emotional_words(self, text: str, language: str) -> int:
        """Zählt emotionale Wörter"""
        emotional_patterns = [
            r"\b(freude|joy|glück|happiness|liebe|love|wunder|wonder)\b",
            r"\b(mut|courage|stark|strong|tapfer|brave|entschlossen|determined)\b",
            r"\b(freundschaft|friendship|herz|heart|warm|warmth|verbunden|connected)\b",
            r"\b(lachen|laugh|spaß|fun|spielen|play|träumen|dream)\b",
            r"\b(angst|fear|sorgen|worries|traurig|sad|einsam|lonely)\b",
            r"\b(hoffnung|hope|vertrauen|trust|glauben|believe|vertrauen|confidence)\b"
        ]
        
        count = 0
        for pattern in emotional_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    def _evaluate_engagement(self, text: str, age_profile: Dict, genre_profile: Dict, language: str) -> float:
        """Evaluiert Engagement-Faktoren"""
        engagement_factors = []
        
        # Dialog-Anteil
        dialogue_ratio = self._calculate_dialogue_ratio(text)
        engagement_factors.append(dialogue_ratio)
        
        # Aktive Verben
        active_verb_ratio = self._calculate_active_verb_ratio(text, language)
        engagement_factors.append(active_verb_ratio)
        
        # Bildhafte Sprache
        imagery_ratio = self._calculate_imagery_ratio(text, language)
        engagement_factors.append(imagery_ratio)
        
        # Strukturierte Handlung
        structure_score = self._evaluate_story_structure(text, genre_profile)
        engagement_factors.append(structure_score)
        
        return sum(engagement_factors) / len(engagement_factors)
    
    def _calculate_dialogue_ratio(self, text: str) -> float:
        """Berechnet Dialog-Anteil"""
        dialogue_patterns = [
            r'"[^"]*"',  # Deutsche Anführungszeichen
            r'"[^"]*"',  # Englische Anführungszeichen
            r'„[^"]*"',  # Deutsche Anführungszeichen
            r'"[^"]*"',  # Deutsche Anführungszeichen
        ]
        
        dialogue_chars = 0
        for pattern in dialogue_patterns:
            matches = re.findall(pattern, text)
            dialogue_chars += sum(len(match) for match in matches)
        
        return min(dialogue_chars / max(len(text), 1), 0.5)  # Max 50% Dialog
    
    def _calculate_active_verb_ratio(self, text: str, language: str) -> float:
        """Berechnet Anteil aktiver Verben"""
        active_verbs = [
            r"\b(rennen|run|springen|jump|fliegen|fly|tanzen|dance)\b",
            r"\b(entdecken|discover|erforschen|explore|finden|find)\b",
            r"\b(lachen|laugh|spielen|play|singen|sing)\b",
            r"\b(helfen|help|retten|save|schützen|protect)\b"
        ]
        
        total_verbs = len(re.findall(r"\b\w+[te|st|en|t]\b", text, re.IGNORECASE))
        if total_verbs == 0:
            return 0.5
        
        active_verb_count = 0
        for pattern in active_verbs:
            active_verb_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return min(active_verb_count / total_verbs, 1.0)
    
    def _calculate_imagery_ratio(self, text: str, language: str) -> float:
        """Berechnet Anteil bildhafter Sprache"""
        imagery_patterns = [
            r"\b(leuchtend|bright|glitzernd|sparkling|funkelnd|twinkling)\b",
            r"\b(weich|soft|sanft|gentle|warm|warm)\b",
            r"\b(groß|big|klein|small|riesig|huge)\b",
            r"\b(schnell|fast|langsam|slow|leise|quiet)\b",
            r"\b(bunt|colorful|dunkel|dark|hell|bright)\b"
        ]
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        imagery_count = 0
        for pattern in imagery_patterns:
            imagery_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return min(imagery_count / total_words * 10, 1.0)  # Skaliert
    
    def _evaluate_story_structure(self, text: str, genre_profile: Dict) -> float:
        """Evaluiert Geschichtenstruktur"""
        # Einfache Struktur-Evaluation basierend auf Absätzen
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 3:
            return 0.3  # Zu wenig Struktur
        elif len(paragraphs) < 5:
            return 0.7  # Grundlegende Struktur
        else:
            return 1.0  # Gute Struktur
    
    def _calculate_overall_score(self, 
                               readability: float,
                               age_appropriateness: float,
                               genre_compliance: float,
                               emotional_depth: float,
                               engagement: float,
                               age_group: str,
                               genre: str) -> float:
        """Berechnet Gesamtscore mit gewichteter Summe"""
        
        # Gewichte basierend auf Altersgruppe und Genre
        weights = {
            "readability": 0.25,
            "age_appropriateness": 0.25,
            "genre_compliance": 0.20,
            "emotional_depth": 0.15,
            "engagement": 0.15
        }
        
        # Anpasse Gewichte basierend auf Altersgruppe
        if age_group == "preschool":
            weights["age_appropriateness"] = 0.35
            weights["readability"] = 0.30
        elif age_group == "young_adult":
            weights["emotional_depth"] = 0.25
            weights["genre_compliance"] = 0.25
        
        # Anpasse Gewichte basierend auf Genre
        if genre == "fantasy":
            weights["genre_compliance"] = 0.25
        elif genre == "educational":
            weights["readability"] = 0.30
        
        # Berechne gewichtete Summe
        overall_score = (
            readability * weights["readability"] +
            age_appropriateness * weights["age_appropriateness"] +
            genre_compliance * weights["genre_compliance"] +
            emotional_depth * weights["emotional_depth"] +
            engagement * weights["engagement"]
        )
        
        return min(overall_score, 1.0)
    
    def _generate_flags(self, 
                       readability: float,
                       age_appropriateness: float,
                       genre_compliance: float,
                       emotional_depth: float,
                       engagement: float,
                       age_group: str,
                       genre: str) -> List[str]:
        """Generiert Flags basierend auf Evaluation"""
        flags = []
        
        if readability < 0.6:
            flags.append("LOW_READABILITY")
        if age_appropriateness < 0.7:
            flags.append("AGE_INAPPROPRIATE")
        if genre_compliance < 0.5:
            flags.append("GENRE_MISMATCH")
        if emotional_depth < 0.4:
            flags.append("LOW_EMOTIONAL_DEPTH")
        if engagement < 0.5:
            flags.append("LOW_ENGAGEMENT")
        
        return flags
    
    def _generate_recommendations(self, 
                                readability: float,
                                age_appropriateness: float,
                                genre_compliance: float,
                                emotional_depth: float,
                                engagement: float,
                                age_group: str,
                                genre: str) -> List[str]:
        """Generiert Empfehlungen basierend auf Evaluation"""
        recommendations = []
        
        if readability < 0.6:
            recommendations.append("Lesbarkeit verbessern - Satzlängen anpassen")
        if age_appropriateness < 0.7:
            recommendations.append("Altersgerechtheit überprüfen - Inhalte anpassen")
        if genre_compliance < 0.5:
            recommendations.append("Genre-Konventionen stärker einbauen")
        if emotional_depth < 0.4:
            recommendations.append("Emotionale Tiefe erhöhen")
        if engagement < 0.5:
            recommendations.append("Engagement-Faktoren verstärken")
        
        return recommendations

def main():
    """Beispiel für zielgruppenspezifische Evaluation"""
    evaluator = TargetGroupEvaluator()
    
    # Test-Text
    test_text = """
    Der kleine Max stand vor der alten Höhle. Sein Herz klopfte laut, aber er wusste, dass er mutig sein musste.
    
    "Du schaffst das!", rief sein Freund Tom. "Ich glaube an dich!"
    
    Max atmete tief durch und trat in die Höhle. Die Kristalle an der Decke leuchteten in allen Farben des Regenbogens.
    
    "Das ist wunderbar!", flüsterte Max. Er hatte noch nie so etwas Schönes gesehen.
    
    Gemeinsam erkundeten sie die magische Höhle und fanden einen versteckten Schatz. Es war ein Tag voller Abenteuer und Freundschaft.
    """
    
    # Teste verschiedene Zielgruppen
    test_combinations = [
        {"age_group": "early_reader", "genre": "adventure", "emotion": "courage"},
        {"age_group": "middle_grade", "genre": "fantasy", "emotion": "wonder"},
        {"age_group": "young_adult", "genre": "self_discovery", "emotion": "growth"}
    ]
    
    for i, combo in enumerate(test_combinations, 1):
        print(f"\n{'='*60}")
        print(f"EVALUATION {i}: {combo['age_group']} / {combo['genre']} / {combo['emotion']}")
        print(f"{'='*60}")
        
        result = evaluator.evaluate_for_target_group(
            text=test_text,
            age_group=combo["age_group"],
            genre=combo["genre"],
            language="de"
        )
        
        print(f"Gesamtscore: {result.overall_score:.3f}")
        print(f"Lesbarkeit: {result.readability_score:.3f}")
        print(f"Altersgerechtheit: {result.age_appropriateness:.3f}")
        print(f"Genre-Compliance: {result.genre_compliance:.3f}")
        print(f"Emotionale Tiefe: {result.emotional_depth:.3f}")
        print(f"Engagement: {result.engagement_score:.3f}")
        
        if result.flags:
            print(f"Flags: {', '.join(result.flags)}")
        
        if result.recommendations:
            print("Empfehlungen:")
            for rec in result.recommendations:
                print(f"• {rec}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main() 