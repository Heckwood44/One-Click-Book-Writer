#!/usr/bin/env python3
"""
One Click Book Writer - Hauptanwendung
KI-basiertes Tool zur automatisierten Kapitelgenerierung
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import project modules
from compiler.prompt_compiler import compile_prompt, compile_prompt_for_chatgpt, validate_prompt_structure
from engine.claude_adapter import ClaudeAdapter
from engine.openai_adapter import OpenAIAdapter
from schema.validate_input import validate_json_schema

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OneClickBookWriter:
    """
    Hauptklasse für die One Click Book Writer Anwendung.
    """
    
    def __init__(self):
        """Initialisiert die Anwendung."""
        self.claude_adapter = None
        self.openai_adapter = None
        self.setup_adapters()
    
    def setup_adapters(self):
        """Richtet die AI-Adapter ein."""
        try:
            # Claude Adapter
            if os.getenv("ANTHROPIC_API_KEY"):
                self.claude_adapter = ClaudeAdapter()
                logger.info("Claude Adapter erfolgreich initialisiert")
            else:
                logger.warning("ANTHROPIC_API_KEY nicht gefunden - Claude nicht verfügbar")
            
            # OpenAI Adapter
            if os.getenv("OPENAI_API_KEY"):
                self.openai_adapter = OpenAIAdapter()
                logger.info("OpenAI Adapter erfolgreich initialisiert")
            else:
                logger.warning("OPENAI_API_KEY nicht gefunden - ChatGPT nicht verfügbar")
                
        except Exception as e:
            logger.error(f"Fehler beim Einrichten der Adapter: {e}")
    
    def load_prompt_frame(self, file_path: str) -> Dict[str, Any]:
        """
        Lädt ein PromptFrame aus einer JSON-Datei.
        
        Args:
            file_path: Pfad zur JSON-Datei
            
        Returns:
            PromptFrame Dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_frame = json.load(f)
            
            logger.info(f"PromptFrame geladen aus: {file_path}")
            return prompt_frame
            
        except FileNotFoundError:
            logger.error(f"Datei nicht gefunden: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ungültige JSON-Datei: {e}")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Laden der Datei: {e}")
            raise
    
    def validate_input(self, prompt_frame: Dict[str, Any]) -> bool:
        """
        Validiert ein PromptFrame gegen das Schema.
        
        Args:
            prompt_frame: Zu validierendes PromptFrame
            
        Returns:
            True wenn gültig
        """
        try:
            # Strukturvalidierung
            if not validate_prompt_structure(prompt_frame):
                logger.error("PromptFrame-Struktur ist ungültig")
                return False
            
            # Schema-Validierung
            schema_path = "schema/prompt_frame.schema.json"
            if not validate_json_schema(prompt_frame, schema_path):
                logger.error("PromptFrame entspricht nicht dem Schema")
                return False
            
            logger.info("PromptFrame erfolgreich validiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Validierung: {e}")
            return False
    
    def generate_chapter(self, prompt_frame: Dict[str, Any], engine: str = "claude", **kwargs) -> Dict[str, Any]:
        """
        Generiert ein Kapitel mit dem gewählten AI-Engine.
        
        Args:
            prompt_frame: PromptFrame für die Generierung
            engine: AI-Engine ("claude" oder "chatgpt")
            **kwargs: Zusätzliche Parameter
            
        Returns:
            Dictionary mit dem generierten Kapitel und Metadaten
        """
        try:
            # Prompt kompilieren
            if engine.lower() == "chatgpt":
                prompt = compile_prompt_for_chatgpt(prompt_frame)
                adapter = self.openai_adapter
            else:
                prompt = compile_prompt(prompt_frame)
                adapter = self.claude_adapter
            
            if not adapter:
                raise ValueError(f"Adapter für {engine} nicht verfügbar")
            
            # Prompt in temporäre Datei speichern
            os.makedirs("tmp", exist_ok=True)
            with open("tmp/generated_prompt.txt", "w", encoding="utf-8") as f:
                f.write(prompt)
            
            logger.info(f"Generiere Kapitel mit {engine}")
            
            # Kapitel generieren
            result = adapter.generate_chapter_with_retry(prompt, **kwargs)
            
            # Validierung
            if not adapter.validate_response(result):
                logger.warning("Generierte Antwort ist möglicherweise unvollständig")
            
            # Metadaten hinzufügen
            result["prompt_frame"] = prompt_frame
            result["engine"] = engine
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Kapitelgenerierung: {e}")
            raise
    
    def save_result(self, result: Dict[str, Any], output_path: str = None) -> str:
        """
        Speichert das generierte Ergebnis.
        
        Args:
            result: Generiertes Ergebnis
            output_path: Ausgabepfad (optional)
            
        Returns:
            Pfad zur gespeicherten Datei
        """
        try:
            if not output_path:
                chapter_info = result.get("prompt_frame", {}).get("input", {}).get("chapter", {})
                chapter_num = chapter_info.get("number", "unknown")
                chapter_title = chapter_info.get("title", "chapter").replace(" ", "_")
                output_path = f"output/chapters/chapter_{chapter_num}_{chapter_title}.txt"
            
            # Verzeichnis erstellen
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Text speichern
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
            
            # Metadaten als JSON speichern
            metadata_path = output_path.replace(".txt", "_metadata.json")
            metadata = {
                "text_length": len(result["text"]),
                "model": result["model"],
                "engine": result["engine"],
                "usage": result["usage"],
                "finish_reason": result["finish_reason"],
                "metadata": result["metadata"]
            }
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Ergebnis gespeichert: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
            raise
    
    def run_interactive(self):
        """Führt die Anwendung im interaktiven Modus aus."""
        print("🚀 One Click Book Writer")
        print("=" * 50)
        
        # Verfügbare Engines anzeigen
        engines = []
        if self.claude_adapter:
            engines.append("claude")
        if self.openai_adapter:
            engines.append("chatgpt")
        
        if not engines:
            print("❌ Keine AI-Engines verfügbar. Bitte API-Keys konfigurieren.")
            return
        
        print(f"Verfügbare Engines: {', '.join(engines)}")
        
        # Eingabedatei wählen
        input_file = input("Pfad zur JSON-Eingabedatei: ").strip()
        if not input_file:
            print("❌ Keine Eingabedatei angegeben.")
            return
        
        # Engine wählen
        engine = input(f"Engine wählen ({'/'.join(engines)}): ").strip().lower()
        if engine not in engines:
            print(f"❌ Ungültige Engine: {engine}")
            return
        
        try:
            # PromptFrame laden und validieren
            prompt_frame = self.load_prompt_frame(input_file)
            if not self.validate_input(prompt_frame):
                print("❌ Eingabe ist ungültig.")
                return
            
            # Kapitel generieren
            print("🔄 Generiere Kapitel...")
            result = self.generate_chapter(prompt_frame, engine)
            
            # Ergebnis speichern
            output_path = self.save_result(result)
            
            print(f"✅ Kapitel erfolgreich generiert: {output_path}")
            print(f"📊 Tokens verwendet: {result['usage']['total_tokens']}")
            
        except Exception as e:
            print(f"❌ Fehler: {e}")


