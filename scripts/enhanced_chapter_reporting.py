#!/usr/bin/env python3
"""
Enhanced Chapter Reporting System
Integriert A/B-Test-Ergebnisse und Nutzerfeedback in Kapitel-Reports
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from user_feedback_system import UserFeedbackSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedChapterReporting:
    """Erweitertes Kapitel-Reporting mit A/B-Tests und Feedback"""
    
    def __init__(self):
        self.feedback_system = UserFeedbackSystem()
    
    def generate_enhanced_report(self, 
                                chapter_number: int,
                                ab_test_results: Optional[Dict] = None,
                                include_feedback: bool = True) -> Dict:
        """
        Generiert erweiterten Kapitel-Report
        
        Args:
            chapter_number: Kapitelnummer
            ab_test_results: Ergebnisse aus A/B-Test (optional)
            include_feedback: Ob Feedback-Analyse eingeschlossen werden soll
        """
        try:
            # Lade bestehende Meta-Daten
            meta_file = f"output/chapter_{chapter_number}_meta.json"
            if Path(meta_file).exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    chapter_metadata = json.load(f)
            else:
                chapter_metadata = {}
            
            # Basis-Report
            enhanced_report = {
                "report_timestamp": datetime.now().isoformat(),
                "chapter_number": chapter_number,
                "base_metadata": chapter_metadata,
                "ab_test_analysis": {},
                "feedback_analysis": {},
                "recommendations": []
            }
            
            # A/B-Test-Analyse
            if ab_test_results:
                enhanced_report["ab_test_analysis"] = self._analyze_ab_test_results(ab_test_results)
            
            # Feedback-Analyse
            if include_feedback:
                enhanced_report["feedback_analysis"] = self._analyze_feedback_for_chapter(chapter_number)
            
            # Empfehlungen generieren
            enhanced_report["recommendations"] = self._generate_enhanced_recommendations(
                enhanced_report["ab_test_analysis"],
                enhanced_report["feedback_analysis"]
            )
            
            # Report speichern
            report_file = f"output/enhanced_report_chapter_{chapter_number}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Erweiterter Report generiert: {report_file}")
            return enhanced_report
            
        except Exception as e:
            logger.error(f"Fehler beim Generieren des erweiterten Reports: {e}")
            return {"error": str(e)}
    
    def _analyze_ab_test_results(self, ab_test_results: Dict) -> Dict:
        """Analysiert A/B-Test-Ergebnisse"""
        try:
            quality_comparison = ab_test_results.get("quality_comparison", {})
            improvement = quality_comparison.get("improvement", {})
            prompt_diff = ab_test_results.get("prompt_diff", {})
            
            analysis = {
                "prompt_hashes": ab_test_results.get("prompt_hashes", {}),
                "quality_improvement": {
                    "score_delta": improvement.get("score_delta", 0),
                    "percentage_improvement": improvement.get("percentage_improvement", 0),
                    "interpretation": self._interpret_improvement(improvement.get("score_delta", 0))
                },
                "prompt_changes": {
                    "total_changes": prompt_diff.get("changes", {}).get("total_changes", 0),
                    "length_change": prompt_diff.get("length_change", 0),
                    "change_ratio": prompt_diff.get("length_change", 0) / max(prompt_diff.get("raw_length", 1), 1)
                },
                "key_improvements": self._extract_key_improvements(prompt_diff),
                "recommendation": self._get_ab_test_recommendation(improvement.get("score_delta", 0))
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Fehler bei A/B-Test-Analyse: {e}")
            return {"error": str(e)}
    
    def _interpret_improvement(self, score_delta: float) -> str:
        """Interpretiert Qualitätsverbesserung"""
        if score_delta >= 0.2:
            return "Signifikante Verbesserung"
        elif score_delta >= 0.1:
            return "Deutliche Verbesserung"
        elif score_delta >= 0.05:
            return "Leichte Verbesserung"
        elif score_delta >= -0.05:
            return "Keine nennenswerte Änderung"
        elif score_delta >= -0.1:
            return "Leichte Verschlechterung"
        else:
            return "Deutliche Verschlechterung"
    
    def _extract_key_improvements(self, prompt_diff: Dict) -> List[str]:
        """Extrahiert wichtige Verbesserungen aus Prompt-Diff"""
        improvements = []
        
        try:
            changes = prompt_diff.get("changes", {})
            added_lines = changes.get("added_lines", [])
            
            # Analysiere hinzugefügte Zeilen
            for line in added_lines:
                line_lower = line.lower()
                if "emotion" in line_lower or "gefühle" in line_lower:
                    improvements.append("Emotionale Tiefe verstärkt")
                elif "dialog" in line_lower or "gespräch" in line_lower:
                    improvements.append("Dialog-Anweisungen hinzugefügt")
                elif "beschreibung" in line_lower or "description" in line_lower:
                    improvements.append("Beschreibungsanweisungen erweitert")
                elif "bildhaft" in line_lower or "metaphor" in line_lower:
                    improvements.append("Bildhafte Sprache verstärkt")
                elif "kohärenz" in line_lower or "consistency" in line_lower:
                    improvements.append("Bilinguale Kohärenz verbessert")
            
            # Entferne Duplikate
            improvements = list(set(improvements))
            
        except Exception as e:
            logger.error(f"Fehler beim Extrahieren von Verbesserungen: {e}")
        
        return improvements
    
    def _get_ab_test_recommendation(self, score_delta: float) -> str:
        """Generiert Empfehlung basierend auf A/B-Test-Ergebnis"""
        if score_delta >= 0.1:
            return "Optimierte Prompt-Version übernehmen"
        elif score_delta >= 0.05:
            return "Optimierte Version weiter testen"
        elif score_delta >= -0.05:
            return "Beide Versionen sind vergleichbar"
        else:
            return "Rohe Version beibehalten, Optimierung überarbeiten"
    
    def _analyze_feedback_for_chapter(self, chapter_number: int) -> Dict:
        """Analysiert Feedback für spezifisches Kapitel"""
        try:
            # Lade Feedback-Daten
            feedback_data = self.feedback_system.feedback_data
            
            # Filtere Feedback für dieses Kapitel
            chapter_feedback = [
                entry for entry in feedback_data.get("feedback_entries", [])
                if entry.get("chapter_number") == chapter_number
            ]
            
            if not chapter_feedback:
                return {"message": "Kein Feedback für dieses Kapitel verfügbar"}
            
            # Analysiere Kapitel-spezifisches Feedback
            ratings = [entry["user_rating"] for entry in chapter_feedback]
            quality_scores = [entry["quality_score"] for entry in chapter_feedback]
            comments = [entry["user_comment"] for entry in chapter_feedback]
            
            # Gruppiere nach Prompt-Hash
            hash_groups = {}
            for entry in chapter_feedback:
                hash_val = entry["prompt_hash"]
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(entry)
            
            analysis = {
                "total_feedback_entries": len(chapter_feedback),
                "average_rating": sum(ratings) / len(ratings) if ratings else 0,
                "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                "feedback_by_prompt_hash": {},
                "common_themes": self._extract_common_themes(comments),
                "rating_distribution": self._calculate_rating_distribution(ratings)
            }
            
            # Analysiere Feedback nach Prompt-Hash
            for hash_val, entries in hash_groups.items():
                hash_ratings = [entry["user_rating"] for entry in entries]
                hash_quality_scores = [entry["quality_score"] for entry in entries]
                
                analysis["feedback_by_prompt_hash"][hash_val] = {
                    "entry_count": len(entries),
                    "average_rating": sum(hash_ratings) / len(hash_ratings),
                    "average_quality_score": sum(hash_quality_scores) / len(hash_quality_scores),
                    "comments": [entry["user_comment"] for entry in entries]
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Fehler bei Feedback-Analyse: {e}")
            return {"error": str(e)}
    
    def _extract_common_themes(self, comments: List[str]) -> List[str]:
        """Extrahiert häufige Themen aus Kommentaren"""
        themes = []
        
        # Einfache Schlüsselwort-Analyse
        keywords = {
            "dialog": ["dialog", "gespräch", "sprechen", "conversation"],
            "emotion": ["emotion", "gefühle", "feeling", "herz"],
            "description": ["beschreibung", "description", "detail", "detailreich"],
            "length": ["länge", "length", "kurz", "short", "lang", "long"],
            "style": ["stil", "style", "schreibstil", "writing style"],
            "plot": ["handlung", "plot", "story", "geschichte"]
        }
        
        for theme, words in keywords.items():
            count = sum(1 for comment in comments 
                       if any(word in comment.lower() for word in words))
            if count > 0:
                themes.append(f"{theme}: {count} Erwähnungen")
        
        return themes
    
    def _calculate_rating_distribution(self, ratings: List[int]) -> Dict:
        """Berechnet Verteilung der Ratings"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for rating in ratings:
            if rating in distribution:
                distribution[rating] += 1
        
        return distribution
    
    def _generate_enhanced_recommendations(self, 
                                         ab_test_analysis: Dict, 
                                         feedback_analysis: Dict) -> List[str]:
        """Generiert erweiterte Empfehlungen"""
        recommendations = []
        
        # A/B-Test-basierte Empfehlungen
        if "recommendation" in ab_test_analysis:
            recommendations.append(f"A/B-Test: {ab_test_analysis['recommendation']}")
        
        if "quality_improvement" in ab_test_analysis:
            improvement = ab_test_analysis["quality_improvement"]
            if improvement.get("score_delta", 0) >= 0.1:
                recommendations.append("Optimierte Prompt-Version für zukünftige Kapitel verwenden")
        
        # Feedback-basierte Empfehlungen
        if "common_themes" in feedback_analysis:
            themes = feedback_analysis["common_themes"]
            for theme in themes:
                if "dialog" in theme.lower():
                    recommendations.append("Dialoge in zukünftigen Kapiteln verstärken")
                elif "emotion" in theme.lower():
                    recommendations.append("Emotionale Tiefe weiter ausbauen")
                elif "description" in theme.lower():
                    recommendations.append("Beschreibungen detaillierter gestalten")
        
        # Rating-basierte Empfehlungen
        avg_rating = feedback_analysis.get("average_rating", 0)
        if avg_rating < 3.0:
            recommendations.append("Generelle Qualitätsverbesserung erforderlich")
        elif avg_rating >= 4.0:
            recommendations.append("Aktuelle Qualität beibehalten")
        
        return recommendations
    
    def generate_summary_report(self) -> Dict:
        """Generiert Zusammenfassungs-Report für alle Kapitel"""
        try:
            # Sammle alle erweiterten Reports
            enhanced_reports = []
            output_dir = Path("output")
            
            for report_file in output_dir.glob("enhanced_report_chapter_*.json"):
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        enhanced_reports.append(report)
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {report_file}: {e}")
            
            if not enhanced_reports:
                return {"message": "Keine erweiterten Reports gefunden"}
            
            # Generiere Zusammenfassung
            summary = {
                "summary_timestamp": datetime.now().isoformat(),
                "total_chapters": len(enhanced_reports),
                "overall_ab_test_results": self._summarize_ab_tests(enhanced_reports),
                "overall_feedback_summary": self.feedback_system.generate_feedback_summary(),
                "chapter_specific_recommendations": self._extract_chapter_recommendations(enhanced_reports)
            }
            
            # Speichere Zusammenfassung
            summary_file = "output/enhanced_summary_report.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Zusammenfassungs-Report generiert: {summary_file}")
            return summary
            
        except Exception as e:
            logger.error(f"Fehler beim Generieren des Zusammenfassungs-Reports: {e}")
            return {"error": str(e)}
    
    def _summarize_ab_tests(self, enhanced_reports: List[Dict]) -> Dict:
        """Fasst A/B-Test-Ergebnisse zusammen"""
        ab_tests = [report["ab_test_analysis"] for report in enhanced_reports 
                   if "ab_test_analysis" in report and "error" not in report["ab_test_analysis"]]
        
        if not ab_tests:
            return {"message": "Keine A/B-Test-Daten verfügbar"}
        
        score_deltas = [test.get("quality_improvement", {}).get("score_delta", 0) for test in ab_tests]
        
        return {
            "total_ab_tests": len(ab_tests),
            "average_improvement": sum(score_deltas) / len(score_deltas),
            "positive_improvements": sum(1 for delta in score_deltas if delta > 0),
            "significant_improvements": sum(1 for delta in score_deltas if delta >= 0.1)
        }
    
    def _extract_chapter_recommendations(self, enhanced_reports: List[Dict]) -> Dict:
        """Extrahiert kapitelspezifische Empfehlungen"""
        recommendations = {}
        
        for report in enhanced_reports:
            chapter_num = report.get("chapter_number")
            if chapter_num:
                recommendations[f"chapter_{chapter_num}"] = report.get("recommendations", [])
        
        return recommendations

