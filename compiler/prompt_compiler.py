#!/usr/bin/env python3
"""
One Click Book Writer - Prompt Compiler (Canvas Execution Plan Version)
Version: 4.0.0 - Canvas Synchronized
"""

import json
import logging
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# =============================================================================
# CANVAS EXECUTION PLAN - STABILE SYSTEM NOTE MIT SIGNATUR
# =============================================================================

SYSTEM_NOTE = """SYSTEM NOTE (nicht ausgeben):
Ein Weltklasse-Autor ist kein Schreiberling. Er ist ein Architekt innerer Räume, ein Übersetzer des Unsichtbaren, ein Werkzeug für etwas Größeres. Schreibe ehrlich, warm und bildhaft. Passe Ton und Wortwahl an 6-jährige Kinder an.

SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"""

# =============================================================================
# DEFENSIVE FELDZUGRIFFE - CANVAS EXECUTION PLAN
# =============================================================================

def safe_get(data: Dict, *keys, default: str = "Unbekannt") -> str:
    """
    Defensive Feldzugriffe mit Fallback - Canvas Execution Plan
    
    Args:
        data: Dictionary to search in
        *keys: Nested keys to traverse
        default: Default value if path not found
    
    Returns:
        String value or default
    """
    try:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return str(current) if current is not None else default
    except (KeyError, TypeError, AttributeError):
        return default

def safe_get_nested(data: Dict, path: str, default: Any = None) -> Any:
    """
    Erweiterte defensive Feldzugriffe für komplexe Pfade
    
    Args:
        data: Dictionary to search in
        path: Dot-separated path (e.g., "book.titles.de")
        default: Default value if path not found
    
    Returns:
        Value or default
    """
    try:
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (KeyError, TypeError, AttributeError):
        return default

# =============================================================================
# PROMPT-HASHING - CANVAS EXECUTION PLAN
# =============================================================================

def generate_prompt_hash(prompt: str) -> str:
    """
    Generiert SHA256-Hash für Prompt-Versionierung - Canvas Execution Plan
    
    Args:
        prompt: The prompt string to hash
    
    Returns:
        First 16 characters of SHA256 hash
    """
    try:
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
    except Exception as e:
        logger.error(f"Fehler beim Generieren des Prompt-Hashes: {e}")
        return "0000000000000000"

def get_prompt_metadata(prompt_frame: Dict) -> Dict:
    """
    Extrahiert Metadaten aus dem PromptFrame - Canvas Execution Plan
    
    Args:
        prompt_frame: The prompt frame dictionary
    
    Returns:
        Dictionary with metadata
    """
    try:
        input_data = prompt_frame.get('input', {})
        
        metadata = {
            "compilation_timestamp": datetime.now().isoformat(),
            "book_title": safe_get(input_data, 'book', 'title'),
            "chapter_number": safe_get(input_data, 'chapter', 'number'),
            "chapter_title": safe_get(input_data, 'chapter', 'title'),
            "genre": safe_get(input_data, 'book', 'genre'),
            "target_audience": safe_get(input_data, 'book', 'target_audience'),
            "is_bilingual": input_data.get('language', {}).get('bilingual_output', False),
            "target_languages": input_data.get('language', {}).get('target_languages', ['de']),
            "word_count_target": safe_get(input_data, 'chapter', 'length_words', default='800')
        }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Metadaten: {e}")
        return {}

# =============================================================================
# BILINGUALE PROMPT-KOMPILIERUNG - CANVAS EXECUTION PLAN
# =============================================================================

def compile_prompt(prompt_frame: Dict) -> str:
    """
    Legacy-Support für Claude (Anthropic) - Canvas Execution Plan
    """
    return compile_prompt_for_chatgpt(prompt_frame)

