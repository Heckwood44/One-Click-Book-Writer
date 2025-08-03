#!/usr/bin/env python3
"""
One Click Book Writer - Batch Generation
Generiert mehrere Kapitel in einem Durchgang
"""

import json
import os
import sys
import argparse
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from compiler.prompt_compiler import (
    compile_prompt,
    compile_prompt_for_chatgpt,
    get_prompt_metadata,
)
from schema.validate_input import validate_json_schema, validate_prompt_frame_structure


class BatchGenerator:
    """Batch-Generator für mehrere Kapitel."""

    def __init__(self, base_prompt_frame: Dict[str, Any]) -> None:
        """
        Initialisiert den Batch-Generator.

        Args:
            base_prompt_frame: Basis-PromptFrame für alle Kapitel
        """
        self.base_prompt_frame: Dict[str, Any] = base_prompt_frame
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

    def generate_chapters(
        self,
        start_chapter: int,
        count: int,
        engine: str = "claude",
        temperature: float = 0.4,
        max_tokens: int = 8000,
        max_workers: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Generiert mehrere Kapitel.

        Args:
            start_chapter: Start-Kapitelnummer
            count: Anzahl der Kapitel
            engine: AI-Engine (claude/chatgpt)
            temperature: Temperature für die Generierung
            max_tokens: Maximale Anzahl Tokens
            max_workers: Maximale Anzahl paralleler Threads

        Returns:
            Liste der Generierungsergebnisse
        """
        logger.info(
            f"🚀 Starte Batch-Generierung: {count} Kapitel ab Kapitel {start_chapter}"
        )
        logger.info(
            f"🤖 Engine: {engine}, Temperature: {temperature}, Max Tokens: {max_tokens}"
        )
        logger.info(f"⚡ Parallele Threads: {max_workers}")
        logger.info("-" * 60)

        # Kapitel-Liste erstellen
        chapters = []
        for i in range(count):
            chapter_num = start_chapter + i
            prompt_frame = self._create_chapter_prompt_frame(chapter_num)
            chapters.append(
                {
                    "chapter_num": chapter_num,
                    "prompt_frame": prompt_frame,
                    "engine": engine,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )

        # Parallele Generierung
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Futures erstellen
            future_to_chapter = {
                executor.submit(self._generate_single_chapter, chapter): chapter
                for chapter in chapters
            }

            # Ergebnisse sammeln
            for future in as_completed(future_to_chapter):
                chapter = future_to_chapter[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"✅ Kapitel {chapter['chapter_num']} generiert")
                except (ValueError, AttributeError, KeyError) as e:
                    error_msg = f"Fehler bei Kapitel {chapter['chapter_num']} (Daten/Attribut): {e}"
                    logger.error(f"❌ {error_msg}")
                    self.errors.append(
                        {
                            "chapter_num": chapter["chapter_num"],
                            "error": f"Datenfehler: {str(e)}",
                        }
                    )
                except Exception as e:
                    error_msg = (
                        f"Unerwarteter Fehler bei Kapitel {chapter['chapter_num']}: {e}"
                    )
                    logger.exception(f"❌ {error_msg}")
                    self.errors.append(
                        {
                            "chapter_num": chapter["chapter_num"],
                            "error": f"Unerwarteter Fehler: {str(e)}",
                        }
                    )

        # Ergebnisse sortieren
        results.sort(key=lambda x: x["chapter_num"])

        # Zusammenfassung
        logger.info("-" * 60)
        logger.info(f"🎉 Batch-Generierung abgeschlossen!")
        logger.info(f"✅ Erfolgreich: {len(results)} Kapitel")
        logger.info(f"❌ Fehler: {len(self.errors)} Kapitel")

        if self.errors:
            logger.error("\nFehler-Details:")
            for error in self.errors:
                logger.error(f"  Kapitel {error['chapter_num']}: {error['error']}")

        return results

    def _create_chapter_prompt_frame(self, chapter_num: int) -> Dict[str, Any]:
        """
        Erstellt ein PromptFrame für ein spezifisches Kapitel.

        Args:
            chapter_num: Kapitelnummer

        Returns:
            PromptFrame für das Kapitel
        """
        # Basis-PromptFrame kopieren
        prompt_frame = json.loads(json.dumps(self.base_prompt_frame))

        # Kapitel-Nummer anpassen
        prompt_frame["input"]["chapter"]["number"] = chapter_num

        # Kapitel-Titel anpassen (falls vorhanden)
        if "title" in prompt_frame["input"]["chapter"]:
            base_title = prompt_frame["input"]["chapter"]["title"]
            prompt_frame["input"]["chapter"][
                "title"
            ] = f"Kapitel {chapter_num}: {base_title}"

        # Story-Kontext anpassen (falls vorhanden)
        if "story_context" in prompt_frame["input"]:
            story_context = prompt_frame["input"]["story_context"]
            if "current_scene" in story_context:
                # Aktuelle Szene für das neue Kapitel anpassen
                story_context[
                    "current_scene"
                ] = f"Kapitel {chapter_num} beginnt mit einer neuen Entwicklung in der Geschichte."

            if "previous_summary" in story_context:
                # Vorherige Zusammenfassung anpassen
                story_context[
                    "previous_summary"
                ] = f"Nach den Ereignissen von Kapitel {chapter_num - 1} entwickelt sich die Geschichte weiter."

        return prompt_frame

    def _generate_single_chapter(self, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiert ein einzelnes Kapitel.

        Args:
            chapter_data: Kapitel-Daten

        Returns:
            Generierungsergebnis
        """
        chapter_num = chapter_data["chapter_num"]
        prompt_frame = chapter_data["prompt_frame"]
        engine = chapter_data["engine"]
        temperature = chapter_data["temperature"]
        max_tokens = chapter_data["max_tokens"]

        try:
            # Prompt kompilieren
            if engine == "chatgpt":
                prompt = compile_prompt_for_chatgpt(prompt_frame)
            else:
                prompt = compile_prompt(prompt_frame)

            # Metadaten extrahieren
            metadata = get_prompt_metadata(prompt_frame)

            # Simulierte Generierung (ohne API-Keys)
            simulated_text = self._generate_simulated_text(
                chapter_num, metadata, engine
            )

            # Ergebnis speichern
            output_path = self._save_chapter_result(
                simulated_text, metadata, engine, chapter_num
            )

            return {
                "chapter_num": chapter_num,
                "success": True,
                "output_path": output_path,
                "text_length": len(simulated_text),
                "engine": engine,
                "metadata": metadata,
            }

        except Exception as e:
            return {"chapter_num": chapter_num, "success": False, "error": str(e)}

    def _generate_simulated_text(
        self, chapter_num: int, metadata: Dict[str, Any], engine: str
    ) -> str:
        """
        Generiert simulierten Text für ein Kapitel.

        Args:
            chapter_num: Kapitelnummer
            metadata: Kapitel-Metadaten
            engine: Verwendete Engine

        Returns:
            Simulierter Text
        """
        genre = metadata.get("genre", "Allgemein")
        title = metadata.get("chapter_title", f"Kapitel {chapter_num}")

        if genre == "Kriminalroman":
            return f"""Kapitel {chapter_num}: {title}

Kommissar Weber betrat das luxuriöse Büro mit der Gewissheit, dass hier etwas nicht stimmte. Die Luft schien zu vibrieren vor Spannung, als er sich dem Schreibtisch näherte, hinter dem der tote Geschäftsmann saß.

"Dr. Schmidt, was können Sie mir sagen?" fragte Weber, während er die Szene aufmerksam musterte.

Der Gerichtsmediziner schüttelte den Kopf. "Keine äußeren Verletzungen, keine Anzeichen eines Kampfes. Es ist, als wäre er einfach... eingeschlafen."

Weber spürte, wie sich sein Detektiv-Instinkt meldete. Etwas an diesem Fall war anders. Etwas, das ihn an seinen traumatischen Fall in der Großstadt erinnerte.

"Frau Müller", wandte er sich an die nervöse Sekretärin, "wann haben Sie ihn zuletzt lebend gesehen?"

Die junge Frau zitterte leicht. "Gestern Abend, kurz vor Feierabend. Er schien... besorgt."

Weber notierte sich das. Besorgt. Das war ein Anfang. Er wusste, dass dieser Fall ihn fordern würde, aber er war bereit. Bereit, die Wahrheit zu finden, egal wohin sie führte.

Die Schatten der Vergangenheit schienen sich in diesem Büro zu sammeln, und Weber spürte, dass die Jagd gerade erst begonnen hatte."""

        elif genre == "Science Fiction":
            return f"""Kapitel {chapter_num}: {title}

Dr. Sarah Chen atmete tief ein, als sie sich dem mysteriösen Objekt näherte. Die Mars-Landschaft um sie herum war still, nur das leise Summen ihrer Raumanzug-Lebenserhaltungssysteme durchbrach die Stille.

Das Objekt schwebte etwa einen Meter über dem roten Sand, pulsierend in einem sanften, bläulichen Licht. Es reagierte auf ihre Anwesenheit, als sie sich näherte.

"Commander Rodriguez, Sie müssen das sehen", funkte sie zurück zur Station. "Es ist... es ist unglaublich."

"Dr. Chen, bleiben Sie vorsichtig", antwortete die Stimme des Commanders. "Dr. Kim ist bereits unterwegs zu Ihnen."

Sarah konnte ihre Aufregung kaum zügeln. Als Astrophysikerin hatte sie ihr Leben lang nach Zeichen außerirdischen Lebens gesucht, und jetzt stand sie direkt davor. Das Objekt schien sie zu studieren, zu analysieren.

"Es ist, als würde es mich verstehen", flüsterte sie, während sie ihre wissenschaftlichen Instrumente aktivierte. "Als würde es kommunizieren wollen."

Das Objekt pulsierte stärker, und plötzlich erschien ein holografisches Display in der Luft vor ihr. Symbole, die sie noch nie gesehen hatte, tanzten in der dünnen Mars-Atmosphäre.

Sarah wusste, dass ihr Leben sich für immer verändert hatte. Sie war Zeugin des ersten Kontakts der Menschheit mit einer außerirdischen Zivilisation."""

        else:
            return f"""Kapitel {chapter_num}: {title}

Dies ist ein simuliertes Kapitel {chapter_num} für die Batch-Generierung mit {engine}.

Die Geschichte entwickelt sich weiter und neue Elemente werden eingeführt. Die Charaktere wachsen und verändern sich, während die Handlung voranschreitet.

"Jedes Kapitel bringt neue Erkenntnisse", sagte eine Stimme in der Geschichte.

Die Protagonisten lernen aus ihren Erfahrungen und werden stärker. Die Herausforderungen werden größer, aber so auch ihre Fähigkeiten, sie zu meistern.

Am Ende des Kapitels steht eine neue Wendung, die die Leser neugierig auf das nächste Kapitel macht."""

    def _save_chapter_result(
        self, text: str, metadata: Dict[str, Any], engine: str, chapter_num: int
    ) -> str:
        """
        Speichert das Ergebnis eines Kapitels.

        Args:
            text: Generierter Text
            metadata: Kapitel-Metadaten
            engine: Verwendete Engine
            chapter_num: Kapitelnummer

        Returns:
            Pfad zur gespeicherten Datei
        """
        try:
            os.makedirs("output/chapters", exist_ok=True)

            # Text speichern
            output_filename = f"batch_chapter_{chapter_num:03d}.txt"
            output_path = f"output/chapters/{output_filename}"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            # Metadaten speichern
            metadata_filename = output_filename.replace(".txt", "_metadata.json")
            metadata_path = f"output/chapters/{metadata_filename}"

            result_metadata = {
                "text_length": len(text),
                "model": f"{engine}-simulated",
                "engine": engine,
                "chapter_number": chapter_num,
                "batch_generated": True,
                "usage": {
                    "input_tokens": 450,
                    "output_tokens": 320,
                    "total_tokens": 770,
                },
                "finish_reason": "stop",
                "prompt_metadata": metadata,
            }

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(result_metadata, f, indent=2, ensure_ascii=False)

            return output_path

        except Exception as e:
            raise Exception(f"Fehler beim Speichern von Kapitel {chapter_num}: {e}")

    def save_batch_summary(
        self, results: List[Dict[str, Any]], output_file: str = None
    ):
        """
        Speichert eine Zusammenfassung der Batch-Generierung.

        Args:
            results: Generierungsergebnisse
            output_file: Ausgabedatei (optional)
        """
        if not output_file:
            timestamp = int(time.time())
            output_file = f"output/batch_summary_{timestamp}.json"

        os.makedirs("output", exist_ok=True)

        summary = {
            "batch_info": {
                "total_chapters": len(results),
                "successful_chapters": len(
                    [r for r in results if r.get("success", False)]
                ),
                "failed_chapters": len(
                    [r for r in results if not r.get("success", False)]
                ),
                "errors": self.errors,
            },
            "chapters": results,
            "timestamp": time.time(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Batch-Zusammenfassung gespeichert: {output_file}")


def load_prompt_frame(file_path: str) -> Dict[str, Any]:
    """
    Lädt ein PromptFrame aus einer Datei.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        PromptFrame Dictionary
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validierung
        if not validate_prompt_frame_structure(data):
            raise ValueError("Ungültige PromptFrame-Struktur")

        if not validate_json_schema(data, "schema/prompt_frame.schema.json"):
            raise ValueError("PromptFrame entspricht nicht dem Schema")

        return data

    except Exception as e:
        raise Exception(f"Fehler beim Laden der Datei {file_path}: {e}")


def main():
    """Hauptfunktion für die Batch-Generierung."""
    parser = argparse.ArgumentParser(
        description="One Click Book Writer - Batch Generation"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Pfad zur JSON-Eingabedatei"
    )
    parser.add_argument(
        "--start", "-s", type=int, default=1, help="Start-Kapitelnummer"
    )
    parser.add_argument(
        "--count", "-c", type=int, required=True, help="Anzahl der Kapitel"
    )
    parser.add_argument(
        "--engine",
        "-e",
        choices=["claude", "chatgpt"],
        default="claude",
        help="AI-Engine",
    )
    parser.add_argument(
        "--temperature", "-t", type=float, default=0.4, help="Temperature"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=8000, help="Maximale Anzahl Tokens"
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=3, help="Anzahl paralleler Threads"
    )
    parser.add_argument("--output", "-o", help="Ausgabedatei für Zusammenfassung")

    args = parser.parse_args()

    try:
        # PromptFrame laden
        logger.info(f"📖 Lade PromptFrame aus {args.input}...")
        base_prompt_frame = load_prompt_frame(args.input)
        logger.info("✅ PromptFrame erfolgreich geladen und validiert")

        # Batch-Generator erstellen
        generator = BatchGenerator(base_prompt_frame)

        # Kapitel generieren
        results = generator.generate_chapters(
            start_chapter=args.start,
            count=args.count,
            engine=args.engine,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            max_workers=args.workers,
        )

        # Zusammenfassung speichern
        generator.save_batch_summary(results, args.output)

        logger.info(f"\n🎉 Batch-Generierung erfolgreich abgeschlossen!")
        logger.info(f"📁 Ergebnisse in: output/chapters/")

    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    main()