def main():
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(description="One Click Book Writer")
    parser.add_argument("--input", "-i", help="Pfad zur JSON-Eingabedatei")
    parser.add_argument("--output", "-o", help="Ausgabepfad")
    parser.add_argument("--engine", "-e", choices=["claude", "chatgpt"], default="claude", help="AI-Engine")
    parser.add_argument("--temperature", "-t", type=float, default=0.4, help="Temperature für die Generierung")
    parser.add_argument("--max-tokens", type=int, help="Maximale Anzahl Tokens")
    parser.add_argument("--interactive", action="store_true", help="Interaktiver Modus")
    
    args = parser.parse_args()
    
    try:
        app = OneClickBookWriter()
        
        if args.interactive or not args.input:
            app.run_interactive()
        else:
            # Kommandozeilen-Modus
            prompt_frame = app.load_prompt_frame(args.input)
            if not app.validate_input(prompt_frame):
                sys.exit(1)
            
            result = app.generate_chapter(
                prompt_frame, 
                args.engine,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )
            
            output_path = app.save_result(result, args.output)
            print(f"✅ Kapitel generiert: {output_path}")
            
    except KeyboardInterrupt:
        print("\n⚠️ Abgebrochen durch Benutzer")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Anwendungsfehler: {e}")
        print(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 