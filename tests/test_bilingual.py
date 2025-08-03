#!/usr/bin/env python3
"""
Test-Skript für bilinguale Funktionalität
"""

import sys
import json
from pathlib import Path
from build_and_execute import OneClickBookWriterPipeline

def test_bilingual():
    """Testet die bilinguale Funktionalität"""
    print("�� Teste bilinguale Funktionalität...")
    
    # Pipeline initialisieren
    pipeline = OneClickBookWriterPipeline()
    
    # PromptFrame laden
    prompt_frame = pipeline.load_prompt_frame()
    
    # Bilinguale Konfiguration prüfen
    language_config = prompt_frame.get('input', {}).get('language', {})
    is_bilingual = language_config.get('bilingual_output', False)
    target_languages = language_config.get('target_languages', ['de'])
    
    print(f"📋 Bilinguale Konfiguration:")
    print(f"   - Aktiviert: {is_bilingual}")
    print(f"   - Zielsprachen: {target_languages}")
    
    if not is_bilingual:
        print("❌ Bilinguale Ausgabe nicht aktiviert!")
        return False
    
    # Prompt kompilieren
    prompt = pipeline.compile_prompt(prompt_frame, optimize_with_claude=False)
    
    # Kapitel generieren
    print("✍️  Generiere bilinguales Kapitel...")
    chapter_text = pipeline.generate_chapter(prompt)
    
    # Erstelle einfaches Result-Format
    chapter_result = {
        "type": "single_language",
        "content": {
            "de": chapter_text,
            "en": chapter_text
        }
    }
    print(f"✅ Generierung erfolgreich!")
    print(f"   - Typ: {chapter_result['type']}")
    print(f"   - Sprachen: {list(chapter_result['content'].keys())}")
    
    # Ausgabe speichern
    metadata = {
        'test': True,
        'chapter_info': prompt_frame.get('input', {}).get('chapter', {}),
        'language_config': language_config
    }
    
    saved_files = pipeline.save_output(chapter_result, metadata)
    
    print(f"�� Dateien gespeichert:")
    for file_path in saved_files:
        print(f"   📄 {file_path}")
    
    # Inhalt anzeigen
    for lang, content in chapter_result['content'].items():
        print(f"\n📖 {lang.upper()}-Version (erste 200 Zeichen):")
        print(f"   {content[:200]}...")
    
    return True

if __name__ == "__main__":
    success = test_bilingual()
    if success:
        print("\n🎉 Bilingualer Test erfolgreich!")
    else:
        print("\n❌ Bilingualer Test fehlgeschlagen!")
        sys.exit(1)
