#!/usr/bin/env python3
"""
Layered Composition Engine
Erweiterter Prompt-Compiler mit gewichtbaren Layern und Template Merging
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import difflib

from core.architecture import (
    ComponentInterface, ComponentType, LayerType, Layer, 
    PromptTemplate, PromptFrame, register_component
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LayeredCompositionEngine(ComponentInterface):
    """Erweiterte Layered Composition Engine für Prompt-Kompilierung"""
    
    def __init__(self):
        super().__init__(ComponentType.COMPILER, version="2.0.0")
        self.age_profiles = self._load_age_profiles()
        self.genre_profiles = self._load_genre_profiles()
        self.emotion_profiles = self._load_emotion_profiles()
        self.language_profiles = self._load_language_profiles()
        self.template_cache = {}
        
    def _load_age_profiles(self) -> Dict:
        """Lädt Altersklassen-Profile"""
        try:
            with open("profiles/age_group_profiles.json", 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                logger.info(f"Loaded {len(profiles)} age profiles")
                return profiles
        except FileNotFoundError:
            logger.warning("Age profiles file not found, using defaults")
            return self._get_default_age_profiles()
        except Exception as e:
            logger.error(f"Error loading age profiles: {e}")
            return self._get_default_age_profiles()
    
    def _get_default_age_profiles(self) -> Dict:
        """Fallback-Altersklassen-Profile"""
        return {
            "preschool": {
                "name": "Vorschule (3-5 Jahre)",
                "reading_level": "beginner",
                "vocabulary_complexity": "simple",
                "sentence_structure": "short",
                "tone": "gentle",
                "word_count_range": [50, 150],
                "sentence_length_range": [5, 15],
                "emotional_depth": "basic",
                "dialogue_ratio": 0.3,
                "description": "Einfache, bildhafte Geschichten mit kurzen Sätzen und grundlegenden Emotionen"
            },
            "early_reader": {
                "name": "Früher Leser (6-8 Jahre)",
                "reading_level": "early",
                "vocabulary_complexity": "basic",
                "sentence_structure": "simple",
                "tone": "encouraging",
                "word_count_range": [150, 300],
                "sentence_length_range": [8, 20],
                "emotional_depth": "moderate",
                "dialogue_ratio": 0.4,
                "description": "Ermutigende Geschichten mit einfacher Sprache und positiven Botschaften"
            },
            "middle_grade": {
                "name": "Mittlere Stufe (9-12 Jahre)",
                "reading_level": "intermediate",
                "vocabulary_complexity": "moderate",
                "sentence_structure": "varied",
                "tone": "engaging",
                "word_count_range": [300, 600],
                "sentence_length_range": [10, 25],
                "emotional_depth": "developed",
                "dialogue_ratio": 0.5,
                "description": "Fesselnde Geschichten mit entwickelten Charakteren und komplexeren Handlungen"
            },
            "young_adult": {
                "name": "Junge Erwachsene (13-17 Jahre)",
                "reading_level": "advanced",
                "vocabulary_complexity": "rich",
                "sentence_structure": "complex",
                "tone": "authentic",
                "word_count_range": [600, 1200],
                "sentence_length_range": [15, 35],
                "emotional_depth": "deep",
                "dialogue_ratio": 0.6,
                "description": "Authentische Geschichten mit tiefen Emotionen und komplexen Themen"
            },
            "adult": {
                "name": "Erwachsene (18+ Jahre)",
                "reading_level": "expert",
                "vocabulary_complexity": "sophisticated",
                "sentence_structure": "advanced",
                "tone": "mature",
                "word_count_range": [800, 2000],
                "sentence_length_range": [20, 50],
                "emotional_depth": "profound",
                "dialogue_ratio": 0.7,
                "description": "Reife Geschichten mit anspruchsvoller Sprache und tiefgründigen Themen"
            }
        }
    
    def _load_genre_profiles(self) -> Dict:
        """Lädt Genre-Profile"""
        try:
            with open("profiles/genre_profiles.json", 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                logger.info(f"Loaded {len(profiles)} genre profiles")
                return profiles
        except FileNotFoundError:
            logger.warning("Genre profiles file not found, using defaults")
            return self._get_default_genre_profiles()
        except Exception as e:
            logger.error(f"Error loading genre profiles: {e}")
            return self._get_default_genre_profiles()
    
    def _get_default_genre_profiles(self) -> Dict:
        """Fallback-Genre-Profile"""
        return {
            "adventure": {
                "name": "Abenteuer",
                "description": "Spannende Geschichten mit Herausforderungen und Entdeckungen",
                "key_elements": ["action", "exploration", "challenges", "discovery"],
                "emotional_focus": "excitement",
                "pacing": "fast",
                "conflict_type": "external",
                "resolution_style": "triumphant",
                "style_guidelines": {
                    "tone": "energetic",
                    "sentence_structure": "dynamic",
                    "imagery": "vivid",
                    "dialogue": "action-oriented"
                }
            },
            "fantasy": {
                "name": "Fantasy",
                "description": "Magische Welten mit übernatürlichen Elementen",
                "key_elements": ["magic", "mythical_creatures", "otherworldly_settings", "quests"],
                "emotional_focus": "wonder",
                "pacing": "varied",
                "conflict_type": "epic",
                "resolution_style": "transformative",
                "style_guidelines": {
                    "tone": "mystical",
                    "sentence_structure": "descriptive",
                    "imagery": "enchanting",
                    "dialogue": "otherworldly"
                }
            },
            "self_discovery": {
                "name": "Selbstfindung",
                "description": "Geschichten über persönliches Wachstum und Identität",
                "key_elements": ["personal_growth", "identity", "reflection", "transformation"],
                "emotional_focus": "introspection",
                "pacing": "contemplative",
                "conflict_type": "internal",
                "resolution_style": "enlightening",
                "style_guidelines": {
                    "tone": "reflective",
                    "sentence_structure": "thoughtful",
                    "imagery": "metaphorical",
                    "dialogue": "introspective"
                }
            },
            "friendship": {
                "name": "Freundschaft",
                "description": "Geschichten über Beziehungen und Verbindungen",
                "key_elements": ["relationships", "loyalty", "trust", "support"],
                "emotional_focus": "connection",
                "pacing": "steady",
                "conflict_type": "relational",
                "resolution_style": "reconciliatory",
                "style_guidelines": {
                    "tone": "warm",
                    "sentence_structure": "conversational",
                    "imagery": "intimate",
                    "dialogue": "natural"
                }
            },
            "mystery": {
                "name": "Mystery",
                "description": "Rätselhafte Geschichten mit Überraschungen",
                "key_elements": ["secrets", "clues", "suspense", "reveals"],
                "emotional_focus": "curiosity",
                "pacing": "suspenseful",
                "conflict_type": "puzzling",
                "resolution_style": "revealing",
                "style_guidelines": {
                    "tone": "intriguing",
                    "sentence_structure": "building",
                    "imagery": "atmospheric",
                    "dialogue": "clue-laden"
                }
            }
        }
    
    def _load_emotion_profiles(self) -> Dict:
        """Lädt Emotions-Profile"""
        return {
            "wonder": {
                "description": "Verwunderung und Staunen",
                "keywords": ["wunderbar", "erstaunlich", "magisch", "faszinierend"],
                "tone": "awe_inspiring, curious, amazed",
                "intensity": 0.8
            },
            "courage": {
                "description": "Mut und Tapferkeit",
                "keywords": ["mutig", "tapfer", "stark", "entschlossen"],
                "tone": "brave, determined, inspiring",
                "intensity": 0.9
            },
            "friendship": {
                "description": "Freundschaft und Verbundenheit",
                "keywords": ["freundlich", "liebevoll", "verbunden", "unterstützend"],
                "tone": "warm, supportive, caring",
                "intensity": 0.7
            },
            "growth": {
                "description": "Wachstum und Entwicklung",
                "keywords": ["wachsen", "lernen", "entwickeln", "verändern"],
                "tone": "encouraging, empowering, transformative",
                "intensity": 0.8
            },
            "mystery": {
                "description": "Geheimnis und Neugier",
                "keywords": ["geheimnisvoll", "rätselhaft", "neugierig", "spannend"],
                "tone": "mysterious, intriguing, suspenseful",
                "intensity": 0.7
            }
        }
    
    def _load_language_profiles(self) -> Dict:
        """Lädt Sprach-Profile"""
        return {
            "de": {
                "name": "Deutsch",
                "formality_levels": ["sehr_formell", "formell", "neutral", "informell", "sehr_informell"],
                "complexity_factors": ["einfach", "mittel", "komplex"],
                "cultural_context": "deutschsprachiger_Raum"
            },
            "en": {
                "name": "English",
                "formality_levels": ["very_formal", "formal", "neutral", "informal", "very_informal"],
                "complexity_factors": ["simple", "intermediate", "complex"],
                "cultural_context": "english_speaking_world"
            }
        }
    
    def compile_template(self, prompt_frame: PromptFrame) -> PromptTemplate:
        """Kompiliert Template basierend auf PromptFrame"""
        try:
            # Erstelle Template-ID
            template_id = f"{prompt_frame.age_group}_{prompt_frame.genre}_{prompt_frame.emotion}_{prompt_frame.language}"
            
            # Prüfe Cache
            if template_id in self.template_cache:
                return self.template_cache[template_id]
            
            # Erstelle Layer-basierte Komposition
            layers = self._create_layered_composition(prompt_frame)
            
            # Erstelle Template
            template = PromptTemplate(
                template_id=template_id,
                name=f"{prompt_frame.age_group.title()} {prompt_frame.genre.title()} {prompt_frame.emotion.title()}",
                description=f"Template für {prompt_frame.age_group} {prompt_frame.genre} mit {prompt_frame.emotion}",
                layers=layers,
                version="2.0.0",
                metadata={
                    "age_group": prompt_frame.age_group,
                    "genre": prompt_frame.genre,
                    "emotion": prompt_frame.emotion,
                    "language": prompt_frame.language,
                    "compilation_timestamp": datetime.now().isoformat()
                }
            )
            
            # Cache Template
            self.template_cache[template_id] = template
            
            return template
            
        except Exception as e:
            logger.error(f"Fehler bei Template-Kompilierung: {e}")
            raise
    
    def _create_layered_composition(self, prompt_frame: PromptFrame) -> List[Layer]:
        """Erstellt Layer-basierte Komposition"""
        layers = []
        
        # Lade Profile
        age_profile = self.age_profiles.get(prompt_frame.age_group, {})
        genre_profile = self.genre_profiles.get(prompt_frame.genre, {})
        emotion_profile = self.emotion_profiles.get(prompt_frame.emotion, {})
        language_profile = self.language_profiles.get(prompt_frame.language, {})
        
        if not age_profile or not genre_profile:
            logger.error(f"Profile nicht gefunden: age_group={prompt_frame.age_group}, genre={prompt_frame.genre}")
            logger.error(f"Verfügbare Altersklassen: {list(self.age_profiles.keys())}")
            logger.error(f"Verfügbare Genres: {list(self.genre_profiles.keys())}")
            raise ValueError(f"Profil nicht gefunden: age_group={prompt_frame.age_group}, genre={prompt_frame.genre}")
        
        # System Note Layer
        layers.append(self._build_system_note_layer(age_profile, genre_profile, language_profile))
        
        # Target Audience Layer
        layers.append(self._build_target_audience_layer(age_profile, prompt_frame.language))
        
        # Genre Layer
        layers.append(self._build_genre_layer(genre_profile))
        
        # Emotion/Drama Layer
        layers.append(self._build_emotion_drama_layer(emotion_profile, genre_profile))
        
        # Style Layer
        layers.append(self._build_style_layer(age_profile, genre_profile))
        
        # Context Layer
        layers.append(self._build_context_layer(prompt_frame))
        
        # Constraints Layer
        layers.append(self._build_constraints_layer(age_profile, genre_profile))
        
        # Language Layer
        layers.append(self._build_language_layer(language_profile, prompt_frame.language))
        
        # Custom Context Layer (falls vorhanden)
        if prompt_frame.custom_context:
            layers.append(self._build_custom_context_layer(prompt_frame.custom_context))
        
        return layers
    
    def _build_system_note_layer(self, age_profile: Dict, genre_profile: Dict, language_profile: Dict) -> Layer:
        """Baut System Note Layer"""
        age_desc = age_profile.get("description", "")
        genre_desc = genre_profile.get("description", "")
        language_name = language_profile.get("name", "")
        
        content = f"""SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR

