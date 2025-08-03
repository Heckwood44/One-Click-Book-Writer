#!/usr/bin/env python3
"""
Scalable Prompt Compiler
Erweiterter Compiler mit Altersklassen- und Genre-spezifischen Layern
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScalablePromptCompiler:
    """Erweiterter Prompt-Compiler für verschiedene Altersklassen und Genres"""
    
    def __init__(self):
        self.age_profiles = self._load_age_profiles()
        self.genre_profiles = self._load_genre_profiles()
        self.emotion_profiles = self._load_emotion_profiles()
    
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
    
    def _load_emotion_profiles(self) -> Dict:
        """Lädt Emotions-Profile"""
        return {
            "wonder": {
                "description": "Verwunderung und Staunen",
                "keywords": ["wunderbar", "erstaunlich", "magisch", "faszinierend"],
                "tone": "awe_inspiring, curious, amazed"
            },
            "courage": {
                "description": "Mut und Tapferkeit",
                "keywords": ["mutig", "tapfer", "stark", "entschlossen"],
                "tone": "brave, determined, inspiring"
            },
            "friendship": {
                "description": "Freundschaft und Verbundenheit",
                "keywords": ["freundlich", "liebevoll", "verbunden", "unterstützend"],
                "tone": "warm, supportive, caring"
            },
            "growth": {
                "description": "Wachstum und Entwicklung",
                "keywords": ["wachsen", "lernen", "entwickeln", "verändern"],
                "tone": "encouraging, empowering, transformative"
            },
            "mystery": {
                "description": "Geheimnis und Neugier",
                "keywords": ["geheimnisvoll", "rätselhaft", "neugierig", "spannend"],
                "tone": "mysterious, intriguing, suspenseful"
            }
        }
    
    def compile_scalable_prompt(self, 
                              age_group: str,
                              genre: str,
                              emotion: str,
                              target_audience: str = "general",
                              custom_context: Optional[Dict] = None) -> Dict:
        """
        Kompiliert skalierbaren Prompt basierend auf Altersklasse, Genre und Emotion
        
        Args:
            age_group: Altersklasse (preschool, early_reader, middle_grade, young_adult, adult)
            genre: Genre (adventure, fantasy, self_discovery, mystery, friendship, educational, self_help)
            emotion: Emotion (wonder, courage, friendship, growth, mystery)
            target_audience: Zielgruppe (general, children, teens, adults)
            custom_context: Zusätzlicher Kontext
        """
        try:
            # Lade Profile
            age_profile = self.age_profiles.get("age_groups", {}).get(age_group, {})
            genre_profile = self.genre_profiles.get("genres", {}).get(genre, {})
            emotion_profile = self.emotion_profiles.get(emotion, {})
            
            if not age_profile or not genre_profile:
                raise ValueError(f"Profil nicht gefunden: age_group={age_group}, genre={genre}")
            
            # Erstelle Layer-basierte Komposition
            layers = self._create_layered_composition(
                age_profile, genre_profile, emotion_profile, target_audience, custom_context
            )
            
            # Kompiliere finalen Prompt
            compiled_prompt = self._assemble_prompt(layers, age_group, genre, emotion)
            
            # Generiere Hash für Versionierung
            prompt_hash = self._generate_prompt_hash(compiled_prompt, age_group, genre, emotion)
            
            return {
                "compiled_prompt": compiled_prompt,
                "prompt_hash": prompt_hash,
                "layers": layers,
                "metadata": {
                    "age_group": age_group,
                    "genre": genre,
                    "emotion": emotion,
                    "target_audience": target_audience,
                    "compilation_timestamp": datetime.now().isoformat(),
                    "layer_weights": self._get_layer_weights(age_group, genre)
                }
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Prompt-Kompilierung: {e}")
            return {"error": str(e)}
    
    def _create_layered_composition(self, 
                                  age_profile: Dict,
                                  genre_profile: Dict,
                                  emotion_profile: Dict,
                                  target_audience: str,
                                  custom_context: Optional[Dict]) -> Dict:
        """Erstellt Layer-basierte Komposition"""
        
        layers = {
            "system_note": self._build_system_note_layer(age_profile, genre_profile),
            "target_audience": self._build_target_audience_layer(age_profile, target_audience),
            "genre_context": self._build_genre_context_layer(genre_profile),
            "emotion_drama": self._build_emotion_drama_layer(emotion_profile, genre_profile),
            "style_guidelines": self._build_style_guidelines_layer(age_profile, genre_profile),
            "content_structure": self._build_content_structure_layer(genre_profile),
            "constraints": self._build_constraints_layer(age_profile, genre_profile),
            "few_shot_examples": self._build_few_shot_layer(genre_profile, age_profile)
        }
        
        # Füge Custom Context hinzu falls vorhanden
        if custom_context:
            layers["custom_context"] = self._build_custom_context_layer(custom_context)
        
        return layers
    
    def _build_system_note_layer(self, age_profile: Dict, genre_profile: Dict) -> Dict:
        """Baut System Note Layer"""
        age_desc = age_profile.get("description", "")
        genre_desc = genre_profile.get("description", "")
        
        content = f"""SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR

