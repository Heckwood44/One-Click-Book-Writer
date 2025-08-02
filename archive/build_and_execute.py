#!/usr/bin/env python3
"""
One Click Book Writer - Build & Execution Pipeline

Implementiert die vollständige Pipeline für KI-gestützte Buchgenerierung:
1. JSON-PromptFrame laden und validieren
2. Prompt kompilieren (mit optionaler Claude-Optimierung)
3. Kapiteltext mit ChatGPT generieren
4. Ausgabe speichern und GUI-Status aktualisieren

Author: One Click Book Writer Team
Version: 1.0.0
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Projekt-Module importieren
from key_check import APIKeyChecker
from compiler.prompt_compiler import compile_prompt, compile_prompt_for_chatgpt
from schema.validate_input import validate_json_schema
import openai
import anthropic

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OneClickBookWriterPipeline:
    """Hauptklasse für die Build & Execution Pipeline"""
    
    def __init__(self):
        """Initialisiert die Pipeline"""
        self.key_checker = APIKeyChecker()
        self.openai_client = None
        self.claude_client = None
        self.setup_clients()
        
        # Pfade konfigurieren
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"
        self.schema_dir = self.project_root / "schema"
        
        # Standard-Dateien
        self.default_json_file = self.data_dir / "generate_chapter_full_extended.json"
        self.schema_file = self.schema_dir / "prompt_frame.schema.json"
        self.output_file = self.output_dir / "chapter_result.txt"
        
        # Erstelle Output-Verzeichnis falls nicht vorhanden
        self.output_dir.mkdir(exist_ok=True)
    
    def setup_clients(self):
        """Initialisiert die AI-Clients basierend auf verfügbaren API Keys"""
        # OpenAI Client
        if self.key_checker.can_generate_chapters():
            openai.api_key = self.key_checker.openai_key
            self.openai_client = openai
            logger.info("OpenAI Client initialisiert")
        else:
            logger.warning("OpenAI Client nicht verfügbar - Kapitelgenerierung nicht möglich")
        
        # Claude Client
        if self.key_checker.can_optimize_prompts():
            try:
                # Verwende nur die notwendigen Parameter für die neueste Anthropic Version
                self.claude_client = anthropic.Anthropic(api_key=self.key_checker.claude_key)
                logger.info("Claude Client initialisiert")
            except Exception as e:
                logger.error(f"Fehler bei Claude Client Initialisierung: {e}")
                # Fallback: Versuche es ohne zusätzliche Parameter
                try:
                    self.claude_client = anthropic.Anthropic()
                    self.claude_client.api_key = self.key_checker.claude_key
                    logger.info("Claude Client erfolgreich initialisiert (Fallback)")
                except Exception as e2:
                    logger.error(f"Claude Client Fallback fehlgeschlagen: {e2}")
                    self.claude_client = None
        else:
            logger.warning("Claude Client nicht verfügbar - Prompt-Optimierung nicht möglich")
    
    def load_prompt_frame(self, json_file: Optional[Path] = None) -> Dict:
        """Lädt und validiert das JSON-PromptFrame"""
        if json_file is None:
            json_file = self.default_json_file
        
        try:
            logger.info(f"Lade PromptFrame aus: {json_file}")
            
            if not json_file.exists():
                raise FileNotFoundError(f"JSON-Datei nicht gefunden: {json_file}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                prompt_frame = json.load(f)
            
            logger.info("PromptFrame erfolgreich geladen")
            return prompt_frame
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON-Parsing Fehler: {e}")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Laden des PromptFrames: {e}")
            raise
    
    def validate_prompt_frame(self, prompt_frame: Dict) -> bool:
        """Validiert das PromptFrame gegen das Schema"""
        try:
            logger.info("Validiere PromptFrame gegen Schema")
            
            if not self.schema_file.exists():
                logger.warning("Schema-Datei nicht gefunden - Überspringe Validierung")
                return True
            
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            is_valid = validate_json_schema(prompt_frame, str(self.schema_file))
            
            if is_valid:
                logger.info("PromptFrame-Validierung erfolgreich")
            else:
                logger.error("PromptFrame-Validierung fehlgeschlagen")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Fehler bei der Schema-Validierung: {e}")
            return False
    
    def compile_prompt(self, prompt_frame: Dict, optimize_with_claude: bool = False) -> str:
        """Kompiliert den Prompt (optional mit Claude-Optimierung)"""
        try:
            logger.info("Kompiliere Prompt")
            
            # Basis-Prompt kompilieren
            base_prompt = compile_prompt_for_chatgpt(prompt_frame)
            logger.info("Basis-Prompt erfolgreich kompiliert")
            
            # Optional: Claude-Optimierung
            if optimize_with_claude and self.claude_client:
                logger.info("Optimiere Prompt mit Claude")
                optimized_prompt = self.optimize_prompt_with_claude(base_prompt, prompt_frame)
                if optimized_prompt:
                    logger.info("Prompt-Optimierung erfolgreich")
                    return optimized_prompt
                else:
                    logger.warning("Prompt-Optimierung fehlgeschlagen - verwende Basis-Prompt")
            
            return base_prompt
            
        except Exception as e:
            logger.error(f"Fehler beim Prompt-Kompilieren: {e}")
            raise
    
    def optimize_prompt_with_claude(self, base_prompt: str, prompt_frame: Dict) -> Optional[str]:
        """Optimiert den Prompt mit Claude"""
        try:
            # Extrahiere relevante Informationen für die Optimierung
            chapter_info = prompt_frame.get('input', {}).get('chapter', {})
            book_info = prompt_frame.get('input', {}).get('book', {})
            
            optimization_prompt = f"""
Du bist ein erfahrener Prompt-Engineer für Buchgenerierung. Optimiere den folgenden Prompt für bessere Kapitelgenerierung.

