#!/usr/bin/env python3
"""
One Click Book Writer - Prompt Compiler
Version: 2.0.0
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

def compile_prompt(prompt_frame: Dict) -> str:
    """Kompiliert PromptFrame für Claude (Anthropic)"""
    try:
        input_data = prompt_frame.get('input', {})
        
        # Extrahiere Basis-Informationen
        book_info = input_data.get('book', {})
        chapter_info = input_data.get('chapter', {})
        characters = input_data.get('characters', {})
        scene = input_data.get('scene', {})
        plot = input_data.get('plot', {})
        style = input_data.get('style', {})
        emotions = input_data.get('emotions', {})
        language_config = input_data.get('language', {})
        
        # Fallback für alte Struktur
        if not characters and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            main_char = {
                'name': 'Feuerherz',
                'description': 'Ein kleiner, mutiger Drache',
                'personality': 'Neugierig und mutig',
                'goals': 'Fliegen lernen'
            }
            characters = {'main_character': main_char}
        
        if not scene and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            location = story_context.get('location', {})
            scene = {
                'setting': location.get('description', 'Drachenhöhle'),
                'time': 'Goldener Nachmittag',
                'atmosphere': location.get('mood', 'Gemütlich und sicher')
            }
        
        if not plot and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            plot = {
                'main_event': 'Erster Flugversuch',
                'conflict': 'Angst vs. Wunsch zu fliegen',
                'resolution': 'Erfolgreicher erster Flug'
            }
        
        if not emotions and 'emotional_layer' in input_data:
            emotional_layer = input_data.get('emotional_layer', {})
            emotions = {
                'core_emotion': emotional_layer.get('core_emotion', 'Mut und Aufregung'),
                'emotional_arc': emotional_layer.get('emotional_tone', 'Von Nervosität zu Freude')
            }
        
        # Prüfe bilinguale Konfiguration
        is_bilingual = language_config.get('bilingual_output', False)
        target_languages = language_config.get('target_languages', ['de'])
        
        # Erstelle Basis-Prompt
        prompt = f"""
# System Note
Du bist ein erfahrener Autor für {book_info.get('genre', 'Kinderbücher')}. 
Erstelle ein fesselndes Kapitel basierend auf den folgenden Spezifikationen.

# Buch-Informationen
- Titel: {book_info.get('title', 'Unbekannt')}
- Genre: {book_info.get('genre', 'Unbekannt')}
- Zielgruppe: {book_info.get('target_audience', 'Unbekannt')}
- Thema: {book_info.get('theme', 'Unbekannt')}
- Setting: {book_info.get('setting', 'Unbekannt')}

# Kapitel-Informationen
- Nummer: {chapter_info.get('number', 'Unbekannt')}
- Titel: {chapter_info.get('title', 'Unbekannt')}
- Zweck: {chapter_info.get('narrative_purpose', 'Unbekannt')}
- Position im Bogen: {chapter_info.get('position_in_arc', 'Unbekannt')}
- Zielwortanzahl: {chapter_info.get('length_words', 'Unbekannt')}

# Hauptfigur
- Name: {characters.get('main_character', {}).get('name', 'Unbekannt')}
- Beschreibung: {characters.get('main_character', {}).get('description', 'Unbekannt')}
- Persönlichkeit: {characters.get('main_character', {}).get('personality', 'Unbekannt')}
- Ziele: {characters.get('main_character', {}).get('goals', 'Unbekannt')}

# Szene
- Setting: {scene.get('setting', 'Unbekannt')}
- Zeit: {scene.get('time', 'Unbekannt')}
- Atmosphäre: {scene.get('atmosphere', 'Unbekannt')}

# Handlung
- Hauptereignis: {plot.get('main_event', 'Unbekannt')}
- Konflikt: {plot.get('conflict', 'Unbekannt')}
- Auflösung: {plot.get('resolution', 'Unbekannt')}

# Stil
- Ton: {style.get('tone', 'Unbekannt')}
- Tempo: {style.get('pacing', 'Unbekannt')}
- Dialogstil: {style.get('dialogue_style', 'Unbekannt')}