Du bist ein weltklasse Autor, der spezialisiert ist auf {age_desc.lower()} im Genre {genre_desc.lower()} für {language_name}-sprechende Leser.

Deine Aufgabe ist es, Geschichten zu schreiben, die:
- Perfekt auf die Zielgruppe abgestimmt sind
- Den Genre-Konventionen entsprechen
- Emotionale Tiefe und Authentizität besitzen
- Bilingual (Deutsch/Englisch) verfasst sind
- Kulturell angemessen für {language_name}-sprechende Leser sind

Verwende die folgenden Layer als strukturierte Anleitung für deine Arbeit."""
        
        return Layer(
            layer_type=LayerType.SYSTEM_NOTE,
            content=content,
            weight=1.0,
            version="2.0.0"
        )
    
    def _build_target_audience_layer(self, age_profile: Dict, language: str) -> Layer:
        """Baut Target Audience Layer"""
        readability = age_profile.get("readability", {})
        style_guidelines = age_profile.get("style_guidelines", {})
        
        content = f"""ZIELGRUPPEN-PROFIL:

Altersgruppe: {age_profile.get('age_range', '')} Jahre
Beschreibung: {age_profile.get('description', '')}

LESBARKEIT:
- Zielwortanzahl: {readability.get('target_words', 0)} Wörter
- Maximale Satzlänge: {readability.get('max_sentence_length', 0)} Wörter
- Vokabular-Level: {readability.get('vocabulary_level', '')}
- Komplexitäts-Score: {readability.get('complexity_score', 0)}

