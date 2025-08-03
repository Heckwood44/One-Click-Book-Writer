#!/usr/bin/env python3
"""
Advanced Prompt Pipeline
Integrierte Pipeline mit modularen Templates, Calibration, Feedback und Health-Dashboard
"""

import json
import logging
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import sys
sys.path.append(str(Path(__file__).parent.parent))

from compiler.modular_prompt_templates import PromptTemplateManager, ModularPromptTemplate
from scripts.prompt_calibration_system import PromptCalibrationSystem
from scripts.user_feedback_system import UserFeedbackSystem
from scripts.prompt_health_dashboard import PromptHealthDashboard
from utils.constraint_checker import ConstraintChecker
from engine.openai_adapter import OpenAIAdapter
from utils.quality_evaluator import QualityEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedPromptPipeline:
    """Erweiterte Pipeline mit allen Prompt-Engineering-Features"""
    
    def __init__(self):
        self.template_manager = PromptTemplateManager()
        self.calibration_system = PromptCalibrationSystem()
        self.feedback_system = UserFeedbackSystem()
        self.health_dashboard = PromptHealthDashboard()
        self.constraint_checker = ConstraintChecker()
        self.openai_client = OpenAIAdapter()
        self.quality_evaluator = QualityEvaluator()
    
    def run_advanced_generation_cycle(self, 
                                    template_id: str,
                                    chapter_number: int = 1,
                                    enable_calibration: bool = True,
                                    enable_feedback: bool = True,
                                    enable_constraints: bool = True,
                                    max_retries: int = 3) -> Dict:
        """
        Führt erweiterten Generierungszyklus durch
        
        Args:
            template_id: ID des zu verwendenden Templates
            chapter_number: Kapitelnummer
            enable_calibration: Ob Prompt-Calibration aktiviert ist
            enable_feedback: Ob Feedback-Sammlung aktiviert ist
            enable_constraints: Ob Constraint-Checking aktiviert ist
            max_retries: Maximale Anzahl von Retries
        """
        logger.info(f"Starte erweiterten Generierungszyklus für Template: {template_id}")
        
        try:
            results = {
                "cycle_timestamp": datetime.now().isoformat(),
                "template_id": template_id,
                "chapter_number": chapter_number,
                "calibration_results": {},
                "generation_results": {},
                "feedback_results": {},
                "health_report": {},
                "summary": {}
            }
            
            # Schritt 1: Template laden und validieren
            template = self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} nicht gefunden")
            
            # Schritt 2: Prompt-Calibration (optional)
            if enable_calibration:
                logger.info("Schritt 2: Führe Prompt-Calibration durch")
                calibration_results = self.calibration_system.calibrate_prompt_template(
                    template_id=template_id,
                    optimization_focus="emotional_depth"
                )
                results["calibration_results"] = calibration_results
                
                # Verwende mutiertes Template falls verfügbar
                if "error" not in calibration_results:
                    mutated_template_id = f"{template_id}_mutated"
                    mutated_template = self.template_manager.get_template(mutated_template_id)
                    if mutated_template:
                        template = mutated_template
                        logger.info(f"Verwende mutiertes Template: {mutated_template_id}")
            
            # Schritt 3: Kapitel-Generierung mit Retry-Logik
            logger.info("Schritt 3: Generiere Kapitel mit Retry-Logik")
            generation_results = self._generate_chapter_with_retry(
                template, chapter_number, enable_constraints, max_retries
            )
            results["generation_results"] = generation_results
            
            # Schritt 4: Feedback-Sammlung (optional)
            if enable_feedback and "error" not in generation_results:
                logger.info("Schritt 4: Sammle Feedback")
                feedback_results = self._collect_comprehensive_feedback(
                    template, generation_results, chapter_number
                )
                results["feedback_results"] = feedback_results
            
            # Schritt 5: Health-Dashboard-Update
            logger.info("Schritt 5: Aktualisiere Health-Dashboard")
            health_report = self.health_dashboard.generate_health_report()
            results["health_report"] = health_report
            
            # Schritt 6: Zusammenfassung generieren
            results["summary"] = self._generate_advanced_summary(results)
            
            # Schritt 7: Ergebnisse speichern
            output_file = f"output/advanced_pipeline_chapter_{chapter_number}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Erweiterter Generierungszyklus abgeschlossen: {output_file}")
            return results
            
        except Exception as e:
            logger.error(f"Fehler im erweiterten Generierungszyklus: {e}")
            return {"error": str(e)}
    
    def _generate_chapter_with_retry(self, 
                                   template: ModularPromptTemplate,
                                   chapter_number: int,
                                   enable_constraints: bool,
                                   max_retries: int) -> Dict:
        """Generiert Kapitel mit Retry-Logik und Constraint-Checking"""
        
        for attempt in range(max_retries + 1):
            logger.info(f"Generierungsversuch {attempt + 1}/{max_retries + 1}")
            
            try:
                # Kompiliere Prompt
                prompt = template.compile_prompt("de")
                
                # Generiere Kapitel
                response = self.openai_client.generate_text(prompt)
                
                # Parse bilinguale Antwort
                german_text, english_text = self._parse_bilingual_response(response)
                
                # Constraint-Checking (optional)
                if enable_constraints:
                    violations = self.constraint_checker.check_constraints(german_text, "de")
                    issues = self.constraint_checker.check_quality_issues(german_text, "de")
                    
                    should_retry = self.constraint_checker.should_retry(violations, issues)
                    
                    if should_retry and attempt < max_retries:
                        logger.info(f"Retry notwendig - Versuch {attempt + 1}")
                        retry_instruction = self.constraint_checker.generate_retry_instruction(violations, issues)
                        
                        # Erweitere Prompt mit Retry-Anweisung
                        enhanced_prompt = prompt + f"\n\nRETRY-INSTRUKTION:\n{retry_instruction}"
                        response = self.openai_client.generate_text(enhanced_prompt)
                        german_text, english_text = self._parse_bilingual_response(response)
                        
                        # Prüfe erneut
                        violations = self.constraint_checker.check_constraints(german_text, "de")
                        issues = self.constraint_checker.check_quality_issues(german_text, "de")
                        should_retry = self.constraint_checker.should_retry(violations, issues)
                    
                    constraint_results = {
                        "violations": [v.__dict__ for v in violations],
                        "issues": [i.__dict__ for i in issues],
                        "retry_attempts": attempt + 1,
                        "final_retry_necessary": should_retry
                    }
                else:
                    constraint_results = {"retry_attempts": 1, "final_retry_necessary": False}
                
                # Qualitäts-Evaluation
                quality_metrics = self.quality_evaluator.calculate_overall_quality_score(
                    text=german_text,
                    target_words=800,
                    target_emotion="wonder",
                    target_audience="children",
                    language="de"
                )
                
                # Ergebnisse zusammenfassen
                generation_results = {
                    "success": True,
                    "attempt": attempt + 1,
                    "german_text": german_text,
                    "english_text": english_text,
                    "prompt_hash": template.template_hash,
                    "quality_metrics": quality_metrics,
                    "constraint_results": constraint_results,
                    "word_count": len(german_text.split()),
                    "generation_timestamp": datetime.now().isoformat()
                }
                
                # Aktualisiere Template-Performance
                self.template_manager.update_template_performance(
                    template.template_id,
                    {
                        "quality_score": quality_metrics.get("overall_score", 0),
                        "response_length": len(response),
                        "retry_count": attempt + 1,
                        "constraint_violations": len(constraint_results.get("violations", [])),
                        "last_used": datetime.now().isoformat()
                    }
                )
                
                return generation_results
                
            except Exception as e:
                logger.error(f"Fehler bei Generierungsversuch {attempt + 1}: {e}")
                if attempt == max_retries:
                    return {
                        "success": False,
                        "error": str(e),
                        "attempt": attempt + 1
                    }
        
        return {"success": False, "error": "Maximale Retry-Anzahl erreicht"}
    
    def _parse_bilingual_response(self, response: str) -> Tuple[str, str]:
        """Parst bilinguale Antwort"""
        try:
            if "---" in response:
                parts = response.split("---")
                if len(parts) >= 2:
                    german_text = parts[0].strip()
                    english_text = parts[1].strip()
                    return german_text, english_text
            
            # Fallback: Verwende gesamte Antwort als deutsche Version
            return response.strip(), ""
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen der bilingualen Antwort: {e}")
            return response.strip(), ""
    
    def _collect_comprehensive_feedback(self, 
                                      template: ModularPromptTemplate,
                                      generation_results: Dict,
                                      chapter_number: int) -> Dict:
        """Sammelt umfassendes Feedback"""
        
        feedback_results = {
            "feedback_collected": False,
            "feedback_entries": [],
            "feedback_summary": {}
        }
        
        try:
            # Automatisches Feedback basierend auf Qualitätsmetriken
            quality_metrics = generation_results.get("quality_metrics", {})
            quality_score = quality_metrics.get("overall_score", 0)
            
            # Simuliere Nutzer-Feedback basierend auf Qualitäts-Score
            if quality_score > 0.8:
                user_rating = 5
                comment = "Ausgezeichnete Geschichte mit emotionaler Tiefe und kindgerechter Sprache"
            elif quality_score > 0.6:
                user_rating = 4
                comment = "Gute Geschichte, könnte mehr Dialoge haben"
            elif quality_score > 0.4:
                user_rating = 3
                comment = "Durchschnittliche Qualität, Verbesserungspotential vorhanden"
            else:
                user_rating = 2
                comment = "Qualität verbesserungsbedürftig, zu kurz oder flach"
            
            # Sammle Feedback für deutsche Version
            self.feedback_system.collect_feedback(
                chapter_number=chapter_number,
                prompt_hash=template.template_hash,
                quality_score=quality_score,
                language="de",
                rating=user_rating,
                comment=comment
            )
            
            # Sammle Feedback für englische Version (falls vorhanden)
            english_text = generation_results.get("english_text", "")
            if english_text:
                english_quality = self.quality_evaluator.calculate_overall_quality_score(
                    text=english_text,
                    target_words=800,
                    target_emotion="wonder",
                    target_audience="children",
                    language="en"
                )
                
                english_rating = max(1, user_rating - 1)  # Leicht niedriger für englische Version
                english_comment = f"English version: {comment.lower()}"
                
                self.feedback_system.collect_feedback(
                    chapter_number=chapter_number,
                    prompt_hash=template.template_hash,
                    quality_score=english_quality.get("overall_score", 0),
                    language="en",
                    rating=english_rating,
                    comment=english_comment
                )
            
            # Generiere Feedback-Zusammenfassung
            feedback_summary = self.feedback_system.generate_feedback_summary()
            
            feedback_results.update({
                "feedback_collected": True,
                "feedback_summary": feedback_summary,
                "simulated_rating": user_rating,
                "quality_correlation": feedback_summary.get("correlation_analysis", {}).get("correlation_quality_vs_rating", 0)
            })
            
        except Exception as e:
            logger.error(f"Fehler bei Feedback-Sammlung: {e}")
            feedback_results["error"] = str(e)
        
        return feedback_results
    
    def _generate_advanced_summary(self, results: Dict) -> Dict:
        """Generiert erweiterte Zusammenfassung"""
        
        summary = {
            "pipeline_success": "error" not in results,
            "template_performance": {},
            "quality_metrics": {},
            "feedback_insights": {},
            "health_indicators": {},
            "recommendations": []
        }
        
        # Template-Performance
        if "generation_results" in results and results["generation_results"].get("success"):
            gen_results = results["generation_results"]
            summary["template_performance"] = {
                "template_hash": gen_results.get("prompt_hash", ""),
                "retry_attempts": gen_results.get("attempt", 1),
                "word_count": gen_results.get("word_count", 0),
                "generation_success": gen_results.get("success", False)
            }
        
        # Qualitäts-Metriken
        if "generation_results" in results:
            quality_metrics = results["generation_results"].get("quality_metrics", {})
            summary["quality_metrics"] = {
                "overall_score": quality_metrics.get("overall_score", 0),
                "quality_level": quality_metrics.get("quality_level", "Unknown"),
                "review_required": quality_metrics.get("review_required", False)
            }
        
        # Feedback-Insights
        if "feedback_results" in results:
            feedback = results["feedback_results"]
            summary["feedback_insights"] = {
                "feedback_collected": feedback.get("feedback_collected", False),
                "simulated_rating": feedback.get("simulated_rating", 0),
                "quality_correlation": feedback.get("quality_correlation", 0)
            }
        
        # Health-Indikatoren
        if "health_report" in results:
            health = results["health_report"]
            summary["health_indicators"] = {
                "overall_health_score": health.get("overall_health_score", 0),
                "template_count": health.get("template_health", {}).get("total_templates", 0),
                "active_templates": health.get("template_health", {}).get("active_templates", 0)
            }
        
        # Empfehlungen
        recommendations = []
        
        # Qualitäts-basierte Empfehlungen
        quality_score = summary["quality_metrics"].get("overall_score", 0)
        if quality_score < 0.6:
            recommendations.append("Template-Optimierung erforderlich - Qualitäts-Score zu niedrig")
        elif quality_score > 0.8:
            recommendations.append("Template für Produktion freigeben - Exzellente Qualität")
        
        # Feedback-basierte Empfehlungen
        correlation = summary["feedback_insights"].get("quality_correlation", 0)
        if abs(correlation) < 0.4:
            recommendations.append("Quality-Evaluator anpassen - Korrelation mit Nutzer-Ratings verbessern")
        
        # Health-basierte Empfehlungen
        health_score = summary["health_indicators"].get("overall_health_score", 0)
        if health_score < 0.6:
            recommendations.append("System-Gesundheit verbessern - Mehr Templates und bessere Performance")
        
        summary["recommendations"] = recommendations
        
        return summary
    
    def run_batch_advanced_cycle(self, 
                                template_ids: List[str],
                                chapters: List[int],
                                enable_calibration: bool = True,
                                enable_feedback: bool = True) -> Dict:
        """Führt erweiterten Batch-Zyklus durch"""
        
        logger.info(f"Starte erweiterten Batch-Zyklus für {len(template_ids)} Templates")
        
        batch_results = {
            "batch_timestamp": datetime.now().isoformat(),
            "template_ids": template_ids,
            "chapters": chapters,
            "results": {},
            "overall_summary": {}
        }
        
        for template_id in template_ids:
            for chapter_number in chapters:
                logger.info(f"Verarbeite Template {template_id}, Kapitel {chapter_number}")
                
                result = self.run_advanced_generation_cycle(
                    template_id=template_id,
                    chapter_number=chapter_number,
                    enable_calibration=enable_calibration,
                    enable_feedback=enable_feedback,
                    enable_constraints=True,
                    max_retries=3
                )
                
                batch_results["results"][f"{template_id}_chapter_{chapter_number}"] = result
        
        # Generiere Gesamtzusammenfassung
        batch_results["overall_summary"] = self._generate_batch_summary(batch_results["results"])
        
        # Speichere Batch-Ergebnisse
        batch_file = f"output/batch_advanced_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Erweiterter Batch-Zyklus abgeschlossen: {batch_file}")
        return batch_results
    
    def _generate_batch_summary(self, results: Dict) -> Dict:
        """Generiert Zusammenfassung für Batch-Zyklus"""
        
        successful_generations = 0
        total_attempts = 0
        quality_scores = []
        feedback_ratings = []
        
        for result in results.values():
            if "error" not in result:
                successful_generations += 1
                
                gen_results = result.get("generation_results", {})
                if gen_results.get("success"):
                    total_attempts += gen_results.get("attempt", 1)
                    
                    quality_score = gen_results.get("quality_metrics", {}).get("overall_score", 0)
                    quality_scores.append(quality_score)
                
                feedback = result.get("feedback_results", {})
                if feedback.get("feedback_collected"):
                    rating = feedback.get("simulated_rating", 0)
                    feedback_ratings.append(rating)
        
        summary = {
            "total_generations": len(results),
            "successful_generations": successful_generations,
            "success_rate": successful_generations / len(results) if results else 0,
            "average_attempts": total_attempts / successful_generations if successful_generations > 0 else 0,
            "average_quality_score": statistics.mean(quality_scores) if quality_scores else 0,
            "average_feedback_rating": statistics.mean(feedback_ratings) if feedback_ratings else 0
        }
        
        return summary