Du bist ein weltklasse Autor, der spezialisiert ist auf {age_desc.lower()} im Genre {genre_desc.lower()}.

Deine Aufgabe ist es, Geschichten zu schreiben, die:
- Perfekt auf die Zielgruppe abgestimmt sind
- Den Genre-Konventionen entsprechen
- Emotionale Tiefe und Authentizität besitzen
- Bilingual (Deutsch/Englisch) verfasst sind

Verwende die folgenden Layer als strukturierte Anleitung für deine Arbeit."""
        
        return {
            "content": content,
            "weight": 1.0,
            "layer_type": "system_note"
        }
    
    def _build_target_audience_layer(self, age_profile: Dict, target_audience: str) -> Dict:
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
        
        return {
            "content": content,
            "weight": 1.2,
            "layer_type": "target_audience"
        }
    
    def _build_genre_context_layer(self, genre_profile: Dict) -> Dict:
        """Baut Genre Context Layer"""
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
        
        return {
            "content": content,
            "weight": 1.1,
            "layer_type": "genre_context"
        }
    
    def _build_emotion_drama_layer(self, emotion_profile: Dict, genre_profile: Dict) -> Dict:
        """Baut Emotion/Drama Layer"""
        emotional_focus = genre_profile.get("emotional_focus", [])
        
        content = f"""EMOTIONALE DRAMATURGIE:

Hauptemotion: {emotion_profile.get('description', '')}
Ton: {emotion_profile.get('tone', '')}

EMOTIONALE SCHWERPUNKTE:
{chr(10).join(f"- {emotion}" for emotion in emotional_focus)}

EMOTIONALE KEYWORDS:
{', '.join(emotion_profile.get('keywords', []))}

EMOTIONALE RICHTLINIEN:
- Baue emotionale Tiefe durch Charakterentwicklung auf
- Verwende die emotionale Landschaft des Genres
- Stelle sicher, dass Emotionen authentisch und altersgerecht sind
- Schaffe emotionale Verbindungen zwischen Charakteren und Lesern"""
        
        return {
            "content": content,
            "weight": 1.3,
            "layer_type": "emotion_drama"
        }
    
    def _build_style_guidelines_layer(self, age_profile: Dict, genre_profile: Dict) -> Dict:
        """Baut Style Guidelines Layer"""
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
        
        return {
            "content": content,
            "weight": 1.2,
            "layer_type": "style_guidelines"
        }
    
    def _build_content_structure_layer(self, genre_profile: Dict) -> Dict:
        """Baut Content Structure Layer"""
        structure = genre_profile.get("structure", {})
        
        content = f"""INHALTSSTRUKTUR:

