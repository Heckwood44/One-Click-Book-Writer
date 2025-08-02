#!/usr/bin/env python3
"""
One Click Book Writer - User Feedback
Version: 2.0.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class UserFeedback:
    """Verwaltet User-Feedback für Qualitätsverbesserung"""
    
    def __init__(self, feedback_file: str = "output/user_feedback.json"):
        self.feedback_file = Path(feedback_file)
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict:
        """Lädt das Feedback"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden des Feedbacks: {e}")
                return {"feedback_entries": [], "statistics": {}}
        return {"feedback_entries": [], "statistics": {}}
    
    def _save_feedback(self):
        """Speichert das Feedback"""
        try:
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Feedbacks: {e}")
    
    def add_feedback(self, 
                    chapter_number: int,
                    rating: int,
                    comment: str = "",
                    language: str = "de",
                    quality_score: Optional[float] = None) -> Dict:
        """Fügt neues Feedback hinzu"""
        
        if not 1 <= rating <= 5:
            raise ValueError("Rating muss zwischen 1 und 5 liegen")
        
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "chapter_number": chapter_number,
            "rating": rating,
            "comment": comment,
            "language": language,
            "quality_score": quality_score,
            "feedback_id": len(self.feedback_data.get("feedback_entries", [])) + 1
        }
        
        self.feedback_data.setdefault("feedback_entries", []).append(feedback_entry)
        self._save_feedback()
        
        logger.info(f"Feedback hinzugefügt: Kapitel {chapter_number}, Rating {rating}")
        
        return feedback_entry
    
    def get_feedback_summary(self) -> Dict:
        """Gibt eine Zusammenfassung des Feedbacks zurück"""
        entries = self.feedback_data.get("feedback_entries", [])
        
        if not entries:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "rating_distribution": {},
                "recent_feedback": []
            }
        
        # Durchschnittliches Rating
        total_rating = sum(entry.get("rating", 0) for entry in entries)
        average_rating = total_rating / len(entries)
        
        # Rating-Verteilung
        rating_distribution = {}
        for entry in entries:
            rating = entry.get("rating", 0)
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        # Kürzliches Feedback (letzte 10 Einträge)
        recent_feedback = sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        return {
            "total_feedback": len(entries),
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "recent_feedback": recent_feedback
        }
    
    def get_feedback_for_chapter(self, chapter_number: int) -> List[Dict]:
        """Gibt Feedback für ein spezifisches Kapitel zurück"""
        entries = self.feedback_data.get("feedback_entries", [])
        return [entry for entry in entries if entry.get("chapter_number") == chapter_number]
    
    def filter_feedback(self, 
                       min_rating: Optional[int] = None,
                       max_rating: Optional[int] = None,
                       language: Optional[str] = None,
                       days_back: Optional[int] = None) -> List[Dict]:
        """Filtert Feedback nach verschiedenen Kriterien"""
        entries = self.feedback_data.get("feedback_entries", [])
        filtered_entries = []
        
        for entry in entries:
            # Rating-Filter
            if min_rating is not None and entry.get("rating", 0) < min_rating:
                continue
            if max_rating is not None and entry.get("rating", 0) > max_rating:
                continue
            
            # Sprach-Filter
            if language is not None and entry.get("language") != language:
                continue
            
            # Zeit-Filter
            if days_back is not None:
                entry_date = datetime.fromisoformat(entry.get("timestamp", ""))
                days_old = (datetime.now() - entry_date).days
                if days_old > days_back:
                    continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def generate_improvement_suggestions(self) -> List[str]:
        """Generiert Verbesserungsvorschläge basierend auf Feedback"""
        summary = self.get_feedback_summary()
        suggestions = []
        
        if summary["total_feedback"] == 0:
            return ["Noch kein Feedback vorhanden"]
        
        average_rating = summary["average_rating"]
        
        # Rating-basierte Vorschläge
        if average_rating < 3.0:
            suggestions.append("⚠️ Durchschnittliches Rating ist niedrig - Qualität verbessern")
        elif average_rating < 4.0:
            suggestions.append("📈 Rating verbesserungswürdig - Details analysieren")
        
        # Rating-Verteilung analysieren
        rating_dist = summary["rating_distribution"]
        low_ratings = sum(count for rating, count in rating_dist.items() if rating <= 2)
        high_ratings = sum(count for rating, count in rating_dist.items() if rating >= 4)
        
        if low_ratings > high_ratings:
            suggestions.append("🔍 Viele niedrige Bewertungen - Ursachen identifizieren")
        
        # Kommentar-Analyse
        entries = self.feedback_data.get("feedback_entries", [])
        comments = [entry.get("comment", "") for entry in entries if entry.get("comment")]
        
        if comments:
            # Einfache Schlüsselwort-Analyse
            common_issues = []
            keywords = {
                "langsam": "Geschwindigkeit",
                "kurz": "Länge",
                "langweilig": "Spannung",
                "kompliziert": "Komplexität",
                "einfach": "Komplexität"
            }
            
            for comment in comments:
                comment_lower = comment.lower()
                for keyword, issue in keywords.items():
                    if keyword in comment_lower and issue not in common_issues:
                        common_issues.append(issue)
            
            for issue in common_issues:
                suggestions.append(f"🎯 Häufiges Problem: {issue} - Verbesserung nötig")
        
        if not suggestions:
            suggestions.append("✅ Feedback ist positiv - Weiter so!")
        
        return suggestions
    
    def export_feedback_report(self, output_file: str = "output/feedback_report.json") -> Dict:
        """Exportiert einen detaillierten Feedback-Report"""
        summary = self.get_feedback_summary()
        suggestions = self.generate_improvement_suggestions()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "improvement_suggestions": suggestions,
            "detailed_feedback": self.feedback_data.get("feedback_entries", [])
        }
        
        # Report speichern
        try:
            report_file = Path(output_file)
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Feedback-Report exportiert: {output_file}")
        except Exception as e:
            logger.error(f"Fehler beim Exportieren des Reports: {e}")
        
        return report 