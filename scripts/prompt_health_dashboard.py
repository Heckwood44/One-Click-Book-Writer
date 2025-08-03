#!/usr/bin/env python3
"""
Prompt Health Dashboard
Überwachung und Empfehlungen für Prompt-Templates und Qualitätsmetriken
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics

import sys
sys.path.append(str(Path(__file__).parent.parent))

from compiler.modular_prompt_templates import PromptTemplateManager
from scripts.user_feedback_system import UserFeedbackSystem
from utils.constraint_checker import ConstraintChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptHealthDashboard:
    """Dashboard für Prompt-Gesundheit und Performance-Überwachung"""
    
    def __init__(self):
        self.template_manager = PromptTemplateManager()
        self.feedback_system = UserFeedbackSystem()
        self.constraint_checker = ConstraintChecker()
    
    def generate_health_report(self) -> Dict:
        """Generiert vollständigen Health-Report"""
        try:
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "template_health": self._analyze_template_health(),
                "performance_metrics": self._analyze_performance_metrics(),
                "feedback_analysis": self._analyze_feedback_health(),
                "diversity_metrics": self._analyze_diversity_metrics(),
                "cost_analysis": self._analyze_cost_metrics(),
                "recommendations": [],
                "overall_health_score": 0.0
            }
            
            # Generiere Empfehlungen
            report["recommendations"] = self._generate_health_recommendations(report)
            
            # Berechne Gesamt-Gesundheits-Score
            report["overall_health_score"] = self._calculate_overall_health_score(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Fehler bei Health-Report-Generierung: {e}")
            return {"error": str(e)}
    
    def _analyze_template_health(self) -> Dict:
        """Analysiert Gesundheit der Prompt-Templates"""
        templates = self.template_manager.templates
        
        if not templates:
            return {"status": "no_templates", "message": "Keine Templates verfügbar"}
        
        template_analysis = {
            "total_templates": len(templates),
            "active_templates": 0,
            "template_versions": {},
            "layer_health": {},
            "performance_distribution": {}
        }
        
        # Analysiere Template-Versionen
        for template_id, template in templates.items():
            # Aktive Templates (mit Performance-Daten)
            if template.performance_metrics:
                template_analysis["active_templates"] += 1
            
            # Version-Tracking
            version = template.version
            if version not in template_analysis["template_versions"]:
                template_analysis["template_versions"][version] = 0
            template_analysis["template_versions"][version] += 1
            
            # Layer-Gesundheit
            for layer_type, layer in template.layers.items():
                if layer_type not in template_analysis["layer_health"]:
                    template_analysis["layer_health"][layer_type] = {
                        "count": 0,
                        "avg_weight": 0.0,
                        "weight_distribution": []
                    }
                
                layer_health = template_analysis["layer_health"][layer_type]
                layer_health["count"] += 1
                layer_health["weight_distribution"].append(layer.weight)
            
            # Performance-Verteilung
            if template.performance_metrics:
                quality_score = template.performance_metrics.get("quality_score", 0)
                if "quality_scores" not in template_analysis["performance_distribution"]:
                    template_analysis["performance_distribution"]["quality_scores"] = []
                template_analysis["performance_distribution"]["quality_scores"].append(quality_score)
        
        # Berechne Durchschnitte für Layer-Gesundheit
        for layer_type, health_data in template_analysis["layer_health"].items():
            if health_data["weight_distribution"]:
                health_data["avg_weight"] = statistics.mean(health_data["weight_distribution"])
        
        # Performance-Statistiken
        quality_scores = template_analysis["performance_distribution"].get("quality_scores", [])
        if quality_scores:
            template_analysis["performance_distribution"]["stats"] = {
                "mean": statistics.mean(quality_scores),
                "median": statistics.median(quality_scores),
                "std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
                "min": min(quality_scores),
                "max": max(quality_scores)
            }
        
        return template_analysis
    
    def _analyze_performance_metrics(self) -> Dict:
        """Analysiert Performance-Metriken"""
        templates = self.template_manager.templates
        
        if not templates:
            return {"status": "no_data", "message": "Keine Performance-Daten verfügbar"}
        
        performance_data = {
            "quality_score_trends": [],
            "response_length_analysis": {},
            "constraint_violations": {},
            "retry_rates": {},
            "improvement_deltas": []
        }
        
        # Sammle Performance-Daten
        for template in templates.values():
            if template.performance_metrics:
                metrics = template.performance_metrics
                
                # Quality Score Trends
                if "quality_score" in metrics:
                    performance_data["quality_score_trends"].append({
                        "template_id": template.template_id,
                        "quality_score": metrics["quality_score"],
                        "timestamp": template.created_at
                    })
                
                # Response Length Analysis
                if "response_length" in metrics:
                    length = metrics["response_length"]
                    if "lengths" not in performance_data["response_length_analysis"]:
                        performance_data["response_length_analysis"]["lengths"] = []
                    performance_data["response_length_analysis"]["lengths"].append(length)
                
                # Constraint Violations
                if "constraint_violations" in metrics:
                    violations = metrics["constraint_violations"]
                    for violation_type, count in violations.items():
                        if violation_type not in performance_data["constraint_violations"]:
                            performance_data["constraint_violations"][violation_type] = 0
                        performance_data["constraint_violations"][violation_type] += count
                
                # Retry Rates
                if "retry_count" in metrics:
                    retry_count = metrics["retry_count"]
                    if "retry_counts" not in performance_data["retry_rates"]:
                        performance_data["retry_rates"]["retry_counts"] = []
                    performance_data["retry_rates"]["retry_counts"].append(retry_count)
                
                # Improvement Deltas
                if "improvement_delta" in metrics:
                    performance_data["improvement_deltas"].append(metrics["improvement_delta"])
        
        # Berechne Statistiken
        if performance_data["quality_score_trends"]:
            scores = [t["quality_score"] for t in performance_data["quality_score_trends"]]
            performance_data["quality_score_stats"] = {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std": statistics.stdev(scores) if len(scores) > 1 else 0
            }
        
        if performance_data["response_length_analysis"].get("lengths"):
            lengths = performance_data["response_length_analysis"]["lengths"]
            performance_data["response_length_analysis"]["stats"] = {
                "mean": statistics.mean(lengths),
                "median": statistics.median(lengths),
                "std": statistics.stdev(lengths) if len(lengths) > 1 else 0
            }
        
        if performance_data["retry_rates"].get("retry_counts"):
            retry_counts = performance_data["retry_rates"]["retry_counts"]
            performance_data["retry_rates"]["stats"] = {
                "mean": statistics.mean(retry_counts),
                "total_retries": sum(retry_counts),
                "retry_rate": sum(retry_counts) / len(retry_counts) if retry_counts else 0
            }
        
        return performance_data
    
    def _analyze_feedback_health(self) -> Dict:
        """Analysiert Feedback-Gesundheit"""
        feedback_data = self.feedback_system.feedback_data
        
        if not feedback_data.get("feedback_entries"):
            return {"status": "no_feedback", "message": "Kein Feedback verfügbar"}
        
        feedback_analysis = {
            "total_feedback_entries": len(feedback_data["feedback_entries"]),
            "rating_distribution": {},
            "correlation_analysis": {},
            "feedback_trends": [],
            "prompt_performance_correlation": {}
        }
        
        # Rating-Verteilung
        ratings = [entry["user_rating"] for entry in feedback_data["feedback_entries"]]
        for rating in ratings:
            if rating not in feedback_analysis["rating_distribution"]:
                feedback_analysis["rating_distribution"][rating] = 0
            feedback_analysis["rating_distribution"][rating] += 1
        
        # Korrelationsanalyse
        correlations = self.feedback_system.analyze_correlations()
        feedback_analysis["correlation_analysis"] = correlations
        
        # Feedback-Trends
        for entry in feedback_data["feedback_entries"]:
            feedback_analysis["feedback_trends"].append({
                "timestamp": entry["timestamp"],
                "rating": entry["user_rating"],
                "quality_score": entry["quality_score"],
                "prompt_hash": entry["prompt_hash"]
            })
        
        # Prompt-Performance-Korrelation
        prompt_ratings = {}
        for entry in feedback_data["feedback_entries"]:
            prompt_hash = entry["prompt_hash"]
            if prompt_hash not in prompt_ratings:
                prompt_ratings[prompt_hash] = {"ratings": [], "quality_scores": []}
            
            prompt_ratings[prompt_hash]["ratings"].append(entry["user_rating"])
            prompt_ratings[prompt_hash]["quality_scores"].append(entry["quality_score"])
        
        for prompt_hash, data in prompt_ratings.items():
            if data["ratings"] and data["quality_scores"]:
                avg_rating = statistics.mean(data["ratings"])
                avg_quality = statistics.mean(data["quality_scores"])
                feedback_analysis["prompt_performance_correlation"][prompt_hash] = {
                    "avg_rating": avg_rating,
                    "avg_quality_score": avg_quality,
                    "correlation_delta": avg_rating - (avg_quality * 5)  # Normalisiert auf 1-5 Skala
                }
        
        return feedback_analysis
    
    def _analyze_diversity_metrics(self) -> Dict:
        """Analysiert Diversity-Metriken"""
        templates = self.template_manager.templates
        
        if not templates:
            return {"status": "no_templates", "message": "Keine Templates für Diversity-Analyse"}
        
        diversity_analysis = {
            "lexical_variety": {},
            "layer_diversity": {},
            "prompt_structure_variety": {},
            "emotional_diversity": {}
        }
        
        # Lexical Variety
        all_prompts = []
        for template in templates.values():
            prompt = template.compile_prompt("de")
            all_prompts.append(prompt)
        
        if all_prompts:
            # Einfache Lexical Variety Berechnung
            all_words = []
            for prompt in all_prompts:
                words = prompt.lower().split()
                all_words.extend(words)
            
            unique_words = set(all_words)
            diversity_analysis["lexical_variety"] = {
                "total_words": len(all_words),
                "unique_words": len(unique_words),
                "lexical_diversity": len(unique_words) / max(len(all_words), 1),
                "vocabulary_size": len(unique_words)
            }
        
        # Layer Diversity
        layer_types = set()
        layer_weights = {}
        
        for template in templates.values():
            for layer_type, layer in template.layers.items():
                layer_types.add(layer_type)
                if layer_type not in layer_weights:
                    layer_weights[layer_type] = []
                layer_weights[layer_type].append(layer.weight)
        
        diversity_analysis["layer_diversity"] = {
            "unique_layer_types": len(layer_types),
            "layer_weight_variation": {}
        }
        
        for layer_type, weights in layer_weights.items():
            if len(weights) > 1:
                diversity_analysis["layer_diversity"]["layer_weight_variation"][layer_type] = {
                    "std": statistics.stdev(weights),
                    "cv": statistics.stdev(weights) / statistics.mean(weights)  # Coefficient of Variation
                }
        
        # Prompt Structure Variety
        structure_patterns = {}
        for template in templates.values():
            layer_count = len(template.layers)
            if layer_count not in structure_patterns:
                structure_patterns[layer_count] = 0
            structure_patterns[layer_count] += 1
        
        diversity_analysis["prompt_structure_variety"] = {
            "structure_distribution": structure_patterns,
            "structure_entropy": self._calculate_entropy(list(structure_patterns.values()))
        }
        
        return diversity_analysis
    
    def _analyze_cost_metrics(self) -> Dict:
        """Analysiert Kosten-Metriken"""
        # Vereinfachte Kosten-Analyse
        cost_analysis = {
            "estimated_tokens_used": 0,
            "estimated_cost_per_chapter": 0.0,
            "cost_trends": [],
            "optimization_cost_benefit": {}
        }
        
        # Schätze Token-Verbrauch basierend auf Template-Anzahl
        templates = self.template_manager.templates
        if templates:
            avg_prompt_length = 0
            for template in templates.values():
                prompt = template.compile_prompt("de")
                avg_prompt_length += len(prompt)
            
            avg_prompt_length /= len(templates)
            cost_analysis["estimated_tokens_used"] = int(avg_prompt_length * len(templates))
            cost_analysis["estimated_cost_per_chapter"] = (avg_prompt_length / 1000) * 0.03  # Grobe Schätzung
        
        return cost_analysis
    
    def _calculate_entropy(self, values: List[int]) -> float:
        """Berechnet Entropie für Diversity-Metriken"""
        if not values or sum(values) == 0:
            return 0.0
        
        total = sum(values)
        entropy = 0.0
        
        for value in values:
            if value > 0:
                p = value / total
                entropy -= p * (p.bit_length() - 1)  # Vereinfachte Entropie
        
        return entropy
    
    def _generate_health_recommendations(self, report: Dict) -> List[str]:
        """Generiert Health-Empfehlungen"""
        recommendations = []
        
        # Template-Gesundheit
        template_health = report.get("template_health", {})
        if template_health.get("active_templates", 0) < 2:
            recommendations.append("Mehr aktive Templates erstellen - Diversität erhöhen")
        
        # Performance-Metriken
        performance = report.get("performance_metrics", {})
        if performance.get("quality_score_stats", {}).get("mean", 0) < 0.7:
            recommendations.append("Qualitäts-Scores verbessern - Template-Optimierung erforderlich")
        
        # Feedback-Analyse
        feedback = report.get("feedback_analysis", {})
        correlation = feedback.get("correlation_analysis", {}).get("correlation_quality_vs_rating", 0)
        if abs(correlation) < 0.4:
            recommendations.append("Quality-Evaluator anpassen - Korrelation mit Nutzer-Ratings verbessern")
        
        # Diversity-Metriken
        diversity = report.get("diversity_metrics", {})
        lexical_diversity = diversity.get("lexical_variety", {}).get("lexical_diversity", 0)
        if lexical_diversity < 0.3:
            recommendations.append("Lexical Variety erhöhen - Prompt-Variation verstärken")
        
        # Retry-Raten
        retry_stats = performance.get("retry_rates", {}).get("stats", {})
        if retry_stats.get("retry_rate", 0) > 0.3:
            recommendations.append("Retry-Rate reduzieren - Template-Qualität verbessern")
        
        # Constraint-Verletzungen
        violations = performance.get("constraint_violations", {})
        if violations:
            recommendations.append("Constraint-Verletzungen reduzieren - Template-Validierung verstärken")
        
        return recommendations
    
    def _calculate_overall_health_score(self, report: Dict) -> float:
        """Berechnet Gesamt-Gesundheits-Score"""
        score = 0.0
        factors = 0
        
        # Template-Gesundheit (30%)
        template_health = report.get("template_health", {})
        if template_health.get("active_templates", 0) > 0:
            active_ratio = min(template_health["active_templates"] / template_health["total_templates"], 1.0)
            score += active_ratio * 0.3
            factors += 1
        
        # Performance (25%)
        performance = report.get("performance_metrics", {})
        quality_stats = performance.get("quality_score_stats", {})
        if quality_stats.get("mean", 0) > 0:
            quality_score = min(quality_stats["mean"], 1.0)
            score += quality_score * 0.25
            factors += 1
        
        # Feedback-Korrelation (20%)
        feedback = report.get("feedback_analysis", {})
        correlation = abs(feedback.get("correlation_analysis", {}).get("correlation_quality_vs_rating", 0))
        score += correlation * 0.2
        factors += 1
        
        # Diversity (15%)
        diversity = report.get("diversity_metrics", {})
        lexical_diversity = diversity.get("lexical_variety", {}).get("lexical_diversity", 0)
        score += min(lexical_diversity, 1.0) * 0.15
        factors += 1
        
        # Retry-Rate (10%)
        performance = report.get("performance_metrics", {})
        retry_stats = performance.get("retry_rates", {}).get("stats", {})
        retry_rate = retry_stats.get("retry_rate", 0)
        retry_score = max(0, 1 - retry_rate)
        score += retry_score * 0.1
        factors += 1
        
        return score / max(factors, 1)
    
    def save_health_report(self, report: Dict, filename: str = None) -> str:
        """Speichert Health-Report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/prompt_health_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Health-Report gespeichert: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Health-Reports: {e}")
            return ""

