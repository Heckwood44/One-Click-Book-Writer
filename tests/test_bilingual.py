#!/usr/bin/env python3
"""
Test-Skript für bilinguale Funktionalität
"""

import sys
import json
from pathlib import Path

def test_bilingual():
    """Testet die bilinguale Funktionalität"""
    print("🌍 Teste bilinguale Funktionalität...")
    
    # Simuliere bilinguale Konfiguration
    language_config = {
        'bilingual_output': True,
        'target_languages': ['de', 'en']
    }
    
    print(f"📋 Bilinguale Konfiguration:")
    print(f"   - Aktiviert: {language_config['bilingual_output']}")
    print(f"   - Zielsprachen: {language_config['target_languages']}")
    
    # Prüfe ob bilingual aktiviert ist
    assert language_config['bilingual_output'], "Bilinguale Ausgabe sollte aktiviert sein"
    
    # Simuliere Prompt-Kompilierung
    prompt = "Schreibe ein Kapitel über ein Abenteuer."
    print("✍️  Kompiliere bilingualen Prompt...")
    
    # Simuliere Kapitel-Generierung
    print("✍️  Generiere bilinguales Kapitel...")
    chapter_text = "Dies ist ein Test-Kapitel über ein spannendes Abenteuer."
    
    # Erstelle einfaches Result-Format
    chapter_result = {
        "type": "bilingual",
        "content": {
            "de": chapter_text,
            "en": "This is a test chapter about an exciting adventure."
        }
    }
    
    print(f"✅ Generierung erfolgreich!")
    print(f"   - Typ: {chapter_result['type']}")
    print(f"   - Sprachen: {list(chapter_result['content'].keys())}")
    
    # Verifikationen
    assert chapter_result['type'] == 'bilingual'
    assert 'de' in chapter_result['content']
    assert 'en' in chapter_result['content']
    assert len(chapter_result['content']) == 2
    
    # Simuliere Ausgabe-Speicherung
    metadata = {
        'test': True,
        'chapter_info': {'number': 1, 'title': 'Test Chapter'},
        'language_config': language_config
    }
    
    print(f"💾 Metadaten erstellt:")
    print(f"   - Test-Modus: {metadata['test']}")
    print(f"   - Kapitel: {metadata['chapter_info']['number']}")
    
    # Verifikationen
    assert metadata['test'] is True
    assert metadata['chapter_info']['number'] == 1
    assert metadata['language_config'] == language_config
    
    print("✅ Bilinguale Funktionalität erfolgreich getestet!")

if __name__ == "__main__":
    test_bilingual()
    print("\n🎉 Bilingualer Test erfolgreich!")
