#!/usr/bin/env python3
"""
Constraint Checker System
Robuste Output-Qualität mit automatischen Retry-Mechanismen
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConstraintViolation:
    """Repräsentiert eine Constraint-Verletzung"""
    constraint_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    detected_content: str
    line_number: Optional[int] = None
    confidence: float = 1.0

@dataclass
class QualityIssue:
    """Repräsentiert ein Qualitätsproblem"""
    issue_type: str
    severity: str
    description: str
    current_value: Any
    target_value: Any
    deviation_percent: float

class ConstraintChecker:
    """Prüft Output auf Constraint-Verletzungen und Qualitätsprobleme"""
    
    def __init__(self):
        self.forbidden_patterns = self._load_forbidden_patterns()
        self.quality_thresholds = self._load_quality_thresholds()
    
    def _load_forbidden_patterns(self) -> Dict[str, List[str]]:
        """Lädt verbotene Muster"""
        return {
            "violence": [
                r"\b(kampf|fight|gewalt|violence|schlag|hit|töten|kill|waffe|weapon)\b",
                r"\b(blut|blood|verletzung|injury|schmerz|pain)\b",
                r"\b(angst|fear|terror|panik|panic)\b"
            ],
            "inappropriate_content": [
                r"\b(fluch|curse|schimpf|swear)\b",
                r"\b(erwachsen|adult|sex|sexual)\b",
                r"\b(drogen|drugs|alkohol|alcohol)\b"
            ],
            "negative_emotions": [
                r"\b(hass|hate|wut|anger|traurig|sad|depressiv|depressive)\b",
                r"\b(verzweiflung|despair|hoffnungslos|hopeless)\b"
            ]
        }
    
    def _load_quality_thresholds(self) -> Dict[str, Dict]:
        """Lädt Qualitäts-Schwellenwerte"""
        return {
            "word_count": {
                "min": 600,
                "max": 1200,
                "target": 800
            },
            "sentence_length": {
                "max": 25,
                "target": 15
            },
            "paragraph_count": {
                "min": 3,
                "target": 5
            },
            "emotional_words": {
                "min_ratio": 0.02,  # 2% emotionale Wörter
                "target_ratio": 0.05
            },
            "dialogue_ratio": {
                "min_ratio": 0.1,  # 10% Dialoge
                "target_ratio": 0.2
            }
        }
    
    def check_constraints(self, text: str, language: str = "de") -> List[ConstraintViolation]:
        """Prüft Text auf Constraint-Verletzungen"""
        violations = []
        
        # Prüfe verbotene Muster
        for constraint_type, patterns in self.forbidden_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    severity = self._determine_violation_severity(constraint_type, match.group())
                    violation = ConstraintViolation(
                        constraint_type=constraint_type,
                        severity=severity,
                        description=f"Verbotenes Muster gefunden: {match.group()}",
                        detected_content=match.group(),
                        line_number=self._get_line_number(text, match.start()),
                        confidence=0.9
                    )
                    violations.append(violation)
        
        # Prüfe sprachspezifische Constraints
        if language == "de":
            violations.extend(self._check_german_constraints(text))
        elif language == "en":
            violations.extend(self._check_english_constraints(text))
        
        return violations
    
    def _determine_violation_severity(self, constraint_type: str, content: str) -> str:
        """Bestimmt Schweregrad einer Verletzung"""
        if constraint_type == "violence":
            if any(word in content.lower() for word in ["töten", "kill", "waffe", "weapon"]):
                return "critical"
            elif any(word in content.lower() for word in ["kampf", "fight", "gewalt", "violence"]):
                return "high"
            else:
                return "medium"
        elif constraint_type == "inappropriate_content":
            return "high"
        elif constraint_type == "negative_emotions":
            return "medium"
        else:
            return "low"
    
    def _get_line_number(self, text: str, position: int) -> int:
        """Berechnet Zeilennummer für Position"""
        return text[:position].count('\n') + 1
    
    def _check_german_constraints(self, text: str) -> List[ConstraintViolation]:
        """Prüft deutsche spezifische Constraints"""
        violations = []
        
        # Prüfe auf zu komplexe deutsche Wörter
        complex_words = re.findall(r'\b\w{15,}\b', text)
        if len(complex_words) > 5:
            violations.append(ConstraintViolation(
                constraint_type="complexity",
                severity="medium",
                description="Zu viele komplexe Wörter für Kinder",
                detected_content=f"{len(complex_words)} komplexe Wörter gefunden",
                confidence=0.8
            ))
        
        return violations
    
    def _check_english_constraints(self, text: str) -> List[ConstraintViolation]:
        """Prüft englische spezifische Constraints"""
        violations = []
        
        # Prüfe auf zu komplexe englische Wörter
        complex_words = re.findall(r'\b\w{12,}\b', text)
        if len(complex_words) > 5:
            violations.append(ConstraintViolation(
                constraint_type="complexity",
                severity="medium",
                description="Too many complex words for children",
                detected_content=f"{len(complex_words)} complex words found",
                confidence=0.8
            ))
        
        return violations
    
    def check_quality_issues(self, text: str, language: str = "de") -> List[QualityIssue]:
        """Prüft Text auf Qualitätsprobleme"""
        issues = []
        thresholds = self.quality_thresholds
        
        # Wortanzahl prüfen
        word_count = len(text.split())
        word_thresholds = thresholds["word_count"]
        
        if word_count < word_thresholds["min"]:
            deviation = ((word_thresholds["min"] - word_count) / word_thresholds["min"]) * 100
            issues.append(QualityIssue(
                issue_type="word_count",
                severity="high" if deviation > 50 else "medium",
                description=f"Text zu kurz: {word_count} Wörter (Minimum: {word_thresholds['min']})",
                current_value=word_count,
                target_value=word_thresholds["min"],
                deviation_percent=deviation
            ))
        elif word_count > word_thresholds["max"]:
            deviation = ((word_count - word_thresholds["max"]) / word_thresholds["max"]) * 100
            issues.append(QualityIssue(
                issue_type="word_count",
                severity="medium",
                description=f"Text zu lang: {word_count} Wörter (Maximum: {word_thresholds['max']})",
                current_value=word_count,
                target_value=word_thresholds["max"],
                deviation_percent=deviation
            ))
        
        # Satzlänge prüfen
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        
        if avg_sentence_length > thresholds["sentence_length"]["max"]:
            deviation = ((avg_sentence_length - thresholds["sentence_length"]["target"]) / thresholds["sentence_length"]["target"]) * 100
            issues.append(QualityIssue(
                issue_type="sentence_length",
                severity="medium",
                description=f"Durchschnittliche Satzlänge zu hoch: {avg_sentence_length:.1f} Wörter",
                current_value=avg_sentence_length,
                target_value=thresholds["sentence_length"]["target"],
                deviation_percent=deviation
            ))
        
        # Absatzanzahl prüfen
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) < thresholds["paragraph_count"]["min"]:
            deviation = ((thresholds["paragraph_count"]["min"] - len(paragraphs)) / thresholds["paragraph_count"]["min"]) * 100
            issues.append(QualityIssue(
                issue_type="paragraph_count",
                severity="medium",
                description=f"Zu wenige Absätze: {len(paragraphs)} (Minimum: {thresholds['paragraph_count']['min']})",
                current_value=len(paragraphs),
                target_value=thresholds["paragraph_count"]["min"],
                deviation_percent=deviation
            ))
        
        # Emotionale Wörter prüfen
        emotional_words = self._count_emotional_words(text, language)
        emotional_ratio = emotional_words / max(word_count, 1)
        
        if emotional_ratio < thresholds["emotional_words"]["min_ratio"]:
            deviation = ((thresholds["emotional_words"]["min_ratio"] - emotional_ratio) / thresholds["emotional_words"]["min_ratio"]) * 100
            issues.append(QualityIssue(
                issue_type="emotional_content",
                severity="high",
                description=f"Zu wenig emotionale Tiefe: {emotional_ratio:.3f} (Minimum: {thresholds['emotional_words']['min_ratio']:.3f})",
                current_value=emotional_ratio,
                target_value=thresholds["emotional_words"]["min_ratio"],
                deviation_percent=deviation
            ))
        
        # Dialog-Anteil prüfen
        dialogue_ratio = self._calculate_dialogue_ratio(text)
        
        if dialogue_ratio < thresholds["dialogue_ratio"]["min_ratio"]:
            deviation = ((thresholds["dialogue_ratio"]["min_ratio"] - dialogue_ratio) / thresholds["dialogue_ratio"]["min_ratio"]) * 100
            issues.append(QualityIssue(
                issue_type="dialogue_content",
                severity="medium",
                description=f"Zu wenig Dialoge: {dialogue_ratio:.3f} (Minimum: {thresholds['dialogue_ratio']['min_ratio']:.3f})",
                current_value=dialogue_ratio,
                target_value=thresholds["dialogue_ratio"]["min_ratio"],
                deviation_percent=deviation
            ))
        
        return issues
    
    def _count_emotional_words(self, text: str, language: str) -> int:
        """Zählt emotionale Wörter im Text"""
        if language == "de":
            emotional_patterns = [
                r"\b(freude|joy|glück|happiness|liebe|love|wunder|wonder|mut|courage)\b",
                r"\b(freundschaft|friendship|herz|heart|warm|warmth|schön|beautiful)\b",
                r"\b(lachen|laugh|spaß|fun|spielen|play|träumen|dream)\b"
            ]
        else:
            emotional_patterns = [
                r"\b(joy|happiness|love|wonder|courage|brave|happy|excited)\b",
                r"\b(friendship|heart|warm|beautiful|amazing|wonderful|magical)\b",
                r"\b(laugh|fun|play|dream|smile|cheer|celebrate)\b"
            ]
        
        count = 0
        for pattern in emotional_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    def _calculate_dialogue_ratio(self, text: str) -> float:
        """Berechnet Dialog-Anteil im Text"""
        # Einfache Dialog-Erkennung
        dialogue_patterns = [
            r'"[^"]*"',  # Deutsche Anführungszeichen
            r'"[^"]*"',  # Englische Anführungszeichen
            r'„[^"]*"',  # Deutsche Anführungszeichen
            r'"[^"]*"',  # Deutsche Anführungszeichen
        ]
        
        dialogue_chars = 0
        for pattern in dialogue_patterns:
            matches = re.findall(pattern, text)
            dialogue_chars += sum(len(match) for match in matches)
        
        return dialogue_chars / max(len(text), 1)
    
    def should_retry(self, violations: List[ConstraintViolation], issues: List[QualityIssue]) -> bool:
        """Entscheidet, ob ein Retry notwendig ist"""
        # Kritische Verletzungen = immer Retry
        critical_violations = [v for v in violations if v.severity == "critical"]
        if critical_violations:
            return True
        
        # Hohe Verletzungen = Retry
        high_violations = [v for v in violations if v.severity == "high"]
        if len(high_violations) >= 2:
            return True
        
        # Qualitätsprobleme mit hoher Abweichung
        high_severity_issues = [i for i in issues if i.severity == "high" and i.deviation_percent > 50]
        if high_severity_issues:
            return True
        
        # Kombination von mehreren Problemen
        total_problems = len(violations) + len(issues)
        if total_problems >= 3:
            return True
        
        return False
    
    def generate_retry_instruction(self, violations: List[ConstraintViolation], issues: List[QualityIssue]) -> str:
        """Generiert Retry-Anweisung basierend auf gefundenen Problemen"""
        instructions = []
        
        # Constraint-Verletzungen
        if violations:
            critical_violations = [v for v in violations if v.severity == "critical"]
            if critical_violations:
                instructions.append("KRITISCHE VERLETZUNGEN BEHEBEN:")
                for violation in critical_violations:
                    instructions.append(f"- {violation.description}")
                instructions.append("")
        
        # Qualitätsprobleme
        if issues:
            instructions.append("QUALITÄTSPROBLEME BEHEBEN:")
            
            word_count_issues = [i for i in issues if i.issue_type == "word_count"]
            if word_count_issues:
                issue = word_count_issues[0]
                if issue.current_value < issue.target_value:
                    instructions.append(f"- Text erweitern auf mindestens {issue.target_value} Wörter")
                else:
                    instructions.append(f"- Text kürzen auf maximal {issue.target_value} Wörter")
            
            emotional_issues = [i for i in issues if i.issue_type == "emotional_content"]
            if emotional_issues:
                instructions.append("- Mehr emotionale Tiefe hinzufügen (Freude, Wunder, Freundschaft)")
            
            dialogue_issues = [i for i in issues if i.issue_type == "dialogue_content"]
            if dialogue_issues:
                instructions.append("- Mehr Dialoge zwischen Charakteren hinzufügen")
            
            sentence_issues = [i for i in issues if i.issue_type == "sentence_length"]
            if sentence_issues:
                instructions.append("- Kürzere, klarere Sätze verwenden")
        
        if not instructions:
            instructions.append("Text leicht verbessern und mehr Details hinzufügen")
        
        return "\n".join(instructions)

def main():
    """Beispiel für Constraint-Checker"""
    checker = ConstraintChecker()
    
    # Test-Text
    test_text = """
    Es war ein wunderschöner Tag im Wald. Die Sonne schien warm und die Vögel sangen fröhlich.
    
    "Hallo!", rief das kleine Eichhörnchen. "Wie geht es dir heute?"
    
    "Mir geht es gut!", antwortete der Hase. "Lass uns zusammen spielen!"
    
    Sie rannten durch den Wald und hatten viel Spaß zusammen. Es war ein Tag voller Freude und Freundschaft.
    """
    
    # Prüfe Constraints
    violations = checker.check_constraints(test_text, "de")
    issues = checker.check_quality_issues(test_text, "de")
    
    print("\n" + "="*60)
    print("CONSTRAINT-CHECKER ERGEBNISSE")
    print("="*60)
    
    print(f"Constraint-Verletzungen: {len(violations)}")
    for violation in violations:
        print(f"• {violation.severity.upper()}: {violation.description}")
    
    print(f"\nQualitätsprobleme: {len(issues)}")
    for issue in issues:
        print(f"• {issue.severity.upper()}: {issue.description}")
    
    should_retry = checker.should_retry(violations, issues)
    print(f"\nRetry notwendig: {'✅ JA' if should_retry else '❌ NEIN'}")
    
    if should_retry:
        retry_instruction = checker.generate_retry_instruction(violations, issues)
        print(f"\nRetry-Anweisung:\n{retry_instruction}")
    
    print("="*60)

if __name__ == "__main__":
    main() 