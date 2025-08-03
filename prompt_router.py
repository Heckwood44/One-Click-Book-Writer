#!/usr/bin/env python3
"""
One Click Book Writer - Prompt Router & Orchestrator
Version: 2.0.0
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

# Import our modules
from compiler.prompt_compiler import (
    compile_prompt_for_chatgpt,
    validate_prompt_structure,
)
from schema.validate_input import validate_json_schema
from engine.openai_adapter import OpenAIAdapter
from engine.claude_adapter import ClaudeAdapter
from utils.prompt_versioning import PromptVersioning
from utils.token_logging import TokenLogger
from utils.user_feedback import UserFeedback
from utils.quality_evaluator import QualityEvaluator

logger = logging.getLogger(__name__)


class PromptRouter:
    """Haupt-Orchestrator für die Kapitelgenerierung"""

    def __init__(self):
        self.openai_client = OpenAIAdapter()
        self.claude_client = ClaudeAdapter()
        self.prompt_versioning = PromptVersioning()
        self.token_logger = TokenLogger()
        self.user_feedback = UserFeedback()
        self.quality_evaluator = QualityEvaluator()

        # Output-Verzeichnis
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def load_and_validate_prompt_frame(
        self, prompt_frame_path: str
    ) -> Tuple[bool, Dict, str]:
        """Lädt und validiert das PromptFrame"""
        try:
            # Lade JSON
            with open(prompt_frame_path, "r", encoding="utf-8") as f:
                prompt_frame = json.load(f)

            # Schema-Validierung
            schema_file = "schema/prompt_frame.schema.json"
            is_valid, message = validate_json_schema(prompt_frame, schema_file)

            if not is_valid:
                return False, {}, f"Schema-Validierung fehlgeschlagen: {message}"

            # Struktur-Validierung
            if not validate_prompt_structure(prompt_frame):
                return False, {}, "Prompt-Struktur ist ungültig"

            return True, prompt_frame, "Validierung erfolgreich"

        except Exception as e:
            return False, {}, f"Fehler beim Laden: {e}"

    def optimize_prompt_with_claude(
        self, raw_prompt: str, prompt_frame: Dict
    ) -> Tuple[bool, str, str]:
        """Optimiert den Prompt mit Claude (optional)"""
        try:
            if not self.claude_client.is_available():
                logger.warning("Claude nicht verfügbar - überspringe Optimierung")
                return False, raw_prompt, "Claude nicht verfügbar"

            optimization_prompt = f"""
Du bist ein Experte für Prompt-Optimierung. Optimiere den folgenden Prompt für bessere Kapitelgenerierung:

ORIGINAL PROMPT:
{raw_prompt}

OPTIMIERUNGSZIELE:
- Klarere Anweisungen
- Bessere Struktur
- Kulturelle Anpassung für bilinguale Inhalte
- Emotionale Tiefe
- Konsistente Charakterentwicklung