STIL-RICHTLINIEN:
- Ton: {style_guidelines.get('tone', '')}
- Satzstruktur: {style_guidelines.get('sentence_structure', '')}
- Bildhaftigkeit: {style_guidelines.get('imagery', '')}
- Dialoge: {style_guidelines.get('dialogue', '')}

STYLE ANCHORS:
{chr(10).join(f"- {anchor}" for anchor in age_profile.get('style_anchors', []))}"""
        
        return Layer(
            layer_type=LayerType.TARGET_AUDIENCE,
            content=content,
            weight=1.2,
            version="2.0.0"
        )
    
    def _build_genre_layer(self, genre_profile: Dict) -> Layer:
        """Baut Genre Layer"""
        structure = genre_profile.get("structure", {})
        conventions = genre_profile.get("conventions", {})
        
        content = f"""GENRE-KONTEXT:

Genre: {genre_profile.get('description', '')}

STRUKTUR:
- Plot-Muster: {structure.get('plot_pattern', '')}
- Tempo: {structure.get('pacing', '')}
- Konflikt-Typ: {structure.get('conflict_type', '')}
- Auflösung: {structure.get('resolution', '')}

KONVENTIONEN:
Tropes: {', '.join(conventions.get('tropes', []))}
Settings: {', '.join(conventions.get('settings', []))}
Charaktere: {', '.join(conventions.get('characters', []))}