KONTEKT:
- Buch: {book_info.get('title', 'Unbekannt')} ({book_info.get('genre', 'Unbekannt')})
- Kapitel: {chapter_info.get('title', 'Unbekannt')} (Nr. {chapter_info.get('number', '?')})
- Zweck: {chapter_info.get('narrative_purpose', 'Unbekannt')}

AKTUELLER PROMPT:
{base_prompt}

AUFGABE:
Optimiere diesen Prompt für:
1. Klarere Anweisungen
2. Bessere Struktur
3. Spezifischere Details
4. Emotionale Tiefe
5. Konsistente Stilführung

Gib nur den optimierten Prompt zurück, ohne zusätzliche Erklärungen.
"""
            
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": optimization_prompt}]
            )
            
            optimized_prompt = response.content[0].text.strip()
            return optimized_prompt
            
        except Exception as e:
            logger.error(f"Fehler bei Claude-Prompt-Optimierung: {e}")
            return None
    
    def generate_chapter(self, prompt: str) -> str:
        """Generiert Kapiteltext mit ChatGPT"""
        if not self.openai_client:
            raise RuntimeError("OpenAI Client nicht verfügbar")
        
        try:
            logger.info("Generiere Kapitel mit ChatGPT")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Autor, der fesselnde Kapitel schreibt."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            chapter_text = response.choices[0].message.content.strip()
            logger.info("Kapitel erfolgreich generiert")
            
            return chapter_text
            
        except Exception as e:
            logger.error(f"Fehler bei der Kapitelgenerierung: {e}")
            raise
    
    def save_output(self, chapter_text: str, metadata: Dict = None) -> Path:
        """Speichert das generierte Kapitel"""
        try:
            logger.info(f"Speichere Ausgabe in: {self.output_file}")
            
            # Kapiteltext speichern
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(chapter_text)
            
            # Metadaten speichern (optional)
            if metadata:
                metadata_file = self.output_file.with_suffix('.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                logger.info(f"Metadaten gespeichert in: {metadata_file}")
            
            logger.info("Ausgabe erfolgreich gespeichert")
            return self.output_file
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Ausgabe: {e}")
            raise
    
    def run_pipeline(self, 
                    json_file: Optional[Path] = None,
                    optimize_prompt: bool = False,
                    output_file: Optional[Path] = None) -> Dict:
        """Führt die vollständige Pipeline aus"""
        
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("🚀 Starte One Click Book Writer Pipeline")
        logger.info("=" * 60)
        
        # Status-Check
        self.key_checker.print_status()
        
        try:
            # 1. PromptFrame laden
            logger.info("📥 Schritt 1: Lade PromptFrame")
            prompt_frame = self.load_prompt_frame(json_file)
            
            # 2. Validierung
            logger.info("✅ Schritt 2: Validiere PromptFrame")
            if not self.validate_prompt_frame(prompt_frame):
                raise ValueError("PromptFrame-Validierung fehlgeschlagen")
            
            # 3. Prompt kompilieren
            logger.info("🔧 Schritt 3: Kompiliere Prompt")
            prompt = self.compile_prompt(prompt_frame, optimize_prompt)
            
            # 4. Kapitel generieren
            logger.info("✍️  Schritt 4: Generiere Kapitel")
            chapter_text = self.generate_chapter(prompt)
            
            # 5. Ausgabe speichern
            logger.info("💾 Schritt 5: Speichere Ausgabe")
            if output_file:
                self.output_file = output_file
            
            metadata = {
                'generated_at': start_time.isoformat(),
                'pipeline_version': '1.0.0',
                'optimization_used': optimize_prompt,
                'chapter_info': prompt_frame.get('input', {}).get('chapter', {}),
                'book_info': prompt_frame.get('input', {}).get('book', {}),
                'word_count': len(chapter_text.split())
            }
            
            saved_file = self.save_output(chapter_text, metadata)
            
            # Erfolgsbericht
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                'success': True,
                'output_file': str(saved_file),
                'chapter_text': chapter_text,
                'metadata': metadata,
                'duration_seconds': duration,
                'word_count': metadata['word_count']
            }
            
            logger.info("=" * 60)
            logger.info("🎉 Pipeline erfolgreich abgeschlossen!")
            logger.info(f"⏱️  Dauer: {duration:.2f} Sekunden")
            logger.info(f"📝 Wörter: {metadata['word_count']}")
            logger.info(f"💾 Ausgabe: {saved_file}")
            logger.info("=" * 60)
            
            return result
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ Pipeline fehlgeschlagen: {e}")
            logger.error("=" * 60)
            
            return {
                'success': False,
                'error': str(e),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }

def main():
    """Hauptfunktion für Kommandozeilen-Ausführung"""
    import argparse
    
    parser = argparse.ArgumentParser(description="One Click Book Writer Pipeline")
    parser.add_argument('--json-file', type=Path, help='JSON-PromptFrame Datei')
    parser.add_argument('--optimize', action='store_true', help='Prompt mit Claude optimieren')
    parser.add_argument('--output', type=Path, help='Ausgabedatei')
    parser.add_argument('--verbose', action='store_true', help='Detaillierte Ausgabe')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Pipeline ausführen
    pipeline = OneClickBookWriterPipeline()
    result = pipeline.run_pipeline(
        json_file=args.json_file,
        optimize_prompt=args.optimize,
        output_file=args.output
    )
    
    if result['success']:
        print(f"\n✅ Erfolgreich! Kapitel generiert: {result['output_file']}")
        print(f"📊 Wörter: {result['word_count']}")
        print(f"⏱️  Dauer: {result['duration_seconds']:.2f}s")
    else:
        print(f"\n❌ Fehler: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 