OPTIMIERTER PROMPT:
"""

            optimized_prompt = self.claude_client.generate_text(optimization_prompt)

            if optimized_prompt and len(optimized_prompt) > 100:
                logger.info("Prompt erfolgreich mit Claude optimiert")
                return True, optimized_prompt, "Optimierung erfolgreich"
            else:
                logger.warning("Claude-Optimierung fehlgeschlagen - verwende Original")
                return False, raw_prompt, "Optimierung fehlgeschlagen"

        except Exception as e:
            logger.error(f"Fehler bei Claude-Optimierung: {e}")
            return False, raw_prompt, f"Optimierungsfehler: {e}"

    def generate_chapter_with_gpt(
        self, prompt: str, prompt_frame: Dict
    ) -> Tuple[bool, str, str]:
        """Generiert das Kapitel mit GPT-4"""
        try:
            if not self.openai_client.is_available():
                return False, "", "OpenAI nicht verfügbar"

            # Token-Logging vor API-Call
            estimated_tokens = self.token_logger.count_tokens(prompt)
            self.token_logger.log_api_call(
                "openai", "gpt-4", estimated_tokens, "chapter_generation"
            )

            # API-Call
            chapter_text = self.openai_client.generate_text(prompt)

            if chapter_text and len(chapter_text) > 30:
                logger.info("Kapitel erfolgreich mit GPT-4 generiert")
                return True, chapter_text, "Generierung erfolgreich"
            else:
                return False, "", "Generierung fehlgeschlagen - zu kurzer Text"

        except Exception as e:
            logger.error(f"Fehler bei GPT-Generierung: {e}")
            return False, "", f"Generierungsfehler: {e}"

    def parse_bilingual_response(self, response: str) -> Tuple[str, str]:
        """Parst bilinguale Antwort in deutsche und englische Versionen"""
        try:
            # Suche nach "---" Trenner
            parts = response.split("---")

            if len(parts) >= 2:
                german_part = parts[0].strip()
                english_part = parts[1].strip()

                # Entferne Markdown-Header und Labels falls vorhanden
                german_part = re.sub(
                    r"^#.*?\n", "", german_part, flags=re.MULTILINE
                ).strip()
                german_part = re.sub(
                    r"^DEUTSCH:\s*", "", german_part, flags=re.MULTILINE
                ).strip()
                english_part = re.sub(
                    r"^#.*?\n", "", english_part, flags=re.MULTILINE
                ).strip()
                english_part = re.sub(
                    r"^ENGLISH:\s*", "", english_part, flags=re.MULTILINE
                ).strip()

                # Prüfe ob die Teile tatsächlich Inhalt haben
                if len(german_part.split()) < 50:
                    logger.warning("Deutsche Version zu kurz, verwende Fallback")
                    german_part = response

                if len(english_part.split()) < 50:
                    logger.warning("Englische Version zu kurz, verwende Fallback")
                    english_part = response

                return german_part, english_part
            else:
                # Fallback: Verwende die gesamte Antwort für beide Sprachen
                logger.warning("Keine bilinguale Trennung gefunden, verwende Fallback")
                return response, response

        except Exception as e:
            logger.error(f"Fehler beim Parsen der bilingualen Antwort: {e}")
            return response, response

    def retry_with_extended_prompt(self, prompt: str, target_words: int = 800) -> str:
        """Erweitert den Prompt für bessere Wortanzahl"""
        extension_instruction = f"""

WICHTIGE ERGÄNZUNG:
- Erweitere die Geschichte so, dass sie mindestens {target_words} Wörter umfasst
- Behalte dabei den Stil, die Emotionen und die Charakterentwicklung bei
- Füge mehr Details, Dialoge und Beschreibungen hinzu
- Stelle sicher, dass die Geschichte vollständig erzählt wird (Anfang, Mitte, Ende)
- Verwende warme, bildhafte Sprache für Kinder