STIL-RICHTLINIEN:
- Ton: {genre_profile.get('style_guidelines', {}).get('tone', '')}
- Tempo: {genre_profile.get('style_guidelines', {}).get('pacing', '')}
- Beschreibungen: {genre_profile.get('style_guidelines', {}).get('descriptions', '')}
- Dialoge: {genre_profile.get('style_guidelines', {}).get('dialogue', '')}"""
        
        return Layer(
            layer_type=LayerType.GENRE,
            content=content,
            weight=1.1,
            version="2.0.0"
        )
    
    def _build_emotion_drama_layer(self, emotion_profile: Dict, genre_profile: Dict) -> Layer:
        """Baut Emotion/Drama Layer"""
        emotional_focus = genre_profile.get("emotional_focus", [])
        intensity = emotion_profile.get("intensity", 0.7)
        
        content = f"""EMOTIONALE DRAMATURGIE:

Hauptemotion: {emotion_profile.get('description', '')}
Ton: {emotion_profile.get('tone', '')}
Intensität: {intensity:.1f}

EMOTIONALE SCHWERPUNKTE:
{chr(10).join(f"- {emotion}" for emotion in emotional_focus)}

EMOTIONALE KEYWORDS:
{', '.join(emotion_profile.get('keywords', []))}

EMOTIONALE RICHTLINIEN:
- Baue emotionale Tiefe durch Charakterentwicklung auf
- Verwende die emotionale Landschaft des Genres
- Stelle sicher, dass Emotionen authentisch und altersgerecht sind
- Schaffe emotionale Verbindungen zwischen Charakteren und Lesern
- Verwende emotionale Intensität von {intensity:.1f} für {emotion_profile.get('description', '')}"""
        
        return Layer(
            layer_type=LayerType.EMOTION_DRAMA,
            content=content,
            weight=1.3,
            version="2.0.0"
        )
    
    def _build_style_layer(self, age_profile: Dict, genre_profile: Dict) -> Layer:
        """Baut Style Layer"""
        age_style = age_profile.get("style_guidelines", {})
        genre_style = genre_profile.get("style_guidelines", {})
        
        content = f"""STIL-RICHTLINIEN:

