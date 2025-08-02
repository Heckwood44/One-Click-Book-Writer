#!/usr/bin/env python3
"""
One Click Book Writer - Interaktive Demo
Simuliert die vollständige Anwendung ohne API-Keys
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from compiler.prompt_compiler import compile_prompt, compile_prompt_for_chatgpt, get_prompt_metadata
from schema.validate_input import validate_json_schema, validate_prompt_frame_structure


def interactive_demo():
    """Interaktive Demo der Anwendung."""
    
    print("🚀 One Click Book Writer - Interaktive Demo")
    print("=" * 50)
    print("Diese Demo zeigt den kompletten Workflow ohne API-Keys")
    print()
    
    # Verfügbare Engines anzeigen
    engines = ["claude", "chatgpt"]
    print(f"Verfügbare Engines: {', '.join(engines)}")
    
    # Eingabedatei wählen
    print("\n📁 Verfügbare Eingabedateien:")
    data_files = [f for f in os.listdir("data") if f.endswith(".json")]
    for i, file in enumerate(data_files, 1):
        print(f"  {i}. {file}")
    
    if not data_files:
        print("❌ Keine JSON-Dateien in data/ gefunden")
        return
    
    # Standardmäßig erste Datei verwenden
    input_file = f"data/{data_files[0]}"
    print(f"\n✅ Verwende: {input_file}")
    
    # Engine wählen
    print(f"\n🤖 Engine wählen ({'/'.join(engines)}):")
    engine = input("Engine (Standard: claude): ").strip().lower() or "claude"
    if engine not in engines:
        print(f"⚠️ Ungültige Engine '{engine}', verwende 'claude'")
        engine = "claude"
    
    print(f"✅ Gewählte Engine: {engine}")
    
    try:
        # 1. PromptFrame laden
        print(f"\n📖 Lade PromptFrame aus {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            prompt_frame = json.load(f)
        print("✅ PromptFrame erfolgreich geladen")
        
        # 2. Validierung
        print("\n🔍 Validiere Eingabe...")
        if not validate_prompt_frame_structure(prompt_frame):
            print("❌ Strukturvalidierung fehlgeschlagen")
            return
        
        if not validate_json_schema(prompt_frame, 'schema/prompt_frame.schema.json'):
            print("❌ Schema-Validierung fehlgeschlagen")
            return
        
        print("✅ Eingabe erfolgreich validiert")
        
        # 3. Metadaten anzeigen
        print("\n📊 PromptFrame Metadaten:")
        metadata = get_prompt_metadata(prompt_frame)
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        
        # 4. Prompt kompilieren
        print(f"\n⚙️ Kompiliere Prompt für {engine}...")
        if engine == "chatgpt":
            prompt = compile_prompt_for_chatgpt(prompt_frame)
        else:
            prompt = compile_prompt(prompt_frame)
        
        print(f"✅ Prompt kompiliert ({len(prompt)} Zeichen)")
        
        # 5. Prompt anzeigen
        print(f"\n📝 Kompilierter Prompt für {engine}:")
        print("-" * 60)
        print(prompt)
        print("-" * 60)
        
        # 6. Simulierte API-Antwort
        print(f"\n🤖 Simuliere {engine} API-Aufruf...")
        
        # Verschiedene simulierte Antworten basierend auf Engine
        if engine == "claude":
            simulated_text = f"""Kapitel {metadata['chapter_number']}: {metadata['chapter_title']}

Feuerherz stand am Rande der gemütlichen Drachenhöhle und schaute sehnsüchtig in die Ferne. Die warme Morgensonne kitzelte seine grünen Schuppen, während er die anderen Drachen beobachtete, die elegant durch die Lüfte tanzten. Seine kleinen Flügel zitterten vor Aufregung.

"Du schaffst das, mein Kleiner", flüsterte Mama Drache sanft und strich ihm mit ihrer warmen Schnauze über den Kopf. "Jeder Drache muss irgendwann seinen ersten Flug wagen."

Papa Drache nickte stolz. "Heute ist dein Tag, Feuerherz. Du bist bereit."