# Emotionen
- Kerngemüt: {emotions.get('core_emotion', 'Unbekannt')}
- Emotionaler Bogen: {emotions.get('emotional_arc', 'Unbekannt')}

# Aufgabe
Erstelle ein fesselndes Kapitel mit etwa {chapter_info.get('length_words', 800)} Wörtern.
Das Kapitel sollte die angegebene emotionale Tiefe haben und den Leser mitreißen.
"""
        
        # Füge bilinguale Anweisungen hinzu
        if is_bilingual and len(target_languages) > 1:
            prompt += f"""
# Bilinguale Generierung
Erstelle das Kapitel in {len(target_languages)} Sprachen: {', '.join(target_languages)}

Für jede Sprache:
1. Verwende die entsprechenden Sprachvarianten für Namen, Orte und Begriffe
2. Passe den Stil an die jeweilige Sprache an
3. Stelle sicher, dass beide Versionen die gleiche emotionale Tiefe haben

Sprachvarianten:
"""
            
            # Füge Sprachvarianten hinzu
            for lang in target_languages:
                prompt += f"\n## {lang.upper()} Varianten:\n"
                
                # Buch-Titel
                if 'titles' in book_info and lang in book_info['titles']:
                    prompt += f"- Buch-Titel: {book_info['titles'][lang]}\n"
                
                # Kapitel-Titel
                if 'titles' in chapter_info and lang in chapter_info['titles']:
                    prompt += f"- Kapitel-Titel: {chapter_info['titles'][lang]}\n"
                
                # Charakter-Varianten
                main_char = characters.get('main_character', {})
                if 'language_variants' in main_char and lang in main_char['language_variants']:
                    lang_var = main_char['language_variants'][lang]
                    prompt += f"- Hauptfigur: {lang_var.get('name', 'Unbekannt')} - {lang_var.get('description', 'Unbekannt')}\n"
                
                # Szene-Varianten
                if 'language_variants' in scene and lang in scene['language_variants']:
                    lang_var = scene['language_variants'][lang]
                    prompt += f"- Setting: {lang_var.get('setting', 'Unbekannt')}\n"
                    prompt += f"- Zeit: {lang_var.get('time', 'Unbekannt')}\n"
                    prompt += f"- Atmosphäre: {lang_var.get('atmosphere', 'Unbekannt')}\n"
            
            prompt += f"""
# Bilinguale Ausgabe
Erstelle das Kapitel in beiden Sprachen ({', '.join(target_languages)}).
Trenne die Versionen mit '---' und markiere jede Sprache klar.
"""
        
        logger.info(f"Prompt erfolgreich kompiliert für Kapitel {chapter_info.get('number', 'Unbekannt')}")
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Fehler beim Kompilieren des Prompts: {e}")
        raise

def compile_prompt_for_chatgpt(prompt_frame: Dict) -> str:
    """Kompiliert PromptFrame für ChatGPT (OpenAI)"""
    try:
        input_data = prompt_frame.get('input', {})
        
        # Extrahiere Basis-Informationen
        book_info = input_data.get('book', {})
        chapter_info = input_data.get('chapter', {})
        characters = input_data.get('characters', {})
        scene = input_data.get('scene', {})
        plot = input_data.get('plot', {})
        style = input_data.get('style', {})
        emotions = input_data.get('emotions', {})
        language_config = input_data.get('language', {})
        
        # Fallback für alte Struktur
        if not characters and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            main_char = {
                'name': 'Feuerherz',
                'description': 'Ein kleiner, mutiger Drache',
                'personality': 'Neugierig und mutig',
                'goals': 'Fliegen lernen'
            }
            characters = {'main_character': main_char}
        
        if not scene and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            location = story_context.get('location', {})
            scene = {
                'setting': location.get('description', 'Drachenhöhle'),
                'time': 'Goldener Nachmittag',
                'atmosphere': location.get('mood', 'Gemütlich und sicher')
            }
        
        if not plot and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            plot = {
                'main_event': 'Erster Flugversuch',
                'conflict': 'Angst vs. Wunsch zu fliegen',
                'resolution': 'Erfolgreicher erster Flug'
            }
        
        if not emotions and 'emotional_layer' in input_data:
            emotional_layer = input_data.get('emotional_layer', {})
            emotions = {
                'core_emotion': emotional_layer.get('core_emotion', 'Mut und Aufregung'),
                'emotional_arc': emotional_layer.get('emotional_tone', 'Von Nervosität zu Freude')
            }
        
        # Prüfe bilinguale Konfiguration
        is_bilingual = language_config.get('bilingual_output', False)
        target_languages = language_config.get('target_languages', ['de'])
        
        # Erstelle strukturierten Prompt
        prompt = f"""Du bist ein erfahrener Autor für {book_info.get('genre', 'Kinderbücher')}.