Ziel: Eine vollständige, fesselnde Geschichte mit mindestens {target_words} Wörtern."""

        return prompt + extension_instruction

    def save_output_files(
        self,
        german_text: str,
        english_text: str,
        prompt_frame: Dict,
        chapter_number: int,
    ) -> Dict:
        """Speichert die Ausgabedateien"""
        try:
            book_title = (
                prompt_frame.get("input", {}).get("book", {}).get("title", "Unknown")
            )
            chapter_title = (
                prompt_frame.get("input", {}).get("chapter", {}).get("title", "Unknown")
            )

            # Dateinamen erstellen
            base_filename = f"chapter_{chapter_number}"
            german_file = self.output_dir / f"{base_filename}_de.txt"
            english_file = self.output_dir / f"{base_filename}_en.txt"
            bilingual_file = self.output_dir / f"{base_filename}_bilingual.txt"
            meta_file = self.output_dir / f"{base_filename}_meta.json"

            # Deutsche Version speichern
            with open(german_file, "w", encoding="utf-8") as f:
                f.write(f"# {chapter_title}\n\n")
                f.write(german_text)

            # Englische Version speichern
            with open(english_file, "w", encoding="utf-8") as f:
                f.write(f"# {chapter_title}\n\n")
                f.write(english_text)

            # Bilinguale Version speichern
            with open(bilingual_file, "w", encoding="utf-8") as f:
                f.write(f"# {chapter_title} (Deutsch)\n\n")
                f.write(german_text)
                f.write("\n\n---\n\n")
                f.write(f"# {chapter_title} (English)\n\n")
                f.write(english_text)

            # Metadaten erstellen
            metadata = {
                "generation_timestamp": datetime.now().isoformat(),
                "book_title": book_title,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "word_counts": {
                    "german": len(german_text.split()),
                    "english": len(english_text.split()),
                },
                "file_paths": {
                    "german": str(german_file),
                    "english": str(english_file),
                    "bilingual": str(bilingual_file),
                    "metadata": str(meta_file),
                },
                "prompt_versioning": {},
                "token_usage": self.token_logger.get_usage_summary(),
            }

            # Metadaten speichern
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Ausgabedateien gespeichert: {base_filename}")
            return metadata

        except Exception as e:
            logger.error(f"Fehler beim Speichern der Ausgabedateien: {e}")
            return {}

    def run_full_pipeline(
        self,
        prompt_frame_path: str,
        optimize_with_claude: bool = True,
        chapter_number: int = 1,
    ) -> Dict:
        """Führt die komplette Pipeline aus"""
        logger.info(f"Starte Pipeline für Kapitel {chapter_number}")

        result = {
            "success": False,
            "chapter_number": chapter_number,
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "output_files": {},
            "errors": [],
        }

        try:
            # Schritt 1: PromptFrame laden und validieren
            logger.info("Schritt 1: Lade und validiere PromptFrame")
            is_valid, prompt_frame, message = self.load_and_validate_prompt_frame(
                prompt_frame_path
            )

            if not is_valid:
                result["errors"].append(f"Validierung fehlgeschlagen: {message}")
                return result

            result["steps"]["validation"] = {"success": True, "message": message}

            # Schritt 2: Prompt kompilieren
            logger.info("Schritt 2: Kompiliere Prompt")
            raw_prompt = compile_prompt_for_chatgpt(prompt_frame)

            # Prompt-Versionierung
            raw_hash = self.prompt_versioning.add_version(
                prompt_frame, raw_prompt, chapter_number=chapter_number
            )

            result["steps"]["compilation"] = {
                "success": True,
                "prompt_length": len(raw_prompt),
                "raw_hash": raw_hash,
            }

            # Schritt 3: Optional Claude-Optimierung
            optimized_prompt = raw_prompt
            optimization_success = False

            if optimize_with_claude:
                logger.info("Schritt 3: Claude-Optimierung")
                (
                    optimization_success,
                    optimized_prompt,
                    opt_message,
                ) = self.optimize_prompt_with_claude(raw_prompt, prompt_frame)

                if optimization_success:
                    opt_hash = self.prompt_versioning.add_version(
                        prompt_frame, raw_prompt, optimized_prompt, chapter_number
                    )
                    result["steps"]["optimization"] = {
                        "success": True,
                        "optimized_hash": opt_hash,
                        "message": opt_message,
                    }
                else:
                    result["steps"]["optimization"] = {
                        "success": False,
                        "message": opt_message,
                    }

            # Schritt 4: GPT-Generierung
            logger.info("Schritt 4: GPT-Generierung")
            (
                generation_success,
                chapter_text,
                gen_message,
            ) = self.generate_chapter_with_gpt(optimized_prompt, prompt_frame)

            if not generation_success:
                result["errors"].append(f"Generierung fehlgeschlagen: {gen_message}")
                return result

            result["steps"]["generation"] = {
                "success": True,
                "text_length": len(chapter_text),
                "message": gen_message,
            }

            # Schritt 5: Bilinguale Antwort parsen
            logger.info("Schritt 5: Parse bilinguale Antwort")
            german_text, english_text = self.parse_bilingual_response(chapter_text)

            result["steps"]["parsing"] = {
                "success": True,
                "german_length": len(german_text),
                "english_length": len(english_text),
            }

            # Schritt 6: Qualitätsbewertung
            logger.info("Schritt 6: Qualitätsbewertung")
            quality_evaluation = self.quality_evaluator.evaluate_bilingual_content(
                german_text, english_text, prompt_frame
            )

            # Canvas-Compliance prüfen
            canvas_compliance = self._check_canvas_compliance(
                raw_prompt, optimized_prompt
            )

            result["steps"]["quality_evaluation"] = {
                "success": True,
                "overall_score": quality_evaluation["overall_bilingual_score"],
                "german_score": quality_evaluation["german_evaluation"][
                    "overall_score"
                ],
                "english_score": quality_evaluation["english_evaluation"][
                    "overall_score"
                ],
                "consistency_score": quality_evaluation["consistency_score"],
                "canvas_compliance": canvas_compliance,
            }

            # Schritt 7: Dateien speichern
            logger.info("Schritt 7: Speichere Ausgabedateien")
            metadata = self.save_output_files(
                german_text, english_text, prompt_frame, chapter_number
            )

            # Qualitätsbewertung zu Metadaten hinzufügen
            metadata["quality_evaluation"] = quality_evaluation

            # Review-Flags hinzufügen
            if quality_evaluation["overall_bilingual_score"] < 0.7:
                metadata["review_required"] = True
                metadata[
                    "review_reason"
                ] = f"Qualitäts-Score {quality_evaluation['overall_bilingual_score']} unter Schwellenwert 0.7"
                logger.warning(
                    f"⚠️ Review erforderlich: Score {quality_evaluation['overall_bilingual_score']} < 0.7"
                )

            if quality_evaluation["overall_bilingual_score"] < 0.5:
                metadata["critical_issues"] = True
                metadata[
                    "critical_reason"
                ] = f"Kritische Qualitätsprobleme: Score {quality_evaluation['overall_bilingual_score']} < 0.5"
                logger.error(
                    f"🚨 Kritische Probleme: Score {quality_evaluation['overall_bilingual_score']} < 0.5"
                )

            # Prompt-Versionierung in Metadaten exportieren
            self.prompt_versioning.export_metadata_for_chapter(
                chapter_number, f"output/chapter_{chapter_number}_meta.json"
            )

            # Qualitätsbewertung, Canvas-Compliance und Review-Flags zu Metadaten hinzufügen
            meta_file = f"output/chapter_{chapter_number}_meta.json"
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    existing_metadata = json.load(f)

                # Qualitätsbewertung hinzufügen
                existing_metadata["quality_evaluation"] = quality_evaluation

                # Canvas-Compliance hinzufügen
                existing_metadata["canvas_compliance"] = canvas_compliance

                # Review-Flags hinzufügen
                if quality_evaluation["overall_bilingual_score"] < 0.7:
                    existing_metadata["review_required"] = True
                    existing_metadata[
                        "review_reason"
                    ] = f"Qualitäts-Score {quality_evaluation['overall_bilingual_score']} unter Schwellenwert 0.7"

                if quality_evaluation["overall_bilingual_score"] < 0.5:
                    existing_metadata["critical_issues"] = True
                    existing_metadata[
                        "critical_reason"
                    ] = f"Kritische Qualitätsprobleme: Score {quality_evaluation['overall_bilingual_score']} < 0.5"

                # Prompt-Diff hinzufügen (falls vorhanden)
                if optimization_success:
                    prompt_diff = self._calculate_prompt_diff(
                        raw_prompt, optimized_prompt
                    )
                    existing_metadata["prompt_diff"] = prompt_diff

                # Aktualisierte Metadaten speichern
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(existing_metadata, f, indent=2, ensure_ascii=False)

                logger.info(
                    f"Qualitätsbewertung und Canvas-Compliance zu Metadaten hinzugefügt: {meta_file}"
                )

            except Exception as e:
                logger.error(f"Fehler beim Hinzufügen der Qualitätsbewertung: {e}")

            result["output_files"] = metadata.get("file_paths", {})
            result["quality_evaluation"] = quality_evaluation
            result["success"] = True

            logger.info(
                f"Pipeline erfolgreich abgeschlossen für Kapitel {chapter_number}"
            )
            logger.info(
                f"Qualitäts-Score: {quality_evaluation['overall_bilingual_score']}"
            )

        except Exception as e:
            logger.error(f"Pipeline-Fehler: {e}")
            result["errors"].append(f"Pipeline-Fehler: {e}")

        return result

    def _check_canvas_compliance(self, raw_prompt: str, optimized_prompt: str) -> Dict:
        """Prüft Canvas-Compliance der Prompts"""
        try:
            system_note_signature = "SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"

            raw_compliance = "missing"
            if system_note_signature in raw_prompt:
                raw_compliance = "full"
            elif "Ein Weltklasse-Autor ist kein" in raw_prompt:
                raw_compliance = "partial"

            opt_compliance = "missing"
            if system_note_signature in optimized_prompt:
                opt_compliance = "full"
            elif "Ein Weltklasse-Autor ist kein" in optimized_prompt:
                opt_compliance = "partial"

            return {
                "raw_prompt_compliance": raw_compliance,
                "optimized_prompt_compliance": opt_compliance,
                "overall_compliance": "full"
                if raw_compliance == "full" or opt_compliance == "full"
                else "partial",
            }

        except Exception as e:
            logger.error(f"Fehler bei Canvas-Compliance-Prüfung: {e}")
            return {
                "raw_prompt_compliance": "error",
                "optimized_prompt_compliance": "error",
                "overall_compliance": "error",
            }

    def _calculate_prompt_diff(self, raw_prompt: str, optimized_prompt: str) -> Dict:
        """Berechnet Diff zwischen rohem und optimiertem Prompt"""
        try:
            import difflib

            raw_lines = raw_prompt.split("\n")
            opt_lines = optimized_prompt.split("\n")

            diff = list(
                difflib.unified_diff(
                    raw_lines,
                    opt_lines,
                    fromfile="raw_prompt",
                    tofile="optimized_prompt",
                    lineterm="",
                )
            )

            return {
                "diff_lines": diff,
                "raw_length": len(raw_prompt),
                "optimized_length": len(optimized_prompt),
                "length_change": len(optimized_prompt) - len(raw_prompt),
                "diff_summary": f"Längenänderung: {len(optimized_prompt) - len(raw_prompt)} Zeichen",
            }

        except Exception as e:
            logger.error(f"Fehler bei Prompt-Diff-Berechnung: {e}")
            return {"error": str(e)}

    def _save_prompt_diff(self, prompt_diff: Dict, chapter_number: int):
        """Speichert Prompt-Diff in Datei"""
        try:
            diff_file = f"output/chapter_{chapter_number}_prompt_diff.json"
            with open(diff_file, "w", encoding="utf-8") as f:
                json.dump(prompt_diff, f, indent=2, ensure_ascii=False)
            logger.info(f"Prompt-Diff gespeichert: {diff_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Prompt-Diffs: {e}")


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung"""
    import argparse

    parser = argparse.ArgumentParser(
        description="One Click Book Writer - Prompt Router"
    )
    parser.add_argument("prompt_frame", help="Pfad zur PromptFrame JSON-Datei")
    parser.add_argument("--chapter", type=int, default=1, help="Kapitelnummer")
    parser.add_argument(
        "--no-optimize", action="store_true", help="Claude-Optimierung überspringen"
    )
    parser.add_argument("--output-dir", default="output", help="Ausgabeverzeichnis")

    args = parser.parse_args()

    # Router initialisieren
    router = PromptRouter()

    # Pipeline ausführen
    result = router.run_full_pipeline(
        args.prompt_frame,
        optimize_with_claude=not args.no_optimize,
        chapter_number=args.chapter,
    )

    # Ergebnis ausgeben
    if result["success"]:
        print(f"✅ Pipeline erfolgreich für Kapitel {args.chapter}")
        print(f"📁 Ausgabedateien: {result['output_files']}")
        print(
            f"🎯 Qualitäts-Score: {result['quality_evaluation']['overall_bilingual_score']}"
        )
    else:
        print(f"❌ Pipeline fehlgeschlagen für Kapitel {args.chapter}")
        for error in result["errors"]:
            print(f"   Fehler: {error}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