def compile_prompt_for_chatgpt(prompt_frame: Dict) -> str:
    """
    Hauptfunktion: Kompiliert PromptFrame für ChatGPT (OpenAI) - Canvas Execution Plan
    
    Args:
        prompt_frame: The prompt frame dictionary
    
    Returns:
        Compiled prompt string
    """
    try:
        input_data = prompt_frame.get('input', {})
        
        # =====================================================================
        # DEFENSIVE EXTRAKTION MIT FALLBACKS - CANVAS EXECUTION PLAN
        # =====================================================================
        
        book_info = input_data.get('book', {})
        chapter_info = input_data.get('chapter', {})
        characters = input_data.get('characters', {})
        scene = input_data.get('scene', {})
        plot = input_data.get('plot', {})
        style = input_data.get('style', {})
        emotions = input_data.get('emotions', {})
        language_config = input_data.get('language', {})
        
        # =====================================================================
        # ROBUSTE FALLBACKS FÜR ALTE STRUKTUREN - CANVAS EXECUTION PLAN
        # =====================================================================
        
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
        
        # =====================================================================
        # BILINGUALE KONFIGURATION MIT FALLBACKS - CANVAS EXECUTION PLAN
        # =====================================================================
        
        is_bilingual = language_config.get('bilingual_output', False)
        target_languages = language_config.get('target_languages', ['de'])
        
        if is_bilingual and len(target_languages) >= 2:
            # =================================================================
            # BILINGUALER PROMPT MIT ZWEI SEKTIONEN - CANVAS EXECUTION PLAN
            # =================================================================
            
            german_prompt = compile_bilingual_prompt(prompt_frame, 'de')
            english_prompt = compile_bilingual_prompt(prompt_frame, 'en')
            
            german_title = safe_get(book_info, 'titles', 'de', default=safe_get(book_info, 'title'))
            english_title = safe_get(book_info, 'titles', 'en', default=safe_get(book_info, 'title'))
            
            prompt = f"""{SYSTEM_NOTE}

Du bist ein erfahrener Autor für {safe_get(book_info, 'genre', default='Kinderbücher')}. 
Erstelle ein fesselndes Kapitel in BEIDEN Sprachen basierend auf den folgenden Spezifikationen.

# DEUTSCHE VERSION
{german_prompt}

---

# ENGLISH VERSION
{english_prompt}

# ANWEISUNGEN
- Erstelle das KAPITEL in beiden Sprachen (nicht nur eine Zusammenfassung)
- Trenne die Versionen mit "---"
- Verwende die jeweiligen Titel: "{german_title}" / "{english_title}"
- Passe den Inhalt kulturell an (z.B. "Staunen" vs "wonder")
- Behalte die gleiche Handlung und Charakterentwicklung bei
- Zielwortanzahl pro Sprache: {safe_get(chapter_info, 'length_words', default='800')} Wörter
- Schreibe warm, bildhaft und kindgerecht
- Erzähle die GESAMTE Geschichte, nicht nur den Anfang
- Verwende natürliche Dialoge und lebendige Beschreibungen
- Stelle sicher, dass beide Versionen die gleiche emotionale Tiefe haben"""
        else:
            # =================================================================
            # MONOLINGUALER PROMPT (FALLBACK) - CANVAS EXECUTION PLAN
            # =================================================================
            
            prompt = f"""{SYSTEM_NOTE}

Du bist ein erfahrener Autor für {safe_get(book_info, 'genre', default='Kinderbücher')}.

Buch: {safe_get(book_info, 'title')} ({safe_get(book_info, 'genre', default='Unbekannt')})
Zielgruppe: {safe_get(book_info, 'target_audience', default='Unbekannt')}
Thema: {safe_get(book_info, 'theme', default='Unbekannt')}

Kapitel {safe_get(chapter_info, 'number', default='?')}: {safe_get(chapter_info, 'title', default='Unbekannt')}
Zweck: {safe_get(chapter_info, 'narrative_purpose', default='Unbekannt')}
Zielwortanzahl: {safe_get(chapter_info, 'length_words', default='800')}

Hauptfigur: {safe_get(characters, 'main_character', 'name', default='Unbekannt')} - {safe_get(characters, 'main_character', 'description', default='Unbekannt')}
Persönlichkeit: {safe_get(characters, 'main_character', 'personality', default='Unbekannt')}

Szene: {safe_get(scene, 'setting', default='Unbekannt')} ({safe_get(scene, 'time', default='Unbekannt')})
Atmosphäre: {safe_get(scene, 'atmosphere', default='Unbekannt')}

Handlung: {safe_get(plot, 'main_event', default='Unbekannt')}
Konflikt: {safe_get(plot, 'conflict', default='Unbekannt')}
Auflösung: {safe_get(plot, 'resolution', default='Unbekannt')}

Stil: {safe_get(style, 'tone', default='Unbekannt')}
Tempo: {safe_get(style, 'pacing', default='Unbekannt')}
Dialog-Stil: {safe_get(style, 'dialogue_style', default='Unbekannt')}

Kernemotion: {safe_get(emotions, 'core_emotion', default='Unbekannt')}
Emotionaler Bogen: {safe_get(emotions, 'emotional_arc', default='Unbekannt')}

# ANWEISUNGEN
- Schreibe ein vollständiges Kapitel mit {safe_get(chapter_info, 'length_words', default='800')} Wörtern
- Verwende warme, bildhafte Sprache
- Erzähle die komplette Geschichte mit Anfang, Mitte und Ende
- Integriere natürliche Dialoge
- Schaffe emotionale Tiefe und Spannung"""
        
        logger.info(f"ChatGPT-Prompt erfolgreich kompiliert für Kapitel {safe_get(chapter_info, 'number', default='Unbekannt')}")
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Fehler beim Kompilieren des ChatGPT-Prompts: {e}")
        raise