Buch: {book_info.get('title', 'Unbekannt')} ({book_info.get('genre', 'Unbekannt')})
Zielgruppe: {book_info.get('target_audience', 'Unbekannt')}
Thema: {book_info.get('theme', 'Unbekannt')}

Kapitel {chapter_info.get('number', '?')}: {chapter_info.get('title', 'Unbekannt')}
Zweck: {chapter_info.get('narrative_purpose', 'Unbekannt')}
Zielwortanzahl: {chapter_info.get('length_words', 800)}

Hauptfigur: {characters.get('main_character', {}).get('name', 'Unbekannt')} - {characters.get('main_character', {}).get('description', 'Unbekannt')}
Persönlichkeit: {characters.get('main_character', {}).get('personality', 'Unbekannt')}

Szene: {scene.get('setting', 'Unbekannt')} ({scene.get('time', 'Unbekannt')})
Atmosphäre: {scene.get('atmosphere', 'Unbekannt')}

Handlung: {plot.get('main_event', 'Unbekannt')}
Konflikt: {plot.get('conflict', 'Unbekannt')}
Auflösung: {plot.get('resolution', 'Unbekannt')}

Stil: {style.get('tone', 'Unbekannt')}, {style.get('pacing', 'Unbekannt')}
Dialoge: {style.get('dialogue_style', 'Unbekannt')}

Emotionen: {emotions.get('core_emotion', 'Unbekannt')}
Emotionaler Bogen: {emotions.get('emotional_arc', 'Unbekannt')}"""
        
        # Füge bilinguale Anweisungen hinzu
        if is_bilingual and len(target_languages) > 1:
            prompt += f"""

BILINGUALE GENERIERUNG:
Erstelle das Kapitel in {len(target_languages)} Sprachen: {', '.join(target_languages)}

Sprachvarianten:"""
            
            # Füge Sprachvarianten hinzu
            for lang in target_languages:
                prompt += f"\n{lang.upper()}:"
                
                # Buch-Titel
                if 'titles' in book_info and lang in book_info['titles']:
                    prompt += f"\n- Buch: {book_info['titles'][lang]}"
                
                # Kapitel-Titel
                if 'titles' in chapter_info and lang in chapter_info['titles']:
                    prompt += f"\n- Kapitel: {chapter_info['titles'][lang]}"
                
                # Charakter-Varianten
                main_char = characters.get('main_character', {})
                if 'language_variants' in main_char and lang in main_char['language_variants']:
                    lang_var = main_char['language_variants'][lang]
                    prompt += f"\n- Hauptfigur: {lang_var.get('name', 'Unbekannt')} - {lang_var.get('description', 'Unbekannt')}"
                
                # Szene-Varianten
                if 'language_variants' in scene and lang in scene['language_variants']:
                    lang_var = scene['language_variants'][lang]
                    prompt += f"\n- Setting: {lang_var.get('setting', 'Unbekannt')}"
                    prompt += f"\n- Zeit: {lang_var.get('time', 'Unbekannt')}"
                    prompt += f"\n- Atmosphäre: {lang_var.get('atmosphere', 'Unbekannt')}"
            
            prompt += f"""