def main():
    """Beispiel für Prompt-Health-Dashboard"""
    dashboard = PromptHealthDashboard()
    
    # Erstelle Standard-Template falls nicht vorhanden
    if not dashboard.template_manager.get_template("children_book_v1"):
        dashboard.template_manager.create_default_children_book_template()
        dashboard.template_manager.save_templates()
    
    # Generiere Health-Report
    report = dashboard.generate_health_report()
    
    if "error" not in report:
        print("\n" + "="*60)
        print("PROMPT-HEALTH-DASHBOARD")
        print("="*60)
        
        print(f"Gesundheits-Score: {report['overall_health_score']:.2f}/1.0")
        
        # Template-Gesundheit
        template_health = report.get("template_health", {})
        print(f"Templates: {template_health.get('total_templates', 0)} total, {template_health.get('active_templates', 0)} aktiv")
        
        # Performance
        performance = report.get("performance_metrics", {})
        quality_stats = performance.get("quality_score_stats", {})
        if quality_stats:
            print(f"Durchschnittlicher Quality-Score: {quality_stats.get('mean', 0):.3f}")
        
        # Feedback
        feedback = report.get("feedback_analysis", {})
        print(f"Feedback-Einträge: {feedback.get('total_feedback_entries', 0)}")
        
        # Diversity
        diversity = report.get("diversity_metrics", {})
        lexical_diversity = diversity.get("lexical_variety", {}).get("lexical_diversity", 0)
        print(f"Lexical Diversity: {lexical_diversity:.3f}")
        
        print("\nEmpfehlungen:")
        for rec in report.get("recommendations", []):
            print(f"• {rec}")
        
        # Speichere Report
        filename = dashboard.save_health_report(report)
        if filename:
            print(f"\nReport gespeichert: {filename}")
        
        print("="*60)
    else:
        print(f"Fehler beim Health-Report: {report['error']}")

if __name__ == "__main__":
    main() 