ALTERSSPEZIFISCHE STIL-RICHTLINIEN:
- Ton: {age_style.get('tone', '')}
- Satzstruktur: {age_style.get('sentence_structure', '')}
- Bildhaftigkeit: {age_style.get('imagery', '')}
- Dialoge: {age_style.get('dialogue', '')}
- Moralische Lektionen: {age_style.get('moral_lessons', '')}

GENRE-SPEZIFISCHE STIL-RICHTLINIEN:
- Ton: {genre_style.get('tone', '')}
- Tempo: {genre_style.get('pacing', '')}
- Beschreibungen: {genre_style.get('descriptions', '')}
- Dialoge: {genre_style.get('dialogue', '')}

KOMBINIERTE STIL-RICHTLINIEN:
- Passe Genre-Konventionen an die Altersgruppe an
- Verwende altersgerechte Sprache mit Genre-typischen Elementen
- Balanciere Komplexität und Zugänglichkeit
- Stelle sicher, dass der Stil konsistent und authentisch ist"""
        
        return Layer(
            layer_type=LayerType.STYLE,
            content=content,
            weight=1.2,
            version="2.0.0"
        )
    
    def _build_context_layer(self, prompt_frame: PromptFrame) -> Layer:
        """Baut Context Layer"""
        content = f"""KONTEXT-INFORMATIONEN:

Zielgruppe: {prompt_frame.target_audience}
Sprache: {prompt_frame.language}
Altersgruppe: {prompt_frame.age_group}
Genre: {prompt_frame.genre}
Emotion: {prompt_frame.emotion}

KONTEXT-RICHTLINIEN:
- Berücksichtige kulturelle und sprachliche Besonderheiten
- Passe den Kontext an die Zielgruppe an
- Stelle sicher, dass alle Elemente kohärent sind
- Verwende kontextgerechte Beispiele und Referenzen"""
        
        return Layer(
            layer_type=LayerType.CONTEXT,
            content=content,
            weight=1.0,
            version="2.0.0"
        )
    
    def _build_constraints_layer(self, age_profile: Dict, genre_profile: Dict) -> Layer:
        """Baut Constraints Layer"""
        age_constraints = age_profile.get("content_constraints", {})
        
        content = f"""INHALTS-BESCHRÄNKUNGEN:

VERMEIDEN:
{chr(10).join(f"- {item}" for item in age_constraints.get('avoid', []))}

BETONEN:
{chr(10).join(f"- {item}" for item in age_constraints.get('emphasize', []))}

THEMEN:
{chr(10).join(f"- {theme}" for theme in age_constraints.get('themes', []))}

QUALITÄTSRICHTLINIEN:
- Stelle sicher, dass alle Inhalte altersgerecht sind
- Vermeide problematische oder beunruhigende Elemente
- Fokussiere auf positive, konstruktive Botschaften
- Balanciere Realismus mit Hoffnung und Optimismus
- Respektiere die emotionalen und kognitiven Fähigkeiten der Zielgruppe"""
        
        return Layer(
            layer_type=LayerType.CONSTRAINTS,
            content=content,
            weight=1.1,
            version="2.0.0"
        )
    
    def _build_language_layer(self, language_profile: Dict, language: str) -> Layer:
        """Baut Language Layer"""
        content = f"""SPRACH-RICHTLINIEN:

Sprache: {language_profile.get('name', language)}
Kultureller Kontext: {language_profile.get('cultural_context', '')}

FORMALITÄTS-LEVELS:
{', '.join(language_profile.get('formality_levels', []))}

KOMPLEXITÄTS-FAKTOREN:
{', '.join(language_profile.get('complexity_factors', []))}

SPRACH-RICHTLINIEN:
- Verwende natürliche, flüssige Sprache
- Berücksichtige kulturelle Nuancen und Konventionen
- Stelle sicher, dass die Sprache altersgerecht ist
- Verwende angemessene Formellheit für die Zielgruppe"""
        
        return Layer(
            layer_type=LayerType.LANGUAGE,
            content=content,
            weight=1.0,
            version="2.0.0"
        )
    
    def _build_custom_context_layer(self, custom_context: Dict) -> Layer:
        """Baut Custom Context Layer"""
        content = f"""ZUSÄTZLICHER KONTEXT:

