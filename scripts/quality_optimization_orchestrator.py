#!/usr/bin/env python3
"""
Quality Optimization Orchestrator
Automatisiert A/B-Tests, Feedback-Sammlung und erweiterte Berichterstattung
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from prompt_optimization_ab_test import PromptOptimizationABTest
from user_feedback_system import UserFeedbackSystem
from enhanced_chapter_reporting import EnhancedChapterReporting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityOptimizationOrchestrator:
    """Orchestriert Qualitätsoptimierung mit A/B-Tests und Feedback"""
    
    def __init__(self):
        self.ab_test = PromptOptimizationABTest()
        self.feedback_system = UserFeedbackSystem()
        self.reporting = EnhancedChapterReporting()
    
    def run_full_optimization_cycle(self, 
                                   prompt_frame_path: str,
                                   chapter_number: int = 1,
                                   collect_feedback: bool = True,
                                   generate_reports: bool = True) -> Dict:
        """
        Führt vollständigen Optimierungszyklus durch
        
        Args:
            prompt_frame_path: Pfad zum PromptFrame
            chapter_number: Kapitelnummer
            collect_feedback: Ob Feedback gesammelt werden soll
            generate_reports: Ob Reports generiert werden sollen
        """
        logger.info(f"Starte vollständigen Optimierungszyklus für Kapitel {chapter_number}")
        
        try:
            results = {
                "cycle_timestamp": datetime.now().isoformat(),
                "chapter_number": chapter_number,
                "ab_test_results": {},
                "feedback_collected": False,
                "reports_generated": False,
                "summary": {}
            }
            
            # Schritt 1: A/B-Test durchführen
            logger.info("Schritt 1: Führe A/B-Test durch")
            ab_results = self.ab_test.run_ab_test(prompt_frame_path, chapter_number)
            
            if "error" not in ab_results:
                results["ab_test_results"] = ab_results
                logger.info("A/B-Test erfolgreich abgeschlossen")
            else:
                logger.error(f"A/B-Test fehlgeschlagen: {ab_results['error']}")
                return {"error": f"A/B-Test fehlgeschlagen: {ab_results['error']}"}
            
            # Schritt 2: Feedback sammeln (optional)
            if collect_feedback:
                logger.info("Schritt 2: Sammle Feedback")
                feedback_collected = self._collect_sample_feedback(chapter_number, ab_results)
                results["feedback_collected"] = feedback_collected
            
            # Schritt 3: Erweiterte Reports generieren
            if generate_reports:
                logger.info("Schritt 3: Generiere erweiterte Reports")
                enhanced_report = self.reporting.generate_enhanced_report(
                    chapter_number=chapter_number,
                    ab_test_results=ab_results,
                    include_feedback=collect_feedback
                )
                results["reports_generated"] = "error" not in enhanced_report
            
            # Schritt 4: Zusammenfassung generieren
            results["summary"] = self._generate_optimization_summary(ab_results, collect_feedback)
            
            # Schritt 5: Ergebnisse speichern
            output_file = f"output/optimization_cycle_chapter_{chapter_number}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Optimierungszyklus abgeschlossen. Ergebnisse: {output_file}")
            return results
            
        except Exception as e:
            logger.error(f"Fehler im Optimierungszyklus: {e}")
            return {"error": str(e)}
    
    def _collect_sample_feedback(self, chapter_number: int, ab_results: Dict) -> bool:
        """Sammelt Beispiel-Feedback für A/B-Test-Ergebnisse"""
        try:
            # Extrahiere Prompt-Hashes
            prompt_hashes = ab_results.get("prompt_hashes", {})
            raw_hash = prompt_hashes.get("raw", "")
            optimized_hash = prompt_hashes.get("optimized", "")
            
            # Extrahiere Quality-Scores
            quality_comparison = ab_results.get("quality_comparison", {})
            raw_score = quality_comparison.get("raw", {}).get("overall_score", 0)
            optimized_score = quality_comparison.get("optimized", {}).get("overall_score", 0)
            
            # Sammle Feedback für rohe Version
            self.feedback_system.collect_feedback(
                chapter_number=chapter_number,
                prompt_hash=raw_hash,
                quality_score=raw_score,
                language="de",
                rating=4 if raw_score > 0.6 else 3,
                comment="Gute Grundstruktur, aber könnte mehr emotionale Tiefe haben"
            )
            
            self.feedback_system.collect_feedback(
                chapter_number=chapter_number,
                prompt_hash=raw_hash,
                quality_score=raw_score,
                language="en",
                rating=3 if raw_score > 0.6 else 2,
                comment="Solid foundation, needs more engaging dialogue"
            )
            
            # Sammle Feedback für optimierte Version
            self.feedback_system.collect_feedback(
                chapter_number=chapter_number,
                prompt_hash=optimized_hash,
                quality_score=optimized_score,
                language="de",
                rating=5 if optimized_score > 0.7 else 4,
                comment="Sehr gute emotionale Tiefe und bildhafte Sprache"
            )
            
            self.feedback_system.collect_feedback(
                chapter_number=chapter_number,
                prompt_hash=optimized_hash,
                quality_score=optimized_score,
                language="en",
                rating=4 if optimized_score > 0.7 else 3,
                comment="Much better emotional engagement and dialogue"
            )
            
            logger.info("Beispiel-Feedback erfolgreich gesammelt")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von Feedback: {e}")
            return False
    
    def _generate_optimization_summary(self, ab_results: Dict, feedback_collected: bool) -> Dict:
        """Generiert Zusammenfassung der Optimierung"""
        try:
            quality_comparison = ab_results.get("quality_comparison", {})
            improvement = quality_comparison.get("improvement", {})
            prompt_diff = ab_results.get("prompt_diff", {})
            
            summary = {
                "base_prompt_hash": ab_results.get("prompt_hashes", {}).get("raw", ""),
                "optimized_prompt_hash": ab_results.get("prompt_hashes", {}).get("optimized", ""),
                "quality_score_delta": improvement.get("score_delta", 0),
                "percentage_improvement": improvement.get("percentage_improvement", 0),
                "prompt_changes": prompt_diff.get("changes", {}).get("total_changes", 0),
                "optimization_success": improvement.get("score_delta", 0) > 0,
                "feedback_available": feedback_collected
            }
            
            # Füge Feedback-Zusammenfassung hinzu
            if feedback_collected:
                feedback_summary = self.feedback_system.generate_feedback_summary()
                summary["user_feedback_summary"] = {
                    "total_entries": feedback_summary.get("total_feedback_entries", 0),
                    "avg_rating": feedback_summary.get("overall_statistics", {}).get("avg_rating", 0),
                    "correlation": feedback_summary.get("correlation_analysis", {}).get("correlation_quality_vs_rating", 0)
                }
            
            # Beste Prompt-Template identifizieren
            if feedback_collected:
                best_prompts = self.feedback_system.get_best_performing_prompts()
                if best_prompts:
                    summary["best_prompt_template"] = {
                        "hash": best_prompts[0]["prompt_hash"],
                        "combined_score": best_prompts[0]["combined_score"],
                        "avg_rating": best_prompts[0]["avg_rating"]
                    }
                else:
                    summary["best_prompt_template"] = "Keine ausreichenden Daten"
            else:
                summary["best_prompt_template"] = "Feedback nicht verfügbar"
            
            # Nächste Aktionen
            summary["next_actions"] = self._generate_next_actions(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Fehler bei Generierung der Zusammenfassung: {e}")
            return {"error": str(e)}
    
    def _generate_next_actions(self, summary: Dict) -> List[str]:
        """Generiert nächste Aktionen basierend auf Optimierungsergebnissen"""
        actions = []
        
        # Qualitätsverbesserung
        score_delta = summary.get("quality_score_delta", 0)
        if score_delta >= 0.1:
            actions.append("Optimierte Prompt-Version für Produktion übernehmen")
        elif score_delta >= 0.05:
            actions.append("Optimierte Version weiter testen und verfeinern")
        else:
            actions.append("Prompt-Optimierung überarbeiten und neue Ansätze testen")
        
        # Feedback-basierte Aktionen
        if summary.get("feedback_available"):
            correlation = summary.get("user_feedback_summary", {}).get("correlation", 0)
            if abs(correlation) < 0.4:
                actions.append("Quality-Evaluator anpassen - Korrelation mit Nutzer-Ratings verbessern")
            
            avg_rating = summary.get("user_feedback_summary", {}).get("avg_rating", 0)
            if avg_rating < 3.5:
                actions.append("Generelle Qualitätsverbesserung basierend auf Nutzer-Feedback")
        
        # Prompt-Änderungen
        prompt_changes = summary.get("prompt_changes", 0)
        if prompt_changes > 20:
            actions.append("Prompt-Änderungen analysieren und erfolgreiche Muster extrahieren")
        
        # Versionierung
        actions.append("Prompt-Versionierung mit neuen Erkenntnissen aktualisieren")
        
        return actions
    
    def run_batch_optimization(self, 
                              prompt_frame_path: str,
                              chapters: List[int],
                              collect_feedback: bool = True) -> Dict:
        """Führt Optimierung für mehrere Kapitel durch"""
        logger.info(f"Starte Batch-Optimierung für Kapitel: {chapters}")
        
        batch_results = {
            "batch_timestamp": datetime.now().isoformat(),
            "chapters": chapters,
            "results": {},
            "overall_summary": {}
        }
        
        for chapter_number in chapters:
            logger.info(f"Optimiere Kapitel {chapter_number}")
            result = self.run_full_optimization_cycle(
                prompt_frame_path=prompt_frame_path,
                chapter_number=chapter_number,
                collect_feedback=collect_feedback,
                generate_reports=True
            )
            
            batch_results["results"][f"chapter_{chapter_number}"] = result
        
        # Generiere Gesamtzusammenfassung
        batch_results["overall_summary"] = self._generate_batch_summary(batch_results["results"])
        
        # Speichere Batch-Ergebnisse
        batch_file = f"output/batch_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Batch-Optimierung abgeschlossen: {batch_file}")
        return batch_results
    
    def _generate_batch_summary(self, results: Dict) -> Dict:
        """Generiert Zusammenfassung für Batch-Optimierung"""
        try:
            successful_chapters = []
            failed_chapters = []
            score_deltas = []
            
            for chapter_key, result in results.items():
                if "error" not in result:
                    successful_chapters.append(chapter_key)
                    summary = result.get("summary", {})
                    score_delta = summary.get("quality_score_delta", 0)
                    score_deltas.append(score_delta)
                else:
                    failed_chapters.append(chapter_key)
            
            if score_deltas:
                avg_improvement = sum(score_deltas) / len(score_deltas)
                positive_improvements = sum(1 for delta in score_deltas if delta > 0)
                significant_improvements = sum(1 for delta in score_deltas if delta >= 0.1)
            else:
                avg_improvement = 0
                positive_improvements = 0
                significant_improvements = 0
            
            return {
                "total_chapters": len(results),
                "successful_chapters": len(successful_chapters),
                "failed_chapters": len(failed_chapters),
                "average_improvement": avg_improvement,
                "positive_improvements": positive_improvements,
                "significant_improvements": significant_improvements,
                "success_rate": len(successful_chapters) / len(results) if results else 0
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Batch-Zusammenfassung: {e}")
            return {"error": str(e)}

def main():
    """Hauptfunktion für Qualitätsoptimierung"""
    orchestrator = QualityOptimizationOrchestrator()
    
    # Führe vollständigen Optimierungszyklus durch
    results = orchestrator.run_full_optimization_cycle(
        prompt_frame_path="data/generate_chapter_full_extended.json",
        chapter_number=1,
        collect_feedback=True,
        generate_reports=True
    )
    
    if "error" not in results:
        summary = results.get("summary", {})
        
        print("\n" + "="*60)
        print("QUALITÄTSOPTIMIERUNG - ZUSAMMENFASSUNG")
        print("="*60)
        print(f"Base Prompt Hash: {summary.get('base_prompt_hash', 'N/A')}")
        print(f"Optimized Prompt Hash: {summary.get('optimized_prompt_hash', 'N/A')}")
        print(f"Quality Score Delta: {summary.get('quality_score_delta', 0):.3f}")
        print(f"Percentage Improvement: {summary.get('percentage_improvement', 0):.1f}%")
        print(f"Optimization Success: {'✅ JA' if summary.get('optimization_success') else '❌ NEIN'}")
        
        if summary.get("feedback_available"):
            feedback_summary = summary.get("user_feedback_summary", {})
            print(f"User Feedback Entries: {feedback_summary.get('total_entries', 0)}")
            print(f"Average Rating: {feedback_summary.get('avg_rating', 0):.2f}/5")
            print(f"Quality vs Rating Correlation: {feedback_summary.get('correlation', 0):.3f}")
        
        best_template = summary.get("best_prompt_template", {})
        if isinstance(best_template, dict):
            print(f"Best Prompt Template: {best_template.get('hash', 'N/A')} (Score: {best_template.get('combined_score', 0):.2f})")
        
        print("\nNächste Aktionen:")
        for action in summary.get("next_actions", []):
            print(f"• {action}")
        
        print("="*60)
    else:
        print(f"Fehler in der Qualitätsoptimierung: {results['error']}")

if __name__ == "__main__":
    main() 