PLOT-MUSTER: {structure.get('plot_pattern', '')}
TEMPO: {structure.get('pacing', '')}
KONFLIKT-TYP: {structure.get('conflict_type', '')}
AUFLÖSUNG: {structure.get('resolution', '')}

STRUKTURELLE RICHTLINIEN:
- Beginne mit einem klaren Setup und Charaktereinführung
- Entwickle den Konflikt organisch und altersgerecht
- Baue Spannung und emotionale Beteiligung auf
- Führe zu einer befriedigenden, thematisch relevanten Auflösung
- Stelle sicher, dass die Struktur dem Genre entspricht

PARAGRAPHEN-STRUKTUR:
- Verwende kurze, fokussierte Absätze für jüngere Leser
- Baue längere, beschreibende Absätze für ältere Leser
- Balanciere Handlung, Dialog und Beschreibung
- Verwende Übergänge, um den Fluss zu verbessern"""
        
        return {
            "content": content,
            "weight": 1.0,
            "layer_type": "content_structure"
        }
    
    def _build_constraints_layer(self, age_profile: Dict, genre_profile: Dict) -> Dict:
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
        
        return {
            "content": content,
            "weight": 1.1,
            "layer_type": "constraints"
        }
    
    def _build_few_shot_layer(self, genre_profile: Dict, age_profile: Dict) -> Dict:
        """Baut Few-Shot Examples Layer"""
        examples = genre_profile.get("few_shot_examples", [])
        
        content = f"""FEW-SHOT BEISPIELE:

Hier sind Beispiele für den gewünschten Stil und Ton:

{chr(10).join(f"Beispiel {i+1}: {example}" for i, example in enumerate(examples))}

RICHTLINIEN FÜR BEISPIELE:
- Verwende diese Beispiele als Inspiration für Stil und Ton
- Passe die Komplexität an die Altersgruppe an
- Stelle sicher, dass die Beispiele dem Genre entsprechen
- Verwende ähnliche emotionale und stilistische Elemente"""
        
        return {
            "content": content,
            "weight": 0.9,
            "layer_type": "few_shot_examples"
        }
    
    def _build_custom_context_layer(self, custom_context: Dict) -> Dict:
        """Baut Custom Context Layer"""
        content = f"""ZUSÄTZLICHER KONTEXT:

{custom_context.get('description', '')}

SPEZIFISCHE ANWEISUNGEN:
{custom_context.get('instructions', '')}

CHARAKTERE:
{custom_context.get('characters', '')}

