#!/usr/bin/env python3
"""
Robustness Manager
Robustheit & Retry-Mechanismen mit Constraint Enforcement und Output-Health-Checks
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
from dataclasses import dataclass

from core.architecture import (
    ComponentInterface, ComponentType, GenerationResult, 
    register_component
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConstraintViolation:
    """Constraint-Verletzung"""
    constraint_type: str
    severity: str  # low, medium, high, critical
    description: str
    detected_content: str
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = None

@dataclass
class QualityIssue:
    """Qualitäts-Problem"""
    issue_type: str
    severity: str  # low, medium, high, critical
    description: str
    metrics: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any] = None

@dataclass
class RetryInstruction:
    """Retry-Anweisung"""
    reason: str
    adjustment_type: str  # prompt_modification, constraint_relaxation, target_adjustment
    specific_instructions: str
    priority: int  # 1-5, höher = wichtiger
    metadata: Dict[str, Any] = None

class RobustnessManager(ComponentInterface):
    """Robustness Manager für Constraint Enforcement und Retry-Mechanismen"""
    
    def __init__(self):
        super().__init__(ComponentType.EVALUATOR, version="2.0.0")
        self.constraint_patterns = self._load_constraint_patterns()
        self.quality_thresholds = self._load_quality_thresholds()
        self.retry_strategies = self._load_retry_strategies()
        
    def _load_constraint_patterns(self) -> Dict[str, Dict]:
        """Lädt Constraint-Patterns"""
        return {
            "violence": {
                "patterns": [
                    r"\b(blut|blood|gewalt|violence|kampf|fight|schlag|hit|töten|kill)\b",
                    r"\b(waffe|weapon|messer|knife|pistole|gun)\b",
                    r"\b(angriff|attack|verletzung|injury|schmerz|pain)\b"
                ],
                "severity": "high",
                "age_groups": ["preschool", "early_reader"],
                "description": "Gewaltdarstellung"
            },
            "inappropriate_content": {
                "patterns": [
                    r"\b(verliebt|in love|kuss|kiss|beziehung|relationship)\b",
                    r"\b(alkohol|alcohol|drogen|drugs|rauchen|smoking)\b",
                    r"\b(fluchen|swearing|schimpfwörter|curse words)\b"
                ],
                "severity": "medium",
                "age_groups": ["preschool", "early_reader", "middle_grade"],
                "description": "Unangemessener Inhalt"
            },
            "negative_emotions": {
                "patterns": [
                    r"\b(verzweiflung|despair|hoffnungslos|hopeless|selbstmord|suicide)\b",
                    r"\b(hass|hate|wut|anger|traurig|sad)\b",
                    r"\b(angst|fear|panik|panic|terror)\b"
                ],
                "severity": "medium",
                "age_groups": ["preschool", "early_reader"],
                "description": "Negative Emotionen"
            },
            "complex_concepts": {
                "patterns": [
                    r"\b(philosophie|philosophy|metaphysik|metaphysics|existenz|existence)\b",
                    r"\b(politik|politics|religion|religion|ideologie|ideology)\b",
                    r"\b(psychologie|psychology|psychoanalyse|psychoanalysis)\b"
                ],
                "severity": "low",
                "age_groups": ["preschool", "early_reader"],
                "description": "Komplexe Konzepte"
            }
        }
    
    def _load_quality_thresholds(self) -> Dict[str, Dict]:
        """Lädt Qualitäts-Schwellenwerte"""
        return {
            "word_count": {
                "preschool": {"min": 100, "max": 300, "target": 200},
                "early_reader": {"min": 300, "max": 600, "target": 400},
                "middle_grade": {"min": 600, "max": 1000, "target": 800},
                "young_adult": {"min": 1000, "max": 1500, "target": 1200},
                "adult": {"min": 1200, "max": 2000, "target": 1500}
            },
            "sentence_length": {
                "preschool": {"max": 8, "avg": 6},
                "early_reader": {"max": 12, "avg": 10},
                "middle_grade": {"max": 18, "avg": 15},
                "young_adult": {"max": 25, "avg": 20},
                "adult": {"max": 30, "avg": 25}
            },
            "emotional_content": {
                "preschool": {"min_ratio": 0.02, "target_ratio": 0.03},
                "early_reader": {"min_ratio": 0.03, "target_ratio": 0.04},
                "middle_grade": {"min_ratio": 0.04, "target_ratio": 0.05},
                "young_adult": {"min_ratio": 0.05, "target_ratio": 0.08},
                "adult": {"min_ratio": 0.06, "target_ratio": 0.10}
            },
            "dialogue_ratio": {
                "preschool": {"min": 0.1, "max": 0.3, "target": 0.2},
                "early_reader": {"min": 0.15, "max": 0.35, "target": 0.25},
                "middle_grade": {"min": 0.2, "max": 0.4, "target": 0.3},
                "young_adult": {"min": 0.25, "max": 0.45, "target": 0.35},
                "adult": {"min": 0.3, "max": 0.5, "target": 0.4}
            }
        }
    
    def _load_retry_strategies(self) -> Dict[str, Dict]:
        """Lädt Retry-Strategien"""
        return {
            "word_count_too_low": {
                "adjustment_type": "prompt_modification",
                "instruction_template": "Erweitere die Geschichte so, dass sie mindestens {target_words} Wörter umfasst. Füge mehr Details, Dialoge und Beschreibungen hinzu.",
                "priority": 3
            },
            "emotional_content_too_low": {
                "adjustment_type": "prompt_modification",
                "instruction_template": "Erhöhe die emotionale Tiefe der Geschichte. Verwende mehr emotionale Schlüsselwörter und schaffe tiefere Charakterverbindungen.",
                "priority": 2
            },
            "dialogue_ratio_too_low": {
                "adjustment_type": "prompt_modification",
                "instruction_template": "Erhöhe den Dialog-Anteil in der Geschichte. Füge mehr Gespräche zwischen Charakteren hinzu.",
                "priority": 2
            },
            "constraint_violation": {
                "adjustment_type": "constraint_relaxation",
                "instruction_template": "Entferne oder ersetze problematische Inhalte: {violations}. Verwende angemessene Alternativen.",
                "priority": 4
            },
            "complexity_too_high": {
                "adjustment_type": "prompt_modification",
                "instruction_template": "Vereinfache die Sprache und Struktur für die Zielgruppe. Verwende kürzere Sätze und einfachere Konzepte.",
                "priority": 3
            }
        }
    
    def check_constraints(self, text: str, age_group: str) -> List[ConstraintViolation]:
        """Prüft Text auf Constraint-Verletzungen"""
        violations = []
        
        for constraint_type, constraint_config in self.constraint_patterns.items():
            # Prüfe ob Constraint für Altersgruppe gilt
            if age_group in constraint_config.get("age_groups", []):
                for pattern in constraint_config["patterns"]:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        violation = ConstraintViolation(
                            constraint_type=constraint_type,
                            severity=constraint_config["severity"],
                            description=constraint_config["description"],
                            detected_content=match.group(),
                            line_number=self._get_line_number(text, match.start()),
                            metadata={
                                "pattern": pattern,
                                "position": match.start(),
                                "context": text[max(0, match.start()-20):match.end()+20]
                            }
                        )
                        violations.append(violation)
        
        return violations
    
    def _get_line_number(self, text: str, position: int) -> int:
        """Berechnet Zeilennummer für Position"""
        return text[:position].count('\n') + 1
    
    def check_quality_issues(self, text: str, age_group: str) -> List[QualityIssue]:
        """Prüft Text auf Qualitäts-Probleme"""
        issues = []
        
        # Wortanzahl prüfen
        word_count = len(text.split())
        thresholds = self.quality_thresholds["word_count"].get(age_group, {})
        
        if word_count < thresholds.get("min", 0):
            issues.append(QualityIssue(
                issue_type="word_count_too_low",
                severity="medium",
                description=f"Text zu kurz: {word_count} Wörter (Minimum: {thresholds.get('min', 0)})",
                metrics={"word_count": word_count, "min_required": thresholds.get("min", 0)},
                recommendations=[
                    "Erweitere die Geschichte mit mehr Details",
                    "Füge Dialoge zwischen Charakteren hinzu",
                    "Beschreibe Umgebung und Atmosphäre"
                ]
            ))
        
        # Satzlängen prüfen
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        sentence_thresholds = self.quality_thresholds["sentence_length"].get(age_group, {})
        
        if avg_sentence_length > sentence_thresholds.get("max", 20):
            issues.append(QualityIssue(
                issue_type="sentence_length_too_high",
                severity="low",
                description=f"Durchschnittliche Satzlänge zu hoch: {avg_sentence_length:.1f} (Maximum: {sentence_thresholds.get('max', 20)})",
                metrics={"avg_sentence_length": avg_sentence_length, "max_allowed": sentence_thresholds.get("max", 20)},
                recommendations=[
                    "Verwende kürzere, klarere Sätze",
                    "Brich lange Sätze in mehrere auf",
                    "Verwende mehr Punkte statt Kommas"
                ]
            ))
        
        # Emotionale Inhalte prüfen
        emotional_words = self._count_emotional_words(text)
        emotional_ratio = emotional_words / max(word_count, 1)
        emotional_thresholds = self.quality_thresholds["emotional_content"].get(age_group, {})
        
        if emotional_ratio < emotional_thresholds.get("min_ratio", 0.02):
            issues.append(QualityIssue(
                issue_type="emotional_content_too_low",
                severity="medium",
                description=f"Emotionale Inhalte zu gering: {emotional_ratio:.3f} (Minimum: {emotional_thresholds.get('min_ratio', 0.02)})",
                metrics={"emotional_ratio": emotional_ratio, "min_required": emotional_thresholds.get("min_ratio", 0.02)},
                recommendations=[
                    "Verwende mehr emotionale Schlüsselwörter",
                    "Beschreibe Charaktergefühle detaillierter",
                    "Baue emotionale Spannungsbögen auf"
                ]
            ))
        
        # Dialog-Anteil prüfen
        dialogue_ratio = self._calculate_dialogue_ratio(text)
        dialogue_thresholds = self.quality_thresholds["dialogue_ratio"].get(age_group, {})
        
        if dialogue_ratio < dialogue_thresholds.get("min", 0.1):
            issues.append(QualityIssue(
                issue_type="dialogue_ratio_too_low",
                severity="low",
                description=f"Dialog-Anteil zu gering: {dialogue_ratio:.3f} (Minimum: {dialogue_thresholds.get('min', 0.1)})",
                metrics={"dialogue_ratio": dialogue_ratio, "min_required": dialogue_thresholds.get("min", 0.1)},
                recommendations=[
                    "Füge mehr Dialoge zwischen Charakteren hinzu",
                    "Verwende direkte Rede für Charakterentwicklung",
                    "Lass Charaktere ihre Gefühle aussprechen"
                ]
            ))
        
        return issues
    
    def _count_emotional_words(self, text: str) -> int:
        """Zählt emotionale Wörter"""
        emotional_patterns = [
            r"\b(freude|joy|glück|happiness|liebe|love|wunder|wonder)\b",
            r"\b(mut|courage|stark|strong|tapfer|brave|entschlossen|determined)\b",
            r"\b(freundschaft|friendship|herz|heart|warm|warmth|verbunden|connected)\b",
            r"\b(lachen|laugh|spaß|fun|spielen|play|träumen|dream)\b",
            r"\b(angst|fear|sorgen|worries|traurig|sad|einsam|lonely)\b",
            r"\b(hoffnung|hope|vertrauen|trust|glauben|believe|vertrauen|confidence)\b"
        ]
        
        count = 0
        for pattern in emotional_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    def _calculate_dialogue_ratio(self, text: str) -> float:
        """Berechnet Dialog-Anteil"""
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
    
    def determine_retry_needed(self, 
                             violations: List[ConstraintViolation],
                             issues: List[QualityIssue],
                             age_group: str) -> Tuple[bool, List[RetryInstruction]]:
        """Bestimmt ob Retry benötigt wird und erstellt Anweisungen"""
        retry_needed = False
        retry_instructions = []
        
        # Prüfe Constraint-Verletzungen
        critical_violations = [v for v in violations if v.severity in ["high", "critical"]]
        if critical_violations:
            retry_needed = True
            retry_instructions.append(RetryInstruction(
                reason="Constraint-Verletzungen",
                adjustment_type="constraint_relaxation",
                specific_instructions=self._create_constraint_retry_instruction(critical_violations),
                priority=4
            ))
        
        # Prüfe Qualitäts-Probleme
        high_priority_issues = [i for i in issues if i.severity in ["high", "medium"]]
        if high_priority_issues:
            retry_needed = True
            for issue in high_priority_issues:
                retry_instructions.append(RetryInstruction(
                    reason=issue.description,
                    adjustment_type="prompt_modification",
                    specific_instructions=self._create_quality_retry_instruction(issue, age_group),
                    priority=3 if issue.severity == "high" else 2
                ))
        
        # Sortiere nach Priorität (höher = wichtiger)
        retry_instructions.sort(key=lambda x: x.priority, reverse=True)
        
        return retry_needed, retry_instructions
    
    def _create_constraint_retry_instruction(self, violations: List[ConstraintViolation]) -> str:
        """Erstellt Retry-Anweisung für Constraint-Verletzungen"""
        violation_descriptions = []
        for violation in violations:
            violation_descriptions.append(f"- {violation.description}: '{violation.detected_content}'")
        
        return f"""ENTFERNE ODER ERSETZE PROBLEMATISCHE INHALTE:

