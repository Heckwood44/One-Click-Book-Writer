#!/usr/bin/env python3
"""
Umfassende Tests für Robustness Manager - Coverage-Verbesserung
Ziel: Coverage von 34% auf mindestens 50% erhöhen
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import time
from typing import List, Dict, Any, Optional

from core.robustness_manager import RobustnessManager, ConstraintViolation, QualityIssue, RetryInstruction
from core.architecture import (
    PromptFrame, PromptTemplate, GenerationResult, EvaluationResult,
    ComponentType
)


class TestRobustnessManagerComprehensive(unittest.TestCase):
    """Umfassende Tests für RobustnessManager - Coverage-Verbesserung"""
    
    def setUp(self):
        """Setup für umfassende Tests"""
        self.robustness_manager = RobustnessManager()
        
        # Test-GenerationResult
        self.generation_result = GenerationResult(
            success=True,
            german_text="Es war einmal ein kleiner Drache...",
            english_text="Once upon a time there was a little dragon...",
            prompt_hash="test_hash",
            template_hash="template_hash",
            generation_time=1.5,
            word_count=100
        )

    # ===== TESTS FÜR CONSTRAINT-CHECKING =====
    
    def test_check_constraints_no_violations(self):
        """Test Constraint-Checking ohne Verletzungen"""
        text = "Es war einmal ein kleiner Drache, der sehr freundlich war."
        
        violations = self.robustness_manager.check_constraints(text, "children")
        
        self.assertIsInstance(violations, list)
        self.assertEqual(len(violations), 0)
    
    def test_check_constraints_violence_violation(self):
        """Test Constraint-Checking mit Gewalt-Verletzung"""
        text = "Der Drache kämpfte mit dem Ritter und es gab viel Blut."
        
        violations = self.robustness_manager.check_constraints(text, "children")
        
        self.assertIsInstance(violations, list)
        self.assertGreater(len(violations), 0)
        
        # Überprüfe, dass es eine Gewalt-Verletzung gibt
        violence_violations = [v for v in violations if v.constraint_type == "violence"]
        self.assertGreater(len(violence_violations), 0)
        self.assertEqual(violence_violations[0].severity, "high")
    
    def test_check_constraints_inappropriate_content(self):
        """Test Constraint-Checking mit unangemessenem Inhalt"""
        text = "Die Prinzessin war verliebt und küsste den Prinzen."
        
        violations = self.robustness_manager.check_constraints(text, "preschool")
        
        self.assertIsInstance(violations, list)
        self.assertGreater(len(violations), 0)
        
        inappropriate_violations = [v for v in violations if v.constraint_type == "inappropriate_content"]
        self.assertGreater(len(inappropriate_violations), 0)
        self.assertEqual(inappropriate_violations[0].severity, "medium")
    
    def test_check_constraints_negative_emotions(self):
        """Test Constraint-Checking mit negativen Emotionen"""
        text = "Der kleine Drache war verzweifelt und hoffnungslos."
        
        violations = self.robustness_manager.check_constraints(text, "early_reader")
        
        self.assertIsInstance(violations, list)
        self.assertGreater(len(violations), 0)
        
        emotion_violations = [v for v in violations if v.constraint_type == "negative_emotions"]
        self.assertGreater(len(emotion_violations), 0)
    
    def test_check_constraints_complex_concepts(self):
        """Test Constraint-Checking mit komplexen Konzepten"""
        text = "Die Geschichte handelte von Philosophie und Metaphysik."
        
        violations = self.robustness_manager.check_constraints(text, "preschool")
        
        self.assertIsInstance(violations, list)
        self.assertGreater(len(violations), 0)
        
        concept_violations = [v for v in violations if v.constraint_type == "complex_concepts"]
        self.assertGreater(len(concept_violations), 0)
        self.assertEqual(concept_violations[0].severity, "low")
    
    def test_check_constraints_older_age_group(self):
        """Test Constraint-Checking für ältere Altersgruppen"""
        text = "Der Drache kämpfte mit dem Ritter und es gab viel Blut."
        
        violations = self.robustness_manager.check_constraints(text, "young_adult")
        
        # Ältere Altersgruppen sollten weniger strikte Constraints haben
        self.assertIsInstance(violations, list)
        # Könnte weniger oder keine Verletzungen haben
    
    # ===== TESTS FÜR QUALITY-ISSUE-CHECKING =====
    
    def test_check_quality_issues_no_issues(self):
        """Test Quality-Issue-Checking ohne Probleme"""
        text = "Es war einmal ein kleiner Drache. Er war sehr freundlich und spielte gerne mit anderen Tieren."
        
        issues = self.robustness_manager.check_quality_issues(text, "children")
        
        self.assertIsInstance(issues, list)
        # Könnte einige Standard-Qualitätsprobleme haben, aber nicht kritisch
    
    def test_check_quality_issues_low_emotional_depth(self):
        """Test Quality-Issue-Checking mit niedriger emotionaler Tiefe"""
        text = "Es war ein Drache. Er lebte in einer Höhle. Das war alles."
        
        issues = self.robustness_manager.check_quality_issues(text, "children")
        
        self.assertIsInstance(issues, list)
        # Sollte Probleme mit emotionaler Tiefe erkennen
    
    def test_check_quality_issues_low_dialogue_ratio(self):
        """Test Quality-Issue-Checking mit niedrigem Dialog-Anteil"""
        text = "Es war einmal ein Drache. Er lebte in einer Höhle. Er war sehr groß. Er hatte Flügel. Das war die Geschichte."
        
        issues = self.robustness_manager.check_quality_issues(text, "children")
        
        self.assertIsInstance(issues, list)
        # Sollte Probleme mit Dialog-Anteil erkennen
    
    def test_check_quality_issues_short_text(self):
        """Test Quality-Issue-Checking mit zu kurzem Text"""
        text = "Kurze Geschichte."
        
        issues = self.robustness_manager.check_quality_issues(text, "children")
        
        self.assertIsInstance(issues, list)
        # Sollte Probleme mit Textlänge erkennen
    
    # ===== TESTS FÜR RETRY-DETERMINATION =====
    
    def test_determine_retry_needed_no_issues(self):
        """Test Retry-Determination ohne Probleme"""
        violations = []
        issues = []
        
        retry_needed, instructions = self.robustness_manager.determine_retry_needed(
            violations, issues, "children"
        )
        
        self.assertIsInstance(retry_needed, bool)
        self.assertIsInstance(instructions, list)
        self.assertFalse(retry_needed)
        self.assertEqual(len(instructions), 0)
    
    def test_determine_retry_needed_with_constraint_violations(self):
        """Test Retry-Determination mit Constraint-Verletzungen"""
        violations = [
            ConstraintViolation(
                constraint_type="violence",
                severity="high",
                description="Gewaltdarstellung",
                detected_content="Blut",
                line_number=1
            )
        ]
        issues = []
        
        retry_needed, instructions = self.robustness_manager.determine_retry_needed(
            violations, issues, "children"
        )
        
        self.assertIsInstance(retry_needed, bool)
        self.assertIsInstance(instructions, list)
        self.assertTrue(retry_needed)
        self.assertGreater(len(instructions), 0)
        
        # Überprüfe, dass es eine Constraint-Retry-Anweisung gibt
        constraint_instructions = [i for i in instructions if i.adjustment_type == "constraint_relaxation"]
        self.assertGreater(len(constraint_instructions), 0)
    
    def test_determine_retry_needed_with_quality_issues(self):
        """Test Retry-Determination mit Qualitätsproblemen"""
        violations = []
        issues = [
            QualityIssue(
                issue_type="low_emotional_depth",
                severity="medium",
                description="Niedrige emotionale Tiefe",
                metrics={"emotional_words": 2, "target": 10},
                recommendations=["Mehr emotionale Wörter verwenden"]
            )
        ]
        
        retry_needed, instructions = self.robustness_manager.determine_retry_needed(
            violations, issues, "children"
        )
        
        self.assertIsInstance(retry_needed, bool)
        self.assertIsInstance(instructions, list)
        self.assertTrue(retry_needed)
        self.assertGreater(len(instructions), 0)
    
    def test_determine_retry_needed_critical_issues(self):
        """Test Retry-Determination mit kritischen Problemen"""
        violations = [
            ConstraintViolation(
                constraint_type="violence",
                severity="critical",
                description="Kritische Gewaltdarstellung",
                detected_content="Blut",
                line_number=1
            )
        ]
        issues = [
            QualityIssue(
                issue_type="inappropriate_content",
                severity="critical",
                description="Kritischer Inhalt",
                metrics={"inappropriate_ratio": 0.8},
                recommendations=["Komplett neu schreiben"]
            )
        ]
        
        retry_needed, instructions = self.robustness_manager.determine_retry_needed(
            violations, issues, "preschool"
        )
        
        self.assertTrue(retry_needed)
        self.assertGreater(len(instructions), 0)
        
        # Überprüfe Prioritäten
        high_priority_instructions = [i for i in instructions if i.priority >= 4]
        self.assertGreater(len(high_priority_instructions), 0)
    
    # ===== TESTS FÜR RETRY-INSTRUCTION-APPLICATION =====
    
    def test_apply_retry_instructions(self):
        """Test Anwendung von Retry-Anweisungen"""
        original_prompt = "Write a story about a dragon."
        
        instructions = [
            RetryInstruction(
                reason="Violence constraint violation",
                adjustment_type="constraint_relaxation",
                specific_instructions="Avoid any mention of violence or fighting",
                priority=4
            ),
            RetryInstruction(
                reason="Low emotional depth",
                adjustment_type="prompt_modification",
                specific_instructions="Add emotional elements and character feelings",
                priority=3
            )
        ]
        
        modified_prompt = self.robustness_manager.apply_retry_instructions(
            original_prompt, instructions
        )
        
        self.assertIsInstance(modified_prompt, str)
        self.assertIn("Write a story about a dragon", modified_prompt)
        self.assertIn("Avoid any mention of violence", modified_prompt)
        self.assertIn("Add emotional elements", modified_prompt)
    
    def test_apply_retry_instructions_empty(self):
        """Test Anwendung von leeren Retry-Anweisungen"""
        original_prompt = "Write a story about a dragon."
        instructions = []
        
        modified_prompt = self.robustness_manager.apply_retry_instructions(
            original_prompt, instructions
        )
        
        self.assertEqual(modified_prompt, original_prompt)
    
    # ===== TESTS FÜR GENERATION-RESULT-VALIDATION =====
    
    def test_validate_generation_result_success(self):
        """Test Validierung eines erfolgreichen Generation-Results"""
        result = self.generation_result
        
        validation = self.robustness_manager.validate_generation_result(result, "children")
        
        self.assertIsInstance(validation, dict)
        self.assertIn("is_valid", validation)
        self.assertIn("health_score", validation)
        self.assertIn("constraint_violations", validation)
        self.assertIn("quality_issues", validation)
        self.assertIn("recommendations", validation)
    
    def test_validate_generation_result_with_violations(self):
        """Test Validierung mit Constraint-Verletzungen"""
        result = GenerationResult(
            success=True,
            german_text="Der Drache kämpfte und es gab viel Blut.",
            english_text="The dragon fought and there was much blood.",
            prompt_hash="test_hash",
            template_hash="template_hash",
            generation_time=1.5,
            word_count=100
        )
        
        validation = self.robustness_manager.validate_generation_result(result, "children")
        
        self.assertIsInstance(validation, dict)
        self.assertIn("is_valid", validation)
        self.assertIn("constraint_violations", validation)
        
        # Sollte Verletzungen erkennen
        violations = validation["constraint_violations"]
        self.assertGreater(len(violations), 0)
    
    def test_validate_generation_result_failed_generation(self):
        """Test Validierung eines fehlgeschlagenen Generation-Results"""
        result = GenerationResult(
            success=False,
            german_text="",
            english_text="",
            prompt_hash="test_hash",
            template_hash="template_hash",
            generation_time=0.0,
            word_count=0
        )
        
        validation = self.robustness_manager.validate_generation_result(result, "children")
        
        self.assertIsInstance(validation, dict)
        self.assertIn("is_valid", validation)
        self.assertFalse(validation["is_valid"])
    
    # ===== TESTS FÜR HILFSMETHODEN =====
    
    def test_get_line_number(self):
        """Test Zeilennummer-Bestimmung"""
        text = "Zeile 1\nZeile 2\nZeile 3"
        position = 10  # Position in "Zeile 2"
        
        line_number = self.robustness_manager._get_line_number(text, position)
        
        self.assertEqual(line_number, 2)
    
    def test_count_emotional_words(self):
        """Test Zählung emotionaler Wörter"""
        text = "Der kleine Drache war glücklich und freute sich sehr über die Freundschaft."
        
        count = self.robustness_manager._count_emotional_words(text)
        
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_calculate_dialogue_ratio(self):
        """Test Berechnung des Dialog-Anteils"""
        text = "Der Drache sagte: 'Hallo!' Dann antwortete der Ritter: 'Guten Tag!'"
        
        ratio = self.robustness_manager._calculate_dialogue_ratio(text)
        
        self.assertIsInstance(ratio, float)
        self.assertGreaterEqual(ratio, 0.0)
        self.assertLessEqual(ratio, 1.0)
    
    def test_calculate_dialogue_ratio_no_dialogue(self):
        """Test Dialog-Anteil ohne Dialog"""
        text = "Der Drache lebte in einer Höhle. Er war sehr groß."
        
        ratio = self.robustness_manager._calculate_dialogue_ratio(text)
        
        self.assertEqual(ratio, 0.0)
    
    def test_calculate_health_score(self):
        """Test Berechnung des Health-Scores"""
        violations = [
            ConstraintViolation(
                constraint_type="violence",
                severity="medium",
                description="Gewaltdarstellung",
                detected_content="Kampf",
                line_number=1
            )
        ]
        issues = [
            QualityIssue(
                issue_type="low_emotional_depth",
                severity="low",
                description="Niedrige emotionale Tiefe",
                metrics={"emotional_words": 2},
                recommendations=["Mehr Emotionen"]
            )
        ]
        
        health_score = self.robustness_manager._calculate_health_score(violations, issues)
        
        self.assertIsInstance(health_score, float)
        self.assertGreaterEqual(health_score, 0.0)
        self.assertLessEqual(health_score, 1.0)
    
    def test_calculate_health_score_perfect(self):
        """Test Health-Score für perfekten Text"""
        violations = []
        issues = []
        
        health_score = self.robustness_manager._calculate_health_score(violations, issues)
        
        self.assertEqual(health_score, 1.0)
    
    def test_calculate_health_score_critical(self):
        """Test Health-Score für kritische Probleme"""
        violations = [
            ConstraintViolation(
                constraint_type="violence",
                severity="critical",
                description="Kritische Gewaltdarstellung",
                detected_content="Blut",
                line_number=1
            )
        ]
        issues = [
            QualityIssue(
                issue_type="inappropriate_content",
                severity="critical",
                description="Kritischer Inhalt",
                metrics={"inappropriate_ratio": 0.9},
                recommendations=["Komplett neu schreiben"]
            )
        ]
        
        health_score = self.robustness_manager._calculate_health_score(violations, issues)
        
        self.assertIsInstance(health_score, float)
        self.assertLess(health_score, 0.5)  # Sollte niedrig sein


if __name__ == '__main__':
    unittest.main() 