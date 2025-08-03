#!/usr/bin/env python3
"""
Prompt Optimization A/B Test Script
Vergleicht rohe vs. Claude-optimierte Prompts und analysiert Qualitätsverbesserungen
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import difflib

# Import project modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from compiler.prompt_compiler import compile_prompt_for_chatgpt, generate_prompt_hash
from engine.claude_adapter import ClaudeAdapter
from engine.openai_adapter import OpenAIAdapter
from utils.quality_evaluator import QualityEvaluator
from prompt_router import PromptRouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptOptimizationABTest:
    """Führt A/B-Tests zwischen rohen und optimierten Prompts durch"""
    
    def __init__(self):
        self.claude_client = ClaudeAdapter()
        self.openai_client = OpenAIAdapter()
        self.quality_evaluator = QualityEvaluator()
        self.router = PromptRouter()
        
    def optimize_prompt_with_claude(self, raw_prompt: str, prompt_frame: Dict) -> str:
        """Optimiert Prompt mit Claude"""
        try:
            optimization_instruction = f"""
OPTIMIERUNGS-AUFTRAG FÜR KINDERBUCH-PROMPT:

Verbessere diesen Prompt für ein Kinderbuch (6 Jahre) in Deutsch & Englisch:

{raw_prompt}

ZIELE DER OPTIMIERUNG:
1. Erhöhe emotionale Tiefe und Verbindung zu jungen Lesern
2. Verbessere Klarheit und Struktur der Anweisungen
3. Stärke Kohärenz zwischen deutschen und englischen Versionen
4. Verstärke bildhafte Sprache und kindgerechte Metaphern
5. Behalte alle Zielvorgaben bei (Wortanzahl, Charaktere, Handlung)
6. Füge spezifische Anweisungen für Dialoge und Beschreibungen hinzu

WICHTIG:
- Gib NUR den optimierten Prompt zurück
- Markiere Änderungen mit [+NEU] und [-ENTFERNT] Kommentaren
- Stelle sicher, dass beide Sprachversionen gleichwertig optimiert werden
- Behalte die System Note Signatur bei