{chr(10).join(violation_descriptions)}

RICHTLINIEN:
- Verwende angemessene Alternativen
- Fokussiere auf positive, konstruktive Botschaften
- Stelle sicher, dass alle Inhalte altersgerecht sind
- Ersetze problematische Elemente durch positive Gegenstücke"""
    
    def _create_quality_retry_instruction(self, issue: QualityIssue, age_group: str) -> str:
        """Erstellt Retry-Anweisung für Qualitäts-Probleme"""
        strategy = self.retry_strategies.get(issue.issue_type, {})
        
        if issue.issue_type == "word_count_too_low":
            thresholds = self.quality_thresholds["word_count"].get(age_group, {})
            target_words = thresholds.get("target", 800)
            return strategy["instruction_template"].format(target_words=target_words)
        
        elif issue.issue_type == "emotional_content_too_low":
            return strategy["instruction_template"]
        
        elif issue.issue_type == "dialogue_ratio_too_low":
            return strategy["instruction_template"]
        
        else:
            return f"Verbessere: {issue.description}\n\nEmpfehlungen:\n" + "\n".join(f"- {rec}" for rec in issue.recommendations)
    
    def apply_retry_instructions(self, 
                               original_prompt: str,
                               retry_instructions: List[RetryInstruction]) -> str:
        """Wendet Retry-Anweisungen auf Prompt an"""
        modified_prompt = original_prompt
        
        # Füge Retry-Anweisungen hinzu
        retry_section = "\n\n=== RETRY-INSTRUKTIONEN ===\n"
        for instruction in retry_instructions:
            retry_section += f"\n{instruction.reason}:\n{instruction.specific_instructions}\n"
        
        modified_prompt += retry_section
        
        return modified_prompt
    
    def validate_generation_result(self, 
                                 result: GenerationResult,
                                 age_group: str) -> Dict[str, Any]:
        """Validiert Generierungs-Ergebnis"""
        validation_result = {
            "valid": True,
            "constraint_violations": [],
            "quality_issues": [],
            "retry_needed": False,
            "retry_instructions": [],
            "overall_health_score": 1.0
        }
        
        # Prüfe deutsche Version
        if result.german_text:
            violations = self.check_constraints(result.german_text, age_group)
            issues = self.check_quality_issues(result.german_text, age_group)
            
            validation_result["constraint_violations"].extend(violations)
            validation_result["quality_issues"].extend(issues)
        
        # Prüfe englische Version
        if result.english_text:
            violations = self.check_constraints(result.english_text, age_group)
            issues = self.check_quality_issues(result.english_text, age_group)
            
            validation_result["constraint_violations"].extend(violations)
            validation_result["quality_issues"].extend(issues)
        
        # Bestimme ob Retry benötigt wird
        retry_needed, retry_instructions = self.determine_retry_needed(
            validation_result["constraint_violations"],
            validation_result["quality_issues"],
            age_group
        )
        
        validation_result["retry_needed"] = retry_needed
        validation_result["retry_instructions"] = retry_instructions
        
        # Berechne Health Score
        health_score = self._calculate_health_score(
            validation_result["constraint_violations"],
            validation_result["quality_issues"]
        )
        validation_result["overall_health_score"] = health_score
        
        # Markiere als ungültig wenn kritische Probleme
        if any(v.severity == "critical" for v in validation_result["constraint_violations"]):
            validation_result["valid"] = False
        
        return validation_result
    
    def _calculate_health_score(self, 
                              violations: List[ConstraintViolation],
                              issues: List[QualityIssue]) -> float:
        """Berechnet Health Score"""
        score = 1.0
        
        # Strafpunkte für Constraint-Verletzungen
        for violation in violations:
            if violation.severity == "critical":
                score -= 0.5
            elif violation.severity == "high":
                score -= 0.3
            elif violation.severity == "medium":
                score -= 0.2
            elif violation.severity == "low":
                score -= 0.1
        
        # Strafpunkte für Qualitäts-Probleme
        for issue in issues:
            if issue.severity == "high":
                score -= 0.2
            elif issue.severity == "medium":
                score -= 0.1
            elif issue.severity == "low":
                score -= 0.05
        
        return max(score, 0.0)

# Registrierte Version des Robustness Managers
class RobustnessManagerComponent(RobustnessManager):
    """Registrierte Version des Robustness Managers"""
    def __init__(self):
        super().__init__() 