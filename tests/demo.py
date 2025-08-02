#!/usr/bin/env python3
"""
One Click Book Writer - Demo
Demonstriert den kompletten Workflow ohne API-Keys
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from compiler.prompt_compiler import compile_prompt, compile_prompt_for_chatgpt, get_prompt_metadata
from schema.validate_input import validate_json_schema, validate_prompt_frame_structure


def demo_workflow():
    """Demonstriert den kompletten Workflow."""
    
    print("🚀 One Click Book Writer - Demo")
    print("=" * 50)
    
    # 1. PromptFrame laden
    print("\n1️⃣ Lade PromptFrame...")
    try:
        with open('data/generate_chapter_full_extended.json', 'r', encoding='utf-8') as f:
            prompt_frame = json.load(f)
        print("✅ PromptFrame erfolgreich geladen")
    except Exception as e:
        print(f"❌ Fehler beim Laden: {e}")
        return
    
    # 2. Strukturvalidierung
    print("\n2️⃣ Validiere Struktur...")
    if validate_prompt_frame_structure(prompt_frame):
        print("✅ Struktur ist gültig")
    else:
        print("❌ Struktur ist ungültig")
        return
    
    # 3. Schema-Validierung
    print("\n3️⃣ Validiere gegen JSON-Schema...")
    if validate_json_schema(prompt_frame, 'schema/prompt_frame.schema.json'):
        print("✅ Schema-Validierung erfolgreich")
    else:
        print("❌ Schema-Validierung fehlgeschlagen")
        return
    
    # 4. Metadaten extrahieren
    print("\n4️⃣ Extrahiere Metadaten...")
    metadata = get_prompt_metadata(prompt_frame)
    print("📊 Metadaten:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")
    
    # 5. Prompt für Claude kompilieren
    print("\n5️⃣ Kompiliere Prompt für Claude...")
    try:
        claude_prompt = compile_prompt(prompt_frame)
        print(f"✅ Claude-Prompt kompiliert ({len(claude_prompt)} Zeichen)")
        print("\n📝 Claude-Prompt (Auszug):")
        print("-" * 40)
        print(claude_prompt[:300] + "..." if len(claude_prompt) > 300 else claude_prompt)
    except Exception as e:
        print(f"❌ Fehler bei Claude-Prompt: {e}")
        return
    
    # 6. Prompt für ChatGPT kompilieren
    print("\n6️⃣ Kompiliere Prompt für ChatGPT...")
    try:
        chatgpt_prompt = compile_prompt_for_chatgpt(prompt_frame)
        print(f"✅ ChatGPT-Prompt kompiliert ({len(chatgpt_prompt)} Zeichen)")
        print("\n📝 ChatGPT-Prompt (Auszug):")
        print("-" * 40)
        print(chatgpt_prompt[:300] + "..." if len(chatgpt_prompt) > 300 else chatgpt_prompt)
    except Exception as e:
        print(f"❌ Fehler bei ChatGPT-Prompt: {e}")
        return
    
    # 7. Prompt in Datei speichern
    print("\n7️⃣ Speichere kompilierte Prompts...")
    try:
        os.makedirs("tmp", exist_ok=True)
        
        with open("tmp/claude_prompt.txt", "w", encoding="utf-8") as f:
            f.write(claude_prompt)
        
        with open("tmp/chatgpt_prompt.txt", "w", encoding="utf-8") as f:
            f.write(chatgpt_prompt)
        
        print("✅ Prompts gespeichert in tmp/")
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")
    
    # 8. Simulierte API-Antwort
    print("\n8️⃣ Simuliere API-Antwort...")
    simulated_response = {
        "text": f"""Kapitel 1: Der erste Flug

Feuerherz stand am Rande der gemütlichen Drachenhöhle und schaute sehnsüchtig in die Ferne. Die warme Morgensonne kitzelte seine grünen Schuppen, während er die anderen Drachen beobachtete, die elegant durch die Lüfte tanzten. Seine kleinen Flügel zitterten vor Aufregung.

"Du schaffst das, mein Kleiner", flüsterte Mama Drache sanft und strich ihm mit ihrer warmen Schnauze über den Kopf. "Jeder Drache muss irgendwann seinen ersten Flug wagen."

Papa Drache nickte stolz. "Heute ist dein Tag, Feuerherz. Du bist bereit."

Feuerherz atmete tief ein. Angst und Aufregung kämpften in seinem kleinen Drachenherzen. Er spürte, wie sein Mut wuchs, während er sich langsam zum Abgrund bewegte.

"Du bist ein Drache", sagte er sich selbst. "Du kannst fliegen."

Mit einem letzten tiefen Atemzug sprang Feuerherz in die Luft. Für einen Moment fühlte er sich schwerelos, dann begannen seine Flügel zu schlagen. Zuerst unsicher, dann immer sicherer, bis er schließlich elegant durch die Lüfte glitt.

"Du fliegst!", rief Mama Drache begeistert.

Feuerherz jubelte innerlich. Er war endlich ein echter Drache!""",
        "model": "claude-3-opus-20240229",
        "usage": {
            "input_tokens": 450,
            "output_tokens": 320,
            "total_tokens": 770
        },
        "finish_reason": "stop",
        "metadata": {
            "temperature": 0.4,
            "max_tokens": 8000
        }
    }
    
    print("✅ Simulierte Antwort erstellt")
    print(f"📊 Token-Verbrauch: {simulated_response['usage']['total_tokens']}")
    print(f"📝 Text-Länge: {len(simulated_response['text'])} Zeichen")
    
    # 9. Ergebnis speichern
    print("\n9️⃣ Speichere Ergebnis...")
    try:
        os.makedirs("output/chapters", exist_ok=True)
        
        # Text speichern
        output_path = "output/chapters/chapter_1_der_erste_flug.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(simulated_response["text"])
        
        # Metadaten speichern
        metadata_path = "output/chapters/chapter_1_der_erste_flug_metadata.json"
        result_metadata = {
            "text_length": len(simulated_response["text"]),
            "model": simulated_response["model"],
            "engine": "claude",
            "usage": simulated_response["usage"],
            "finish_reason": simulated_response["finish_reason"],
            "metadata": simulated_response["metadata"],
            "prompt_metadata": metadata
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(result_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Ergebnis gespeichert: {output_path}")
        print(f"✅ Metadaten gespeichert: {metadata_path}")
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")
    
    print("\n🎉 Demo erfolgreich abgeschlossen!")
    print("\n📁 Erstellte Dateien:")
    print("   - tmp/claude_prompt.txt")
    print("   - tmp/chatgpt_prompt.txt")
    print("   - output/chapters/chapter_1_der_erste_flug.txt")
    print("   - output/chapters/chapter_1_der_erste_flug_metadata.json")
    
    print("\n💡 Nächste Schritte:")
    print("   1. Füge deine API-Keys in .env hinzu")
    print("   2. Führe 'python main.py --interactive' aus")
    print("   3. Oder verwende: 'python main.py --input data/generate_chapter_full_extended.json --engine claude'")


if __name__ == "__main__":
    demo_workflow() 