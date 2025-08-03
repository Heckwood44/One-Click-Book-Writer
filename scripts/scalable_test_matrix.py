#!/usr/bin/env python3
"""
Scalable Test Matrix
Automatisierte Testmatrix für alle Altersklassen und Genres mit A/B-Vergleichen
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics

import sys
sys.path.append(str(Path(__file__).parent.parent))

from compiler.scalable_prompt_compiler import ScalablePromptCompiler
from utils.target_group_evaluator import TargetGroupEvaluator
from scripts.user_feedback_system import UserFeedbackSystem
from engine.openai_adapter import OpenAIAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScalableTestMatrix:
    """Automatisierte Testmatrix für skalierbare Prompt-Generierung"""
    
    def __init__(self):
        self.compiler = ScalablePromptCompiler()
        self.evaluator = TargetGroupEvaluator()
        self.feedback_system = UserFeedbackSystem()
        self.openai_client = OpenAIAdapter()
        
        # Definiere Test-Matrix
        self.test_matrix = self._define_test_matrix()
    
    def _define_test_matrix(self) -> List[Dict]:
        """Definiert die Test-Matrix mit exemplarischen Kombinationen"""
        return [
            # Kinder-Abenteuer
            {
                "segment": "Kinder 6 Jahre / Abenteuer",
                "age_group": "early_reader",
                "genre": "adventure",
                "emotion": "courage",
                "description": "Spannende Abenteuergeschichten für Erstleser"
            },
            # Kinder-Fantasy
            {
                "segment": "Kinder 9 Jahre / Fantasy",
                "age_group": "middle_grade",
                "genre": "fantasy",
                "emotion": "wonder",
                "description": "Magische Geschichten für Mittelstufe"
            },
            # Teenager-Selbstfindung
            {
                "segment": "Teenager 14 Jahre / Selbstfindung",
                "age_group": "young_adult",
                "genre": "self_discovery",
                "emotion": "growth",
                "description": "Authentische Geschichten über Identitätsfindung"
            },
            # Erwachsene-Ratgeber
            {
                "segment": "Erwachsene / Ratgeber",
                "age_group": "adult",
                "genre": "self_help",
                "emotion": "growth",
                "description": "Inspirierende Geschichten für Erwachsene"
            },
            # Kinder-Freundschaft
            {
                "segment": "Kinder 7 Jahre / Freundschaft",
                "age_group": "early_reader",
                "genre": "friendship",
                "emotion": "friendship",
                "description": "Warme Geschichten über Freundschaft"
            },
            # Jugendliche-Mystery
            {
                "segment": "Jugendliche 15 Jahre / Mystery",
                "age_group": "young_adult",
                "genre": "mystery",
                "emotion": "mystery",
                "description": "Spannende Rätselgeschichten"
            }
        ]
    
    def run_complete_test_matrix(self, enable_ab_testing: bool = True) -> Dict:
        """Führt komplette Test-Matrix durch"""
        logger.info("Starte komplette Test-Matrix")
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "matrix_results": {},
            "ab_test_results": {},
            "performance_summary": {},
            "top_performers": [],
            "recommendations": []
        }
        
        # Führe Tests für jede Kombination durch
        for test_case in self.test_matrix:
            segment = test_case["segment"]
            logger.info(f"Teste Segment: {segment}")
            
            # Generiere Prompt
            prompt_result = self.compiler.compile_scalable_prompt(
                age_group=test_case["age_group"],
                genre=test_case["genre"],
                emotion=test_case["emotion"]
            )
            
            if "error" in prompt_result:
                logger.error(f"Fehler bei Prompt-Generierung für {segment}: {prompt_result['error']}")
                continue
            
            # Generiere Kapitel
            chapter_result = self._generate_chapter_for_segment(
                prompt_result["compiled_prompt"],
                test_case
            )
            
            # Evaluiere Ergebnis
            evaluation_result = self.evaluator.evaluate_for_target_group(
                text=chapter_result.get("german_text", ""),
                age_group=test_case["age_group"],
                genre=test_case["genre"],
                language="de"
            )
            
            # Sammle Feedback
            feedback_result = self._collect_segment_feedback(
                test_case, chapter_result, evaluation_result
            )
            
            # Speichere Ergebnisse
            results["matrix_results"][segment] = {
                "test_case": test_case,
                "prompt_hash": prompt_result["prompt_hash"],
                "chapter_result": chapter_result,
                "evaluation": {
                    "overall_score": evaluation_result.overall_score,
                    "readability_score": evaluation_result.readability_score,
                    "age_appropriateness": evaluation_result.age_appropriateness,
                    "genre_compliance": evaluation_result.genre_compliance,
                    "emotional_depth": evaluation_result.emotional_depth,
                    "engagement_score": evaluation_result.engagement_score,
                    "flags": evaluation_result.flags,
                    "recommendations": evaluation_result.recommendations
                },
                "feedback": feedback_result
            }
        
        # Führe A/B-Tests durch falls aktiviert
        if enable_ab_testing:
            results["ab_test_results"] = self._run_ab_tests(results["matrix_results"])
        
        # Generiere Performance-Summary
        results["performance_summary"] = self._generate_performance_summary(results["matrix_results"])
        
        # Identifiziere Top-Performer
        results["top_performers"] = self._identify_top_performers(results["matrix_results"])
        
        # Generiere Empfehlungen
        results["recommendations"] = self._generate_matrix_recommendations(results)
        
        # Speichere Ergebnisse
        output_file = f"output/scalable_test_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test-Matrix abgeschlossen: {output_file}")
        return results
    
    def _generate_chapter_for_segment(self, prompt: str, test_case: Dict) -> Dict:
        """Generiert Kapitel für spezifisches Segment"""
        try:
            # Generiere Kapitel
            response = self.openai_client.generate_text(prompt)
            
            # Parse bilinguale Antwort
            german_text, english_text = self._parse_bilingual_response(response)
            
            return {
                "success": True,
                "german_text": german_text,
                "english_text": english_text,
                "response_length": len(response),
                "word_count": len(german_text.split()),
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Kapitel-Generierung: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
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
    
    def _collect_segment_feedback(self, test_case: Dict, chapter_result: Dict, evaluation_result) -> Dict:
        """Sammelt Feedback für Segment"""
        try:
            # Simuliere Nutzer-Feedback basierend auf Evaluation
            quality_score = evaluation_result.overall_score
            
            if quality_score > 0.8:
                user_rating = 5
                comment = f"Exzellente {test_case['genre']}-Geschichte für {test_case['age_group']}"
            elif quality_score > 0.6:
                user_rating = 4
                comment = f"Gute {test_case['genre']}-Geschichte mit Verbesserungspotential"
            elif quality_score > 0.4:
                user_rating = 3
                comment = f"Durchschnittliche Qualität für {test_case['genre']}"
            else:
                user_rating = 2
                comment = f"Qualität verbesserungsbedürftig für {test_case['genre']}"
            
            # Sammle Feedback
            self.feedback_system.collect_feedback(
                chapter_number=1,
                prompt_hash=chapter_result.get("prompt_hash", ""),
                quality_score=quality_score,
                language="de",
                rating=user_rating,
                comment=comment,
                metadata={
                    "age_group": test_case["age_group"],
                    "genre": test_case["genre"],
                    "emotion": test_case["emotion"],
                    "segment": test_case["segment"]
                }
            )
            
            return {
                "feedback_collected": True,
                "simulated_rating": user_rating,
                "quality_correlation": quality_score,
                "comment": comment
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Feedback-Sammlung: {e}")
            return {
                "feedback_collected": False,
                "error": str(e)
            }
    
    def _run_ab_tests(self, matrix_results: Dict) -> Dict:
        """Führt A/B-Tests für Top-Performer durch"""
        ab_results = {}
        
        # Wähle Top-Performer für A/B-Tests
        top_performers = self._identify_top_performers(matrix_results)
        
        for performer in top_performers[:3]:  # Teste Top 3
            segment = performer["segment"]
            logger.info(f"Führe A/B-Test durch für: {segment}")
            
            # Hole Original-Ergebnisse
            original_result = matrix_results[segment]
            
            # Generiere optimierte Version
            optimized_result = self._generate_optimized_version(original_result)
            
            # Vergleiche Ergebnisse
            comparison = self._compare_ab_results(original_result, optimized_result)
            
            ab_results[segment] = {
                "original": original_result,
                "optimized": optimized_result,
                "comparison": comparison,
                "improvement": comparison.get("score_delta", 0)
            }
        
        return ab_results
    
    def _generate_optimized_version(self, original_result: Dict) -> Dict:
        """Generiert optimierte Version basierend auf Feedback"""
        test_case = original_result["test_case"]
        evaluation = original_result["evaluation"]
        
        # Erstelle optimierten Prompt basierend auf Empfehlungen
        optimization_focus = self._determine_optimization_focus(evaluation)
        
        # Generiere optimierten Prompt
        optimized_prompt = self.compiler.compile_scalable_prompt(
            age_group=test_case["age_group"],
            genre=test_case["genre"],
            emotion=test_case["emotion"],
            custom_context={
                "description": f"Optimierte Version basierend auf Feedback",
                "instructions": f"Fokussiere auf: {optimization_focus}",
                "characters": "Verbessere Charakterentwicklung",
                "setting": "Verstärke Genre-Elemente"
            }
        )
        
        # Generiere optimiertes Kapitel
        optimized_chapter = self._generate_chapter_for_segment(
            optimized_prompt["compiled_prompt"], test_case
        )
        
        # Evaluiere optimierte Version
        optimized_evaluation = self.evaluator.evaluate_for_target_group(
            text=optimized_chapter.get("german_text", ""),
            age_group=test_case["age_group"],
            genre=test_case["genre"],
            language="de"
        )
        
        return {
            "prompt_hash": optimized_prompt["prompt_hash"],
            "chapter_result": optimized_chapter,
            "evaluation": {
                "overall_score": optimized_evaluation.overall_score,
                "readability_score": optimized_evaluation.readability_score,
                "age_appropriateness": optimized_evaluation.age_appropriateness,
                "genre_compliance": optimized_evaluation.genre_compliance,
                "emotional_depth": optimized_evaluation.emotional_depth,
                "engagement_score": optimized_evaluation.engagement_score
            }
        }
    
    def _determine_optimization_focus(self, evaluation: Dict) -> str:
        """Bestimmt Fokus für Optimierung basierend auf Evaluation"""
        scores = {
            "readability": evaluation["readability_score"],
            "age_appropriateness": evaluation["age_appropriateness"],
            "genre_compliance": evaluation["genre_compliance"],
            "emotional_depth": evaluation["emotional_depth"],
            "engagement": evaluation["engagement_score"]
        }
        
        # Finde niedrigsten Score
        min_score_key = min(scores, key=scores.get)
        min_score = scores[min_score_key]
        
        if min_score < 0.5:
            return f"Verbessere {min_score_key}"
        else:
            return "Erhöhe emotionale Tiefe und Engagement"
    
    def _compare_ab_results(self, original: Dict, optimized: Dict) -> Dict:
        """Vergleicht Original- und optimierte Ergebnisse"""
        original_score = original["evaluation"]["overall_score"]
        optimized_score = optimized["evaluation"]["overall_score"]
        
        score_delta = optimized_score - original_score
        improvement_percentage = (score_delta / max(original_score, 0.1)) * 100
        
        return {
            "score_delta": score_delta,
            "improvement_percentage": improvement_percentage,
            "original_score": original_score,
            "optimized_score": optimized_score,
            "significant_improvement": score_delta > 0.1
        }
    
    def _generate_performance_summary(self, matrix_results: Dict) -> Dict:
        """Generiert Performance-Summary für alle Segmente"""
        scores = []
        segments_by_performance = []
        
        for segment, result in matrix_results.items():
            score = result["evaluation"]["overall_score"]
            scores.append(score)
            
            segments_by_performance.append({
                "segment": segment,
                "score": score,
                "age_group": result["test_case"]["age_group"],
                "genre": result["test_case"]["genre"]
            })
        
        # Sortiere nach Performance
        segments_by_performance.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "total_segments": len(matrix_results),
            "average_score": statistics.mean(scores) if scores else 0,
            "median_score": statistics.median(scores) if scores else 0,
            "score_std": statistics.stdev(scores) if len(scores) > 1 else 0,
            "top_performers": segments_by_performance[:3],
            "bottom_performers": segments_by_performance[-3:],
            "performance_distribution": {
                "excellent": len([s for s in scores if s >= 0.8]),
                "good": len([s for s in scores if 0.6 <= s < 0.8]),
                "fair": len([s for s in scores if 0.4 <= s < 0.6]),
                "poor": len([s for s in scores if s < 0.4])
            }
        }
    
    def _identify_top_performers(self, matrix_results: Dict) -> List[Dict]:
        """Identifiziert Top-Performer"""
        performers = []
        
        for segment, result in matrix_results.items():
            performers.append({
                "segment": segment,
                "score": result["evaluation"]["overall_score"],
                "age_group": result["test_case"]["age_group"],
                "genre": result["test_case"]["genre"],
                "emotion": result["test_case"]["emotion"],
                "prompt_hash": result["prompt_hash"]
            })
        
        # Sortiere nach Score
        performers.sort(key=lambda x: x["score"], reverse=True)
        
        return performers
    
    def _generate_matrix_recommendations(self, results: Dict) -> List[str]:
        """Generiert Empfehlungen basierend auf Matrix-Ergebnissen"""
        recommendations = []
        
        performance_summary = results["performance_summary"]
        matrix_results = results["matrix_results"]
        
        # Allgemeine Empfehlungen basierend auf Performance
        avg_score = performance_summary["average_score"]
        if avg_score < 0.6:
            recommendations.append("Systematische Verbesserung der Prompt-Templates erforderlich")
        
        # Segment-spezifische Empfehlungen
        for segment, result in matrix_results.items():
            evaluation = result["evaluation"]
            
            if evaluation["overall_score"] < 0.5:
                recommendations.append(f"Segment '{segment}' benötigt dringende Optimierung")
            
            if evaluation["genre_compliance"] < 0.5:
                recommendations.append(f"Genre-Compliance für '{segment}' verbessern")
            
            if evaluation["age_appropriateness"] < 0.7:
                recommendations.append(f"Altersgerechtheit für '{segment}' überprüfen")
        
        # A/B-Test Empfehlungen
        ab_results = results.get("ab_test_results", {})
        for segment, ab_result in ab_results.items():
            if ab_result["comparison"]["significant_improvement"]:
                recommendations.append(f"Optimierte Version für '{segment}' übernehmen")
        
        return recommendations

def main():
    """Beispiel für skalierbare Test-Matrix"""
    test_matrix = ScalableTestMatrix()
    
    # Führe komplette Test-Matrix durch
    results = test_matrix.run_complete_test_matrix(enable_ab_testing=True)
    
    # Zeige Ergebnisse
    print("\n" + "="*60)
    print("SKALIERBARE TEST-MATRIX ERGEBNISSE")
    print("="*60)
    
    # Performance-Summary
    performance = results["performance_summary"]
    print(f"Durchschnittlicher Score: {performance['average_score']:.3f}")
    print(f"Anzahl Segmente: {performance['total_segments']}")
    
    print("\nTop-Performer:")
    for i, performer in enumerate(performance["top_performers"], 1):
        print(f"{i}. {performer['segment']}: {performer['score']:.3f}")
    
    # A/B-Test Ergebnisse
    ab_results = results.get("ab_test_results", {})
    if ab_results:
        print("\nA/B-Test Ergebnisse:")
        for segment, ab_result in ab_results.items():
            comparison = ab_result["comparison"]
            print(f"• {segment}: {comparison['improvement_percentage']:+.1f}% Verbesserung")
    
    # Empfehlungen
    if results["recommendations"]:
        print("\nEmpfehlungen:")
        for rec in results["recommendations"]:
            print(f"• {rec}")
    
    print("="*60)

if __name__ == "__main__":
    main() 