Feuerherz atmete tief ein. Angst und Aufregung kämpften in seinem kleinen Drachenherzen. Er spürte, wie sein Mut wuchs, während er sich langsam zum Abgrund bewegte.

"Du bist ein Drache", sagte er sich selbst. "Du kannst fliegen."

Mit einem letzten tiefen Atemzug sprang Feuerherz in die Luft. Für einen Moment fühlte er sich schwerelos, dann begannen seine Flügel zu schlagen. Zuerst unsicher, dann immer sicherer, bis er schließlich elegant durch die Lüfte glitt.

"Du fliegst!", rief Mama Drache begeistert.

Feuerherz jubelte innerlich. Er war endlich ein echter Drache!"""
        else:  # chatgpt
            simulated_text = f"""Kapitel {metadata['chapter_number']}: {metadata['chapter_title']}

Der kleine Drache Feuerherz blickte mit gemischten Gefühlen aus der warmen Drachenhöhle. Die Morgensonne tauchte die Berglandschaft in goldenes Licht, und er sah, wie seine Artgenossen majestätisch durch die Lüfte segelten. Sein Herz klopfte vor Aufregung.

Mama Drache trat neben ihn und legte sanft ihre Schnauze auf seinen Kopf. "Jeder von uns hat einmal so angefangen", sagte sie mit warmer Stimme. "Du bist bereit für deinen ersten Flug."

Papa Drache kam hinzu und nickte zustimmend. "Heute ist der Tag, an dem du lernst, was es bedeutet, ein Drache zu sein."

Feuerherz spürte, wie sich Angst und Mut in seiner Brust balgten. Er trat vorsichtig an den Rand der Höhle und blickte hinab. Die Welt lag weit unter ihm, aber er fühlte sich bereit.

"Du kannst es schaffen", flüsterte er sich zu und atmete tief ein.

Mit einem mutigen Sprung stürzte er sich in die Luft. Seine Flügel breiteten sich aus und fingen den Wind. Zuerst war es ein wildes Taumeln, dann fand er sein Gleichgewicht. Plötzlich glitt er elegant durch die Lüfte, so natürlich, als hätte er es schon immer gekonnt.

"Du fliegst!", jubelte Mama Drache.

Feuerherz war überglücklich. Er war endlich ein wahrer Drache!"""
        
        # 7. Ergebnis anzeigen
        print(f"\n📖 Generierter Text ({len(simulated_text)} Zeichen):")
        print("=" * 60)
        print(simulated_text)
        print("=" * 60)
        
        # 8. Speichern
        print(f"\n💾 Speichere Ergebnis...")
        os.makedirs("output/chapters", exist_ok=True)
        
        output_filename = f"chapter_{metadata['chapter_number']}_{metadata['chapter_title'].replace(' ', '_').lower()}.txt"
        output_path = f"output/chapters/{output_filename}"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(simulated_text)
        
        # Metadaten speichern
        metadata_filename = output_filename.replace(".txt", "_metadata.json")
        metadata_path = f"output/chapters/{metadata_filename}"
        
        result_metadata = {
            "text_length": len(simulated_text),
            "model": f"{engine}-simulated",
            "engine": engine,
            "usage": {
                "input_tokens": 450,
                "output_tokens": 320,
                "total_tokens": 770
            },
            "finish_reason": "stop",
            "metadata": {
                "temperature": 0.4,
                "max_tokens": 8000
            },
            "prompt_metadata": metadata
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(result_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Text gespeichert: {output_path}")
        print(f"✅ Metadaten gespeichert: {metadata_path}")
        
        # 9. Zusammenfassung
        print(f"\n🎉 Kapitel erfolgreich generiert!")
        print(f"📊 Token-Verbrauch: 770 (simuliert)")
        print(f"📝 Text-Länge: {len(simulated_text)} Zeichen")
        print(f"🤖 Verwendete Engine: {engine}")
        
        print(f"\n💡 Für echte AI-Generierung:")
        print(f"   1. Füge API-Keys in .env hinzu")
        print(f"   2. Führe 'python main.py --interactive' aus")
        print(f"   3. Oder: 'python main.py --input {input_file} --engine {engine}'")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    interactive_demo() 