SETTING:
{custom_context.get('setting', '')}"""
        
        return {
            "content": content,
            "weight": 1.0,
            "layer_type": "custom_context"
        }
    
    def _assemble_prompt(self, layers: Dict, age_group: str, genre: str, emotion: str) -> str:
        """Assembliert finalen Prompt aus Layern"""
        prompt_parts = []
        
        # System Note (immer zuerst)
        if "system_note" in layers:
            prompt_parts.append(layers["system_note"]["content"])
            prompt_parts.append("---")
        
        # Target Audience
        if "target_audience" in layers:
            prompt_parts.append(f"ZIELGRUPPEN-PROFIL ({age_group.upper()}):")
            prompt_parts.append(layers["target_audience"]["content"])
            prompt_parts.append("---")
        
        # Genre Context
        if "genre_context" in layers:
            prompt_parts.append(f"GENRE-KONTEXT ({genre.upper()}):")
            prompt_parts.append(layers["genre_context"]["content"])
            prompt_parts.append("---")
        
        # Emotion/Drama
        if "emotion_drama" in layers:
            prompt_parts.append(f"EMOTIONALE DRAMATURGIE ({emotion.upper()}):")
            prompt_parts.append(layers["emotion_drama"]["content"])
            prompt_parts.append("---")
        
        # Style Guidelines
        if "style_guidelines" in layers:
            prompt_parts.append("STIL-RICHTLINIEN:")
            prompt_parts.append(layers["style_guidelines"]["content"])
            prompt_parts.append("---")
        
        # Content Structure
        if "content_structure" in layers:
            prompt_parts.append("INHALTSSTRUKTUR:")
            prompt_parts.append(layers["content_structure"]["content"])
            prompt_parts.append("---")
        
        # Constraints
        if "constraints" in layers:
            prompt_parts.append("INHALTS-BESCHRÄNKUNGEN:")
            prompt_parts.append(layers["constraints"]["content"])
            prompt_parts.append("---")
        
        # Few-Shot Examples
        if "few_shot_examples" in layers:
            prompt_parts.append("FEW-SHOT BEISPIELE:")
            prompt_parts.append(layers["few_shot_examples"]["content"])
            prompt_parts.append("---")
        
        # Custom Context (falls vorhanden)
        if "custom_context" in layers:
            prompt_parts.append("ZUSÄTZLICHER KONTEXT:")
            prompt_parts.append(layers["custom_context"]["content"])
            prompt_parts.append("---")
        
        return "\n".join(prompt_parts)
    
    def _get_layer_weights(self, age_group: str, genre: str) -> Dict[str, float]:
        """Gibt Layer-Gewichte basierend auf Altersgruppe und Genre zurück"""
        base_weights = {
            "system_note": 1.0,
            "target_audience": 1.2,
            "genre_context": 1.1,
            "emotion_drama": 1.3,
            "style_guidelines": 1.2,
            "content_structure": 1.0,
            "constraints": 1.1,
            "few_shot_examples": 0.9,
            "custom_context": 1.0
        }
        
        # Anpasse Gewichte basierend auf Altersgruppe
        if age_group == "preschool":
            base_weights["target_audience"] = 1.4  # Höhere Gewichtung für Altersgruppe
            base_weights["constraints"] = 1.3      # Stärkere Beschränkungen
        elif age_group == "young_adult":
            base_weights["emotion_drama"] = 1.5    # Höhere emotionale Tiefe
            base_weights["style_guidelines"] = 1.4 # Komplexerer Stil
        
        # Anpasse Gewichte basierend auf Genre
        if genre == "fantasy":
            base_weights["genre_context"] = 1.3    # Wichtigere Genre-Konventionen
        elif genre == "mystery":
            base_weights["content_structure"] = 1.2 # Wichtigere Struktur
        
        return base_weights
    
    def _generate_prompt_hash(self, prompt: str, age_group: str, genre: str, emotion: str) -> str:
        """Generiert Hash für Prompt-Versionierung"""
        content_str = f"{age_group}:{genre}:{emotion}:{prompt}"
        return hashlib.md5(content_str.encode()).hexdigest()[:16]

def main():
    """Beispiel für skalierbaren Prompt-Compiler"""
    compiler = ScalablePromptCompiler()
    
    # Teste verschiedene Kombinationen
    test_combinations = [
        {"age_group": "early_reader", "genre": "adventure", "emotion": "courage"},
        {"age_group": "middle_grade", "genre": "fantasy", "emotion": "wonder"},
        {"age_group": "young_adult", "genre": "self_discovery", "emotion": "growth"}
    ]
    
    for i, combo in enumerate(test_combinations, 1):
        print(f"\n{'='*60}")
        print(f"TEST KOMBINATION {i}: {combo['age_group']} / {combo['genre']} / {combo['emotion']}")
        print(f"{'='*60}")
        
        result = compiler.compile_scalable_prompt(**combo)
        
        if "error" not in result:
            print(f"Prompt Hash: {result['prompt_hash']}")
            print(f"Layer Count: {len(result['layers'])}")
            print(f"Layer Weights: {result['metadata']['layer_weights']}")
            
            # Zeige ersten Teil des kompilierten Prompts
            prompt_preview = result['compiled_prompt'][:500] + "..." if len(result['compiled_prompt']) > 500 else result['compiled_prompt']
            print(f"\nPrompt Preview:\n{prompt_preview}")
        else:
            print(f"Fehler: {result['error']}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    main() 