def compile_bilingual_prompt(prompt_frame: Dict, target_language: str) -> str:
    """
    Kompiliert PromptFrame für eine spezifische Zielsprache - Canvas Execution Plan
    
    Args:
        prompt_frame: The prompt frame dictionary
        target_language: Target language code ('de' or 'en')
    
    Returns:
        Language-specific prompt string
    """
    try:
        input_data = prompt_frame.get('input', {})
        
        # =====================================================================
        # DEFENSIVE EXTRAKTION - CANVAS EXECUTION PLAN
        # =====================================================================
        
        book_info = input_data.get('book', {})
        chapter_info = input_data.get('chapter', {})
        characters = input_data.get('characters', {})
        scene = input_data.get('scene', {})
        plot = input_data.get('plot', {})
        style = input_data.get('style', {})
        emotions = input_data.get('emotions', {})
        
        # =====================================================================
        # FALLBACKS FÜR ALTE STRUKTUREN - CANVAS EXECUTION PLAN
        # =====================================================================
        
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
        
        # =====================================================================
        # SPRACHSPEZIFISCHE VARIANTEN MIT FALLBACKS - CANVAS EXECUTION PLAN
        # =====================================================================
        
        book_title = safe_get(book_info, 'titles', target_language, default=safe_get(book_info, 'title'))
        chapter_title = safe_get(chapter_info, 'titles', target_language, default=safe_get(chapter_info, 'title'))
        
        main_char = characters.get('main_character', {})
        char_lang_var = main_char.get('language_variants', {}).get(target_language, {})
        char_name = safe_get(char_lang_var, 'name', default=safe_get(main_char, 'name'))
        char_desc = safe_get(char_lang_var, 'description', default=safe_get(main_char, 'description'))
        
        scene_lang_var = scene.get('language_variants', {}).get(target_language, {})
        scene_setting = safe_get(scene_lang_var, 'setting', default=safe_get(scene, 'setting'))
        scene_time = safe_get(scene_lang_var, 'time', default=safe_get(scene, 'time'))
        scene_atmosphere = safe_get(scene_lang_var, 'atmosphere', default=safe_get(scene, 'atmosphere'))
        
        style_lang_var = style.get('language_variants', {}).get(target_language, {})
        style_tone = safe_get(style_lang_var, 'tone', default=safe_get(style, 'tone'))
        style_pacing = safe_get(style_lang_var, 'pacing', default=safe_get(style, 'pacing'))
        style_dialogue = safe_get(style_lang_var, 'dialogue_style', default=safe_get(style, 'dialogue_style'))
        
        emotions_lang_var = emotions.get('language_variants', {}).get(target_language, {})
        core_emotion = safe_get(emotions_lang_var, 'core_emotion', default=safe_get(emotions, 'core_emotion'))
        emotional_arc = safe_get(emotions_lang_var, 'emotional_arc', default=safe_get(emotions, 'emotional_arc'))
        
        # =====================================================================
        # ERSTELLE SPRACHSPEZIFISCHEN PROMPT - CANVAS EXECUTION PLAN
        # =====================================================================
        
        prompt = f"""{SYSTEM_NOTE}

Du bist ein erfahrener Autor für {safe_get(book_info, 'genre', default='Kinderbücher')}.

Buch: {book_title} ({safe_get(book_info, 'genre', default='Unbekannt')})
Zielgruppe: {safe_get(book_info, 'target_audience', default='Unbekannt')}
Thema: {safe_get(book_info, 'theme', default='Unbekannt')}

Kapitel {safe_get(chapter_info, 'number', default='?')}: {chapter_title}
Zweck: {safe_get(chapter_info, 'narrative_purpose', default='Unbekannt')}
Zielwortanzahl: {safe_get(chapter_info, 'length_words', default='800')}

Hauptfigur: {char_name} - {char_desc}
Persönlichkeit: {safe_get(main_char, 'personality', default='Unbekannt')}

Szene: {scene_setting} ({scene_time})
Atmosphäre: {scene_atmosphere}

Handlung: {safe_get(plot, 'main_event', default='Unbekannt')}
Konflikt: {safe_get(plot, 'conflict', default='Unbekannt')}
Auflösung: {safe_get(plot, 'resolution', default='Unbekannt')}

Stil: {style_tone}
Tempo: {style_pacing}
Dialog-Stil: {style_dialogue}

Kernemotion: {core_emotion}
Emotionaler Bogen: {emotional_arc}

# ANWEISUNGEN
- Schreibe ein vollständiges Kapitel mit {safe_get(chapter_info, 'length_words', default='800')} Wörtern
- Verwende warme, bildhafte Sprache
- Erzähle die komplette Geschichte mit Anfang, Mitte und Ende
- Integriere natürliche Dialoge
- Schaffe emotionale Tiefe und Spannung"""
        
        logger.info(f"Bilingualer Prompt erfolgreich kompiliert für {target_language.upper()} - Kapitel {safe_get(chapter_info, 'number', default='Unbekannt')}")
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Fehler beim Kompilieren des bilingualen Prompts: {e}")
        raise