def main():
    """Beispiel für erweiterte Pipeline"""
    pipeline = AdvancedPromptPipeline()
    
    # Erstelle Standard-Template falls nicht vorhanden
    if not pipeline.template_manager.get_template("children_book_v1"):
        pipeline.template_manager.create_default_children_book_template()
        pipeline.template_manager.save_templates()
    
    # Führe erweiterten Generierungszyklus durch
    results = pipeline.run_advanced_generation_cycle(
        template_id="children_book_v1",
        chapter_number=1,
        enable_calibration=True,
        enable_feedback=True,
        enable_constraints=True,
        max_retries=3
    )
    
    if "error" not in results:
        summary = results.get("summary", {})
        
        print("\n" + "="*60)
        print("ERWEITERTE PROMPT-PIPELINE ERGEBNISSE")
        print("="*60)
        
        print(f"Pipeline-Erfolg: {'✅ JA' if summary.get('pipeline_success') else '❌ NEIN'}")
        
        # Template-Performance
        template_perf = summary.get("template_performance", {})
        print(f"Template Hash: {template_perf.get('template_hash', 'N/A')}")
        print(f"Retry-Versuche: {template_perf.get('retry_attempts', 0)}")
        print(f"Wortanzahl: {template_perf.get('word_count', 0)}")
        
        # Qualitäts-Metriken
        quality = summary.get("quality_metrics", {})
        print(f"Quality-Score: {quality.get('overall_score', 0):.3f}")
        print(f"Quality-Level: {quality.get('quality_level', 'N/A')}")
        
        # Feedback-Insights
        feedback = summary.get("feedback_insights", {})
        print(f"Feedback gesammelt: {'✅ JA' if feedback.get('feedback_collected') else '❌ NEIN'}")
        print(f"Simuliertes Rating: {feedback.get('simulated_rating', 0)}/5")
        print(f"Quality-Korrelation: {feedback.get('quality_correlation', 0):.3f}")
        
        # Health-Indikatoren
        health = summary.get("health_indicators", {})
        print(f"Health-Score: {health.get('overall_health_score', 0):.2f}/1.0")
        print(f"Aktive Templates: {health.get('active_templates', 0)}")
        
        print("\nEmpfehlungen:")
        for rec in summary.get("recommendations", []):
            print(f"• {rec}")
        
        print("="*60)
    else:
        print(f"Fehler in der erweiterten Pipeline: {results['error']}")

if __name__ == "__main__":
    main() 