{custom_context.get('description', '')}

SPEZIFISCHE ANWEISUNGEN:
{custom_context.get('instructions', '')}

CHARAKTERE:
{custom_context.get('characters', '')}

SETTING:
{custom_context.get('setting', '')}"""
        
        return Layer(
            layer_type=LayerType.CUSTOM,
            content=content,
            weight=1.0,
            version="2.0.0"
        )
    
    def merge_templates(self, templates: List[PromptTemplate], weights: Optional[List[float]] = None) -> PromptTemplate:
        """Merged mehrere Templates mit gewichteter Kombination"""
        if not templates:
            raise ValueError("Mindestens ein Template erforderlich")
        
        if weights is None:
            weights = [1.0] * len(templates)
        
        if len(weights) != len(templates):
            raise ValueError("Anzahl der Gewichte muss der Anzahl der Templates entsprechen")
        
        # Normalisiere Gewichte
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Erstelle merged Template
        merged_template_id = f"merged_{hashlib.md5(str(templates).encode()).hexdigest()[:8]}"
        
        # Kombiniere Layer
        merged_layers = []
        layer_types = set()
        
        for template, weight in zip(templates, normalized_weights):
            for layer in template.layers:
                if layer.layer_type not in layer_types:
                    # Erste Instanz dieses Layer-Typs
                    merged_layers.append(Layer(
                        layer_type=layer.layer_type,
                        content=layer.content,
                        weight=layer.weight * weight,
                        version=layer.version,
                        metadata=layer.metadata
                    ))
                    layer_types.add(layer.layer_type)
                else:
                    # Layer-Typ bereits vorhanden, gewichte kombinieren
                    existing_layer = next(l for l in merged_layers if l.layer_type == layer.layer_type)
                    existing_layer.content += f"\n\n--- GEWICHTET {weight:.2f} ---\n{layer.content}"
                    existing_layer.weight = (existing_layer.weight + layer.weight * weight) / 2
        
        return PromptTemplate(
            template_id=merged_template_id,
            name=f"Merged Template ({len(templates)} Templates)",
            description=f"Gewichtete Kombination von {len(templates)} Templates",
            layers=merged_layers,
            version="2.0.0",
            metadata={
                "merged_templates": [t.template_id for t in templates],
                "weights": normalized_weights,
                "merge_timestamp": datetime.now().isoformat()
            }
        )
    
    def generate_prompt(self, template: PromptTemplate) -> str:
        """Generiert finalen Prompt aus Template"""
        prompt_parts = []
        
        # Sortiere Layer nach Gewicht (höchste zuerst)
        sorted_layers = sorted(template.layers, key=lambda x: x.weight, reverse=True)
        
        for layer in sorted_layers:
            prompt_parts.append(f"=== {layer.layer_type.value.upper()} (Gewicht: {layer.weight:.2f}) ===")
            prompt_parts.append(layer.content)
            prompt_parts.append("---")
        
        return "\n".join(prompt_parts)
    
    def calculate_template_hash(self, template: PromptTemplate) -> str:
        """Berechnet Hash für Template"""
        return template.get_hash()
    
    def compare_templates(self, template1: PromptTemplate, template2: PromptTemplate) -> Dict[str, Any]:
        """Vergleicht zwei Templates"""
        prompt1 = self.generate_prompt(template1)
        prompt2 = self.generate_prompt(template2)
        
        # Berechne Diff
        diff = list(difflib.unified_diff(
            prompt1.splitlines(keepends=True),
            prompt2.splitlines(keepends=True),
            fromfile=f"Template {template1.template_id}",
            tofile=f"Template {template2.template_id}"
        ))
        
        return {
            "template1_hash": template1.get_hash(),
            "template2_hash": template2.get_hash(),
            "diff": ''.join(diff),
            "similarity": self._calculate_similarity(prompt1, prompt2)
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Berechnet Ähnlichkeit zwischen zwei Texten"""
        return difflib.SequenceMatcher(None, text1, text2).ratio()

# Registrierte Version der Layered Composition Engine
class LayeredCompositionEngineComponent(LayeredCompositionEngine):
    """Registrierte Version der Layered Composition Engine"""
    def __init__(self):
        super().__init__() 