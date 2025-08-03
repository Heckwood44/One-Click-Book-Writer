#!/usr/bin/env python3
"""
User Feedback System
Sammelt und analysiert Nutzerfeedback für Prompt-Optimierung
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserFeedbackSystem:
    """Sammelt und analysiert Nutzerfeedback"""
    
    def __init__(self, feedback_file: str = "user_feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict:
        """Lädt bestehende Feedback-Daten"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Feedback-Daten: {e}")
        
        return {
            "feedback_entries": [],
            "statistics": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "total_entries": 0
            }
        }
    
    def _save_feedback(self):
        """Speichert Feedback-Daten"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Feedback-Daten gespeichert: {self.feedback_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Feedback-Daten: {e}")
    
    def collect_feedback(self, 
                        chapter_number: int,
                        prompt_hash: str,
                        quality_score: float,
                        language: str,
                        rating: int,
                        comment: str,
                        metadata: Optional[Dict] = None) -> bool:
        """
        Sammelt Nutzerfeedback
        
        Args:
            chapter_number: Kapitelnummer
            prompt_hash: Hash des verwendeten Prompts
            quality_score: Automatischer Qualitäts-Score
            language: Sprache (de/en)
            rating: Nutzer-Rating (1-5 Sterne)
            comment: Freitext-Kommentar
            metadata: Zusätzliche Metadaten
        """
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "chapter_number": chapter_number,
                "prompt_hash": prompt_hash,
                "quality_score": quality_score,
                "language": language,
                "user_rating": rating,
                "user_comment": comment,
                "metadata": metadata or {}
            }
            
            self.feedback_data["feedback_entries"].append(feedback_entry)
            self.feedback_data["metadata"]["total_entries"] = len(self.feedback_data["feedback_entries"])
            
            # Aktualisiere Statistiken
            self._update_statistics()
            
            # Speichere Feedback
            self._save_feedback()
            
            logger.info(f"Feedback gesammelt: Kapitel {chapter_number}, Rating {rating}/5")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von Feedback: {e}")
            return False
    
    def _update_statistics(self):
        """Aktualisiert Feedback-Statistiken"""
        entries = self.feedback_data["feedback_entries"]
        
        if not entries:
            return
        
        # Grundlegende Statistiken
        ratings = [entry["user_rating"] for entry in entries]
        quality_scores = [entry["quality_score"] for entry in entries]
        
        # Prompt-Hash Statistiken
        prompt_hashes = {}
        for entry in entries:
            hash_val = entry["prompt_hash"]
            if hash_val not in prompt_hashes:
                prompt_hashes[hash_val] = {
                    "count": 0,
                    "ratings": [],
                    "quality_scores": []
                }
            prompt_hashes[hash_val]["count"] += 1
            prompt_hashes[hash_val]["ratings"].append(entry["user_rating"])
            prompt_hashes[hash_val]["quality_scores"].append(entry["quality_score"])
        
        # Berechne Durchschnitte für jeden Hash
        for hash_val, data in prompt_hashes.items():
            data["avg_rating"] = statistics.mean(data["ratings"])
            data["avg_quality_score"] = statistics.mean(data["quality_scores"])
            data["rating_std"] = statistics.stdev(data["ratings"]) if len(data["ratings"]) > 1 else 0
            data["quality_std"] = statistics.stdev(data["quality_scores"]) if len(data["quality_scores"]) > 1 else 0
        
        self.feedback_data["statistics"] = {
            "overall": {
                "total_entries": len(entries),
                "avg_rating": statistics.mean(ratings),
                "avg_quality_score": statistics.mean(quality_scores),
                "rating_std": statistics.stdev(ratings) if len(ratings) > 1 else 0,
                "quality_std": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            },
            "by_prompt_hash": prompt_hashes,
            "last_updated": datetime.now().isoformat()
        }
    
    def analyze_correlations(self) -> Dict:
        """Analysiert Korrelationen zwischen automatischen Scores und Nutzer-Ratings"""
        entries = self.feedback_data["feedback_entries"]
        
        if len(entries) < 2:
            return {"error": "Nicht genügend Daten für Korrelationsanalyse"}
        
        # Berechne Korrelation zwischen Quality Score und User Rating
        quality_scores = [entry["quality_score"] for entry in entries]
        user_ratings = [entry["user_rating"] for entry in entries]
        
        # Einfache Korrelationsberechnung (Pearson-ähnlich)
        n = len(quality_scores)
        if n > 1:
            mean_quality = statistics.mean(quality_scores)
            mean_rating = statistics.mean(user_ratings)
            
            numerator = sum((q - mean_quality) * (r - mean_rating) for q, r in zip(quality_scores, user_ratings))
            denominator_quality = sum((q - mean_quality) ** 2 for q in quality_scores)
            denominator_rating = sum((r - mean_rating) ** 2 for r in user_ratings)
            
            if denominator_quality > 0 and denominator_rating > 0:
                correlation = numerator / (denominator_quality * denominator_rating) ** 0.5
            else:
                correlation = 0
        else:
            correlation = 0
        
        # Analysiere Divergenzen
        divergences = []
        for entry in entries:
            quality_score = entry["quality_score"]
            user_rating = entry["user_rating"]
            
            # Normalisiere auf 0-1 Skala für Vergleich
            normalized_quality = quality_score
            normalized_rating = (user_rating - 1) / 4  # 1-5 -> 0-1
            
            divergence = abs(normalized_quality - normalized_rating)
            divergences.append({
                "entry_id": len(divergences),
                "prompt_hash": entry["prompt_hash"],
                "chapter_number": entry["chapter_number"],
                "quality_score": quality_score,
                "user_rating": user_rating,
                "divergence": divergence,
                "comment": entry["user_comment"]
            })
        
        # Sortiere nach Divergenz (höchste zuerst)
        divergences.sort(key=lambda x: x["divergence"], reverse=True)
        
        return {
            "correlation_quality_vs_rating": correlation,
            "correlation_interpretation": self._interpret_correlation(correlation),
            "top_divergences": divergences[:5],  # Top 5 Divergenzen
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpretiert Korrelationswert"""
        if abs(correlation) >= 0.8:
            return "Sehr starke Korrelation"
        elif abs(correlation) >= 0.6:
            return "Starke Korrelation"
        elif abs(correlation) >= 0.4:
            return "Mittlere Korrelation"
        elif abs(correlation) >= 0.2:
            return "Schwache Korrelation"
        else:
            return "Keine nennenswerte Korrelation"
    
    def get_best_performing_prompts(self, min_entries: int = 2) -> List[Dict]:
        """Identifiziert die besten Prompt-Varianten basierend auf Feedback"""
        stats = self.feedback_data["statistics"]
        
        if "by_prompt_hash" not in stats:
            return []
        
        best_prompts = []
        
        for prompt_hash, data in stats["by_prompt_hash"].items():
            if data["count"] >= min_entries:
                # Kombiniere Rating und Quality Score für Gesamtbewertung
                combined_score = (data["avg_rating"] * 0.6 + data["avg_quality_score"] * 0.4)
                
                best_prompts.append({
                    "prompt_hash": prompt_hash,
                    "entry_count": data["count"],
                    "avg_rating": data["avg_rating"],
                    "avg_quality_score": data["avg_quality_score"],
                    "combined_score": combined_score,
                    "rating_std": data["rating_std"],
                    "quality_std": data["quality_std"]
                })
        
        # Sortiere nach kombinierter Bewertung
        best_prompts.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return best_prompts
    
    def generate_feedback_summary(self) -> Dict:
        """Generiert Zusammenfassung des Feedbacks"""
        stats = self.feedback_data["statistics"]
        correlations = self.analyze_correlations()
        best_prompts = self.get_best_performing_prompts()
        
        return {
            "summary_timestamp": datetime.now().isoformat(),
            "total_feedback_entries": self.feedback_data["metadata"]["total_entries"],
            "overall_statistics": stats.get("overall", {}),
            "correlation_analysis": correlations,
            "best_performing_prompts": best_prompts[:3],  # Top 3
            "recommendations": self._generate_recommendations(correlations, best_prompts)
        }
    
    def _generate_recommendations(self, correlations: Dict, best_prompts: List[Dict]) -> List[str]:
        """Generiert Empfehlungen basierend auf Feedback-Analyse"""
        recommendations = []
        
        # Korrelations-basierte Empfehlungen
        correlation = correlations.get("correlation_quality_vs_rating", 0)
        if abs(correlation) < 0.4:
            recommendations.append("Automatische Quality-Scores stimmen nicht gut mit Nutzer-Ratings überein - Quality-Evaluator überprüfen")
        
        # Prompt-basierte Empfehlungen
        if best_prompts:
            top_prompt = best_prompts[0]
            recommendations.append(f"Beste Prompt-Variante: {top_prompt['prompt_hash']} (Score: {top_prompt['combined_score']:.2f})")
        
        # Divergenz-basierte Empfehlungen
        top_divergences = correlations.get("top_divergences", [])
        if top_divergences:
            recommendations.append(f"Größte Divergenz: Kapitel {top_divergences[0]['chapter_number']} (Quality: {top_divergences[0]['quality_score']:.2f}, Rating: {top_divergences[0]['user_rating']}/5)")
        
        return recommendations