AUFGABE:
Erstelle das Kapitel in beiden Sprachen ({', '.join(target_languages)}).
Trenne die Versionen mit '---' und markiere jede Sprache klar.
Beispiel:
DEUTSCH:
[Deutscher Text]

ENGLISH:
[English text]

Stelle sicher, dass beide Versionen die gleiche emotionale Tiefe und Qualität haben."""
        else:
            prompt += f"""

AUFGABE:
Erstelle ein fesselndes Kapitel mit etwa {chapter_info.get('length_words', 800)} Wörtern.
Das Kapitel sollte die angegebene emotionale Tiefe haben und den Leser mitreißen."""
        
        logger.info(f"ChatGPT-Prompt erfolgreich kompiliert für Kapitel {chapter_info.get('number', 'Unbekannt')}")
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Fehler beim Kompilieren des ChatGPT-Prompts: {e}")
        raise

def compile_bilingual_prompt(prompt_frame: Dict, target_language: str) -> str:
    """Kompiliert PromptFrame für eine spezifische Zielsprache"""
    try:
        input_data = prompt_frame.get('input', {})
        
        # Extrahiere Basis-Informationen
        book_info = input_data.get('book', {})
        chapter_info = input_data.get('chapter', {})
        characters = input_data.get('characters', {})
        scene = input_data.get('scene', {})
        plot = input_data.get('plot', {})
        style = input_data.get('style', {})
        emotions = input_data.get('emotions', {})
        
        # Fallback für alte Struktur
        if not characters and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            main_char = {
                'name': 'Feuerherz',
                'description': 'Ein kleiner, mutiger Drache',
                'personality': 'Neugierig und mutig',
                'goals': 'Fliegen lernen'
            }
            characters = {'main_character': main_char}
        
        if not scene and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            location = story_context.get('location', {})
            scene = {
                'setting': location.get('description', 'Drachenhöhle'),
                'time': 'Goldener Nachmittag',
                'atmosphere': location.get('mood', 'Gemütlich und sicher')
            }
        
        if not plot and 'story_context' in input_data:
            story_context = input_data.get('story_context', {})
            plot = {
                'main_event': 'Erster Flugversuch',
                'conflict': 'Angst vs. Wunsch zu fliegen',
                'resolution': 'Erfolgreicher erster Flug'
            }
        
        if not emotions and 'emotional_layer' in input_data:
            emotional_layer = input_data.get('emotional_layer', {})
            emotions = {
                'core_emotion': emotional_layer.get('core_emotion', 'Mut und Aufregung'),
                'emotional_arc': emotional_layer.get('emotional_tone', 'Von Nervosität zu Freude')
            }
        
        # Hole Sprachvarianten
        book_title = book_info.get('titles', {}).get(target_language, book_info.get('title', 'Unbekannt'))
        chapter_title = chapter_info.get('titles', {}).get(target_language, chapter_info.get('title', 'Unbekannt'))
        
        main_char = characters.get('main_character', {})
        char_lang_var = main_char.get('language_variants', {}).get(target_language, {})
        char_name = char_lang_var.get('name', main_char.get('name', 'Unbekannt'))
        char_desc = char_lang_var.get('description', main_char.get('description', 'Unbekannt'))
        
        scene_lang_var = scene.get('language_variants', {}).get(target_language, {})
        scene_setting = scene_lang_var.get('setting', scene.get('setting', 'Unbekannt'))
        scene_time = scene_lang_var.get('time', scene.get('time', 'Unbekannt'))
        scene_atmosphere = scene_lang_var.get('atmosphere', scene.get('atmosphere', 'Unbekannt'))
        
        style_lang_var = style.get('language_variants', {}).get(target_language, {})
        style_tone = style_lang_var.get('tone', style.get('tone', 'Unbekannt'))
        style_pacing = style_lang_var.get('pacing', style.get('pacing', 'Unbekannt'))
        style_dialogue = style_lang_var.get('dialogue_style', style.get('dialogue_style', 'Unbekannt'))
        
        emotions_lang_var = emotions.get('language_variants', {}).get(target_language, {})
        core_emotion = emotions_lang_var.get('core_emotion', emotions.get('core_emotion', 'Unbekannt'))
        emotional_arc = emotions_lang_var.get('emotional_arc', emotions.get('emotional_arc', 'Unbekannt'))
        
        # Erstelle sprachspezifischen Prompt
        prompt = f"""Du bist ein erfahrener Autor für {book_info.get('genre', 'Kinderbücher')}.