OPTIMIERTER PROMPT:
"""
            
            logger.info("Sende Prompt an Claude zur Optimierung...")
            optimized_prompt = self.claude_client.generate_text(optimization_instruction)
            
            # Bereinige Claude-Antwort
            if "OPTIMIERTER PROMPT:" in optimized_prompt:
                optimized_prompt = optimized_prompt.split("OPTIMIERTER PROMPT:")[1].strip()
            
            logger.info(f"Prompt erfolgreich optimiert. Länge: {len(optimized_prompt)} Zeichen")
            return optimized_prompt
            
        except Exception as e:
            logger.error(f"Fehler bei Claude-Optimierung: {e}")
            return raw_prompt
    
    def generate_chapter_with_prompt(self, prompt: str, prompt_frame: Dict) -> Tuple[str, str]:
        """Generiert Kapitel mit gegebenem Prompt"""
        try:
            logger.info("Generiere Kapitel mit GPT-4...")
            response = self.openai_client.generate_text(prompt)
            
            # Parse bilinguale Antwort
            german_text, english_text = self.router.parse_bilingual_response(response)
            
            return german_text, english_text
            
        except Exception as e:
            logger.error(f"Fehler bei Kapitelgenerierung: {e}")
            return "", ""
    
    def calculate_quality_metrics(self, german_text: str, english_text: str, prompt_frame: Dict) -> Dict:
        """Berechnet Qualitätsmetriken für beide Sprachen"""
        try:
            # Deutsche Evaluation
            german_eval = self.quality_evaluator.calculate_overall_quality_score(
                text=german_text,
                target_words=800,
                target_emotion="wonder",
                target_audience="children",
                language="de"
            )
            
            # Englische Evaluation
            english_eval = self.quality_evaluator.calculate_overall_quality_score(
                text=english_text,
                target_words=800,
                target_emotion="wonder",
                target_audience="children",
                language="en"
            )
            
            # Bilinguale Konsistenz
            bilingual_eval = self.quality_evaluator.evaluate_bilingual_content(
                german_text, english_text, prompt_frame
            )
            
            return {
                "german_evaluation": german_eval,
                "english_evaluation": english_eval,
                "bilingual_evaluation": bilingual_eval,
                "overall_score": bilingual_eval["overall_bilingual_score"]
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Qualitätsberechnung: {e}")
            return {"overall_score": 0.0}
    
    def generate_prompt_diff(self, raw_prompt: str, optimized_prompt: str) -> Dict:
        """Generiert strukturierten Diff zwischen rohem und optimiertem Prompt"""
        try:
            raw_lines = raw_prompt.split('\n')
            opt_lines = optimized_prompt.split('\n')
            
            # Zeilenweise Diff
            diff_lines = list(difflib.unified_diff(
                raw_lines, opt_lines,
                fromfile='raw_prompt',
                tofile='optimized_prompt',
                lineterm=''
            ))
            
            # Strukturelle Analyse
            changes = {
                "added_lines": [],
                "removed_lines": [],
                "modified_lines": [],
                "total_changes": 0
            }
            
            for line in diff_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    changes["added_lines"].append(line[1:])
                    changes["total_changes"] += 1
                elif line.startswith('-') and not line.startswith('---'):
                    changes["removed_lines"].append(line[1:])
                    changes["total_changes"] += 1
            
            return {
                "diff_lines": diff_lines,
                "changes": changes,
                "raw_length": len(raw_prompt),
                "optimized_length": len(optimized_prompt),
                "length_change": len(optimized_prompt) - len(raw_prompt)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Diff-Generierung: {e}")
            return {}
    
    def run_ab_test(self, prompt_frame_path: str, chapter_number: int = 1) -> Dict:
        """Führt kompletten A/B-Test durch"""
        logger.info(f"Starte A/B-Test für Kapitel {chapter_number}")
        
        try:
            # Lade PromptFrame
            is_valid, prompt_frame, message = self.router.load_and_validate_prompt_frame(prompt_frame_path)
            if not is_valid:
                raise ValueError(f"PromptFrame ungültig: {message}")
            
            # Schritt 1: Rohen Prompt generieren
            logger.info("Schritt 1: Generiere rohen Prompt")
            raw_prompt = compile_prompt_for_chatgpt(prompt_frame)
            raw_prompt_hash = generate_prompt_hash(raw_prompt)
            
            # Schritt 2: Prompt mit Claude optimieren
            logger.info("Schritt 2: Optimiere Prompt mit Claude")
            optimized_prompt = self.optimize_prompt_with_claude(raw_prompt, prompt_frame)
            optimized_prompt_hash = generate_prompt_hash(optimized_prompt)
            
            # Schritt 3: Kapitel mit rohem Prompt generieren
            logger.info("Schritt 3: Generiere Kapitel mit rohem Prompt")
            raw_german, raw_english = self.generate_chapter_with_prompt(raw_prompt, prompt_frame)
            raw_metrics = self.calculate_quality_metrics(raw_german, raw_english, prompt_frame)
            
            # Schritt 4: Kapitel mit optimiertem Prompt generieren
            logger.info("Schritt 4: Generiere Kapitel mit optimiertem Prompt")
            opt_german, opt_english = self.generate_chapter_with_prompt(optimized_prompt, prompt_frame)
            opt_metrics = self.calculate_quality_metrics(opt_german, opt_english, prompt_frame)
            
            # Schritt 5: Prompt-Diff generieren
            logger.info("Schritt 5: Generiere Prompt-Diff")
            prompt_diff = self.generate_prompt_diff(raw_prompt, optimized_prompt)
            
            # Schritt 6: Ergebnisse zusammenfassen
            results = {
                "test_timestamp": datetime.now().isoformat(),
                "chapter_number": chapter_number,
                "prompt_hashes": {
                    "raw": raw_prompt_hash,
                    "optimized": optimized_prompt_hash
                },
                "quality_comparison": {
                    "raw": raw_metrics,
                    "optimized": opt_metrics,
                    "improvement": {
                        "score_delta": opt_metrics["overall_score"] - raw_metrics["overall_score"],
                        "percentage_improvement": ((opt_metrics["overall_score"] - raw_metrics["overall_score"]) / raw_metrics["overall_score"] * 100) if raw_metrics["overall_score"] > 0 else 0
                    }
                },
                "prompt_diff": prompt_diff,
                "text_samples": {
                    "raw": {
                        "german": raw_german[:500] + "..." if len(raw_german) > 500 else raw_german,
                        "english": raw_english[:500] + "..." if len(raw_english) > 500 else raw_english
                    },
                    "optimized": {
                        "german": opt_german[:500] + "..." if len(opt_german) > 500 else opt_german,
                        "english": opt_english[:500] + "..." if len(opt_english) > 500 else opt_english
                    }
                }
            }
            
            # Schritt 7: Ergebnisse speichern
            output_file = f"output/ab_test_chapter_{chapter_number}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"A/B-Test abgeschlossen. Ergebnisse gespeichert: {output_file}")
            return results
            
        except Exception as e:
            logger.error(f"Fehler im A/B-Test: {e}")
            return {"error": str(e)}

def main():
    """Hauptfunktion für A/B-Test"""
    ab_test = PromptOptimizationABTest()
    
    # Führe A/B-Test durch
    results = ab_test.run_ab_test("data/generate_chapter_full_extended.json", chapter_number=1)
    
    if "error" not in results:
        print("\n" + "="*60)
        print("A/B-TEST ERGEBNISSE")
        print("="*60)
        print(f"Roher Prompt Hash: {results['prompt_hashes']['raw']}")
        print(f"Optimierter Prompt Hash: {results['prompt_hashes']['optimized']}")
        print(f"Qualitäts-Score Delta: {results['quality_comparison']['improvement']['score_delta']:.3f}")
        print(f"Verbesserung: {results['quality_comparison']['improvement']['percentage_improvement']:.1f}%")
        print(f"Prompt-Änderungen: {results['prompt_diff']['changes']['total_changes']} Zeilen")
        print("="*60)
    else:
        print(f"Fehler im A/B-Test: {results['error']}")

if __name__ == "__main__":
    main() 