# =============================================================================
# VALIDIERUNG - CANVAS EXECUTION PLAN
# =============================================================================

def validate_prompt_structure(prompt_frame: Dict) -> bool:
    """
    Validiert die PromptFrame-Struktur mit Fallbacks - Canvas Execution Plan
    
    Args:
        prompt_frame: The prompt frame dictionary
    
    Returns:
        True if valid, False otherwise
    """
    try:
        input_data = prompt_frame.get('input', {})
        
        # =====================================================================
        # ERFORDERLICHE FELDER PRÜFEN - CANVAS EXECUTION PLAN
        # =====================================================================
        
        required_sections = ['book', 'chapter']
        for section in required_sections:
            if section not in input_data:
                logger.warning(f"Fehlende Sektion: {section}")
                return False
        
        # =====================================================================
        # FALLBACK-LOGIK FÜR BILINGUALE KONFIGURATION - CANVAS EXECUTION PLAN
        # =====================================================================
        
        language_config = input_data.get('language', {})
        if 'bilingual_output' not in language_config:
            logger.info("Bilinguale Konfiguration nicht gefunden, setze Fallback")
            language_config['bilingual_output'] = False
            language_config['target_languages'] = ['de']
        
        if 'target_languages' not in language_config:
            language_config['target_languages'] = ['de']
        
        logger.info("PromptFrame-Struktur ist gültig")
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der PromptFrame-Validierung: {e}")
        return False

# =============================================================================
# CLAUDE-OPTIMIZER HOOK - CANVAS EXECUTION PLAN
# =============================================================================