Buch: {book_title} ({book_info.get('genre', 'Unbekannt')})
Zielgruppe: {book_info.get('target_audience', 'Unbekannt')}
Thema: {book_info.get('theme', 'Unbekannt')}

Kapitel {chapter_info.get('number', '?')}: {chapter_title}
Zweck: {chapter_info.get('narrative_purpose', 'Unbekannt')}
Zielwortanzahl: {chapter_info.get('length_words', 800)}

Hauptfigur: {char_name} - {char_desc}
Persönlichkeit: {main_char.get('personality', 'Unbekannt')}

Szene: {scene_setting} ({scene_time})
Atmosphäre: {scene_atmosphere}

Handlung: {plot.get('main_event', 'Unbekannt')}
Konflikt: {plot.get('conflict', 'Unbekannt')}
Auflösung: {plot.get('resolution', 'Unbekannt')}

Stil: {style_tone}, {style_pacing}
Dialoge: {style_dialogue}

Emotionen: {core_emotion}
Emotionaler Bogen: {emotional_arc}

AUFGABE:
Erstelle ein fesselndes Kapitel in {target_language.upper()} mit etwa {chapter_info.get('length_words', 800)} Wörtern.
Das Kapitel sollte die angegebene emotionale Tiefe haben und den Leser mitreißen."""
        
        logger.info(f"Bilingualer Prompt erfolgreich kompiliert für {target_language.upper()} - Kapitel {chapter_info.get('number', 'Unbekannt')}")
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Fehler beim Kompilieren des bilingualen Prompts: {e}")
        raise

def validate_prompt_structure(prompt_frame: Dict) -> bool:
    """Validiert die Struktur des PromptFrames"""
    try:
        required_keys = ['input']
        input_keys = ['book', 'chapter']  # Minimale Anforderungen
        
        # Prüfe Hauptstruktur
        for key in required_keys:
            if key not in prompt_frame:
                logger.error(f"Fehlender Schlüssel in PromptFrame: '{key}'")
                return False
        
        # Prüfe Input-Struktur
        input_data = prompt_frame.get('input', {})
        for key in input_keys:
            if key not in input_data:
                logger.error(f"Fehlender Schlüssel in PromptFrame: '{key}'")
                return False
        
        # Prüfe bilinguale Konfiguration
        language_config = input_data.get('language', {})
        if language_config.get('bilingual_output', False):
            target_languages = language_config.get('target_languages', [])
            if len(target_languages) < 2:
                logger.warning("Bilinguale Ausgabe aktiviert, aber weniger als 2 Zielsprachen definiert")
        
        logger.info("PromptFrame-Struktur ist gültig")
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der PromptFrame-Validierung: {e}")
        return False

def get_prompt_metadata(prompt_frame: Dict) -> Dict:
    """Extrahiert Metadaten aus dem PromptFrame"""
    try:
        input_data = prompt_frame.get('input', {})
        
        metadata = {
            'book_title': input_data.get('book', {}).get('title', 'Unbekannt'),
            'chapter_number': input_data.get('chapter', {}).get('number', 'Unbekannt'),
            'chapter_title': input_data.get('chapter', {}).get('title', 'Unbekannt'),
            'target_languages': input_data.get('language', {}).get('target_languages', ['de']),
            'is_bilingual': input_data.get('language', {}).get('bilingual_output', False),
            'word_count_target': input_data.get('chapter', {}).get('length_words', 800)
        }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Metadaten: {e}")
        return {}