def main():
    """Beispiel für erweitertes Reporting"""
    reporting = EnhancedChapterReporting()
    
    # Generiere erweiterten Report für Kapitel 1
    enhanced_report = reporting.generate_enhanced_report(
        chapter_number=1,
        include_feedback=True
    )
    
    print("\n" + "="*60)
    print("ERWEITERTER KAPITEL-REPORT")
    print("="*60)
    
    if "error" not in enhanced_report:
        print(f"Kapitel: {enhanced_report['chapter_number']}")
        
        # A/B-Test-Analyse
        ab_analysis = enhanced_report.get("ab_test_analysis", {})
        if ab_analysis and "error" not in ab_analysis:
            improvement = ab_analysis.get("quality_improvement", {})
            print(f"Qualitätsverbesserung: {improvement.get('score_delta', 0):.3f}")
            print(f"Empfehlung: {ab_analysis.get('recommendation', 'N/A')}")
        
        # Feedback-Analyse
        feedback_analysis = enhanced_report.get("feedback_analysis", {})
        if feedback_analysis and "error" not in feedback_analysis:
            print(f"Durchschnittliches Rating: {feedback_analysis.get('average_rating', 0):.2f}/5")
            print(f"Feedback-Einträge: {feedback_analysis.get('total_feedback_entries', 0)}")
        
        # Empfehlungen
        recommendations = enhanced_report.get("recommendations", [])
        if recommendations:
            print("\nEmpfehlungen:")
            for rec in recommendations:
                print(f"• {rec}")
    else:
        print(f"Fehler: {enhanced_report['error']}")
    
    print("="*60)

if __name__ == "__main__":
    main() 