def prepare_claude_optimization_hook(prompt: str, prompt_frame: Dict) -> str:
    """
    Bereitet Hook für Claude-Optimierung vor - Canvas Execution Plan
    
    Args:
        prompt: The raw prompt
        prompt_frame: The prompt frame dictionary
    
    Returns:
        Optimization-ready prompt
    """
    try:
        # =====================================================================
        # OPTIMIERUNGS-HOOK VORBEREITUNG - CANVAS EXECUTION PLAN
        # =====================================================================
        
        optimization_instruction = f"""
OPTIMIERUNGS-AUFTRAG FÜR CLAUDE:
Analysiere und verbessere den folgenden Prompt für die Kapitelgenerierung:

{prompt}

ZIELE DER OPTIMIERUNG:
1. Klarheit und Struktur verbessern
2. Emotionale Tiefe verstärken
3. Bilinguale Konsistenz sicherstellen
4. Wortlimit-Compliance optimieren
5. Kindgerechte Sprache verfeinern

GIB DEN OPTIMIERTEN PROMPT ZURÜCK, OHNE ZUSÄTZLICHE ERKLÄRUNGEN.
"""
        
        return optimization_instruction.strip()
        
    except Exception as e:
        logger.error(f"Fehler bei der Claude-Optimierung-Vorbereitung: {e}")
        return prompt

# =============================================================================
# HAUPTFUNKTION - CANVAS EXECUTION PLAN
# =============================================================================

def main():
    """
    Hauptfunktion für direkte Ausführung - Canvas Execution Plan
    """
    import sys
    
    if len(sys.argv) != 2:
        print("Verwendung: python prompt_compiler.py <prompt_frame.json>")
        sys.exit(1)
    
    try:
        # =====================================================================
        # PROMPTFRAME LADEN - CANVAS EXECUTION PLAN
        # =====================================================================
        
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            prompt_frame = json.load(f)
        
        # =====================================================================
        # PROMPT KOMPILIEREN - CANVAS EXECUTION PLAN
        # =====================================================================
        
        prompt = compile_prompt_for_chatgpt(prompt_frame)
        prompt_hash = generate_prompt_hash(prompt)
        
        # =====================================================================
        # AUSGABE - CANVAS EXECUTION PLAN
        # =====================================================================
        
        print("=" * 80)
        print("CANVAS EXECUTION PLAN - KOMPILIERTER PROMPT")
        print("=" * 80)
        print(prompt)
        print("\n" + "=" * 80)
        print(f"PROMPT-HASH: {prompt_hash}")
        print(f"PROMPT-LÄNGE: {len(prompt)} Zeichen")
        print(f"KOMPILIERUNGS-ZEIT: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # =====================================================================
        # VALIDIERUNG - CANVAS EXECUTION PLAN
        # =====================================================================
        
        # Bilinguale Struktur prüfen
        if "---" in prompt:
            print("✅ Bilinguale Struktur erkannt")
        else:
            print("⚠️  Keine bilinguale Struktur gefunden")
        
        # System Note prüfen
        system_note_signature = "SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"
        if system_note_signature in prompt:
            print("✅ System Note mit Signatur erkannt")
        else:
            print("❌ System Note nicht gefunden")
        
        # Claude-Optimierung Hook prüfen
        if "Claude" in prompt or "OPTIMIERUNG" in prompt:
            print("✅ Claude-Optimierung Hook erkannt")
        else:
            print("ℹ️  Claude-Optimierung Hook nicht aktiv")
        
        # =====================================================================
        # METADATEN AUSGABE - CANVAS EXECUTION PLAN
        # =====================================================================
        
        metadata = get_prompt_metadata(prompt_frame)
        print(f"\n📊 METADATEN:")
        print(f"   Buch: {metadata.get('book_title', 'Unbekannt')}")
        print(f"   Kapitel: {metadata.get('chapter_number', '?')} - {metadata.get('chapter_title', 'Unbekannt')}")
        print(f"   Genre: {metadata.get('genre', 'Unbekannt')}")
        print(f"   Bilingual: {metadata.get('is_bilingual', False)}")
        print(f"   Zielsprachen: {metadata.get('target_languages', ['de'])}")
        print(f"   Wortziel: {metadata.get('word_count_target', '800')}")
        
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