def main():
    """Beispiel für Feedback-System"""
    feedback_system = UserFeedbackSystem()
    
    # Beispiel-Feedback sammeln
    feedback_system.collect_feedback(
        chapter_number=1,
        prompt_hash="998fa1af57e8a3cd",
        quality_score=0.607,
        language="de",
        rating=4,
        comment="Gute Geschichte, aber könnte mehr Dialoge haben"
    )
    
    feedback_system.collect_feedback(
        chapter_number=1,
        prompt_hash="998fa1af57e8a3cd",
        quality_score=0.607,
        language="en",
        rating=3,
        comment="English version feels a bit flat compared to German"
    )
    
    # Feedback-Analyse
    summary = feedback_system.generate_feedback_summary()
    
    print("\n" + "="*60)
    print("FEEDBACK-SYSTEM ZUSAMMENFASSUNG")
    print("="*60)
    print(f"Gesamte Feedback-Einträge: {summary['total_feedback_entries']}")
    print(f"Durchschnittliches Rating: {summary['overall_statistics'].get('avg_rating', 0):.2f}/5")
    print(f"Durchschnittlicher Quality-Score: {summary['overall_statistics'].get('avg_quality_score', 0):.3f}")
    print(f"Korrelation Quality vs Rating: {summary['correlation_analysis'].get('correlation_quality_vs_rating', 0):.3f}")
    
    if summary['best_performing_prompts']:
        best = summary['best_performing_prompts'][0]
        print(f"Beste Prompt-Variante: {best['prompt_hash']} (Score: {best['combined_score']:.2f})")
    
    print("\nEmpfehlungen:")
    for rec in summary['recommendations']:
        print(f"• {rec}")
    print("="*60)

if __name__ == "__main__":
    main() 