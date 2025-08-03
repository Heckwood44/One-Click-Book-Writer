#!/usr/bin/env python3
"""
Policy Engine
Automatische Entscheidungslogik für Prompt-Optimierung und Template-Management
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import hashlib
from dataclasses import dataclass
from enum import Enum

from core.architecture import (
    PromptTemplate, OptimizationResult, ABTestResult, 
    FeedbackEntry, PipelineResult
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyAction(Enum):
    """Policy-Aktionen"""
    PROMOTE = "promote"
    RETRY = "retry"
    EXPERIMENT = "experiment"
    RECALIBRATE = "recalibrate"
    MANUAL_REVIEW = "manual_review"

class PolicyTrigger(Enum):
    """Policy-Trigger"""
    SCORE_IMPROVEMENT = "score_improvement"
    SCORE_DECLINE = "score_decline"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"
    DRIFT_DETECTED = "drift_detected"
    TIME_BASED = "time_based"
    EXPERIMENT_COMPLETE = "experiment_complete"

@dataclass
class PolicyDecision:
    """Policy-Entscheidung"""
    action: PolicyAction
    trigger: PolicyTrigger
    confidence: float  # 0.0-1.0
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class TemplateScore:
    """Template-Score für Ranking"""
    template_hash: str
    quality_score: float
    user_rating: float
    feedback_count: int
    drift_score: float  # Abweichung von Vorversion
    age_days: int
    total_runs: int
    success_rate: float
    
    def calculate_weighted_score(self, weights: Dict[str, float]) -> float:
        """Berechnet gewichteten Gesamtscore"""
        return (
            self.quality_score * weights.get("quality", 0.4) +
            self.user_rating * weights.get("user_rating", 0.3) +
            (1.0 - self.drift_score) * weights.get("stability", 0.2) +
            self.success_rate * weights.get("reliability", 0.1)
        )

class PolicyEngine:
    """Policy Engine für automatische Prompt-Optimierung"""
    
    def __init__(self):
        self.policy_history = []
        self.template_scores = {}
        self.segment_performance = {}
        self.experiment_queue = []
        
        # Policy-Schwellenwerte
        self.thresholds = {
            "promotion_min_score": 0.8,
            "promotion_min_improvement": 0.1,
            "retry_threshold": 0.6,
            "drift_threshold": 0.15,
            "experiment_interval_days": 7,
            "manual_review_threshold": 0.3
        }
        
        # Scoring-Gewichte
        self.scoring_weights = {
            "quality": 0.4,
            "user_rating": 0.3,
            "stability": 0.2,
            "reliability": 0.1
        }
    
    def evaluate_pipeline_result(self, result: PipelineResult) -> PolicyDecision:
        """Evaluiert Pipeline-Ergebnis und trifft Policy-Entscheidung"""
        segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
        
        # Aktualisiere Segment-Performance
        self._update_segment_performance(segment, result)
        
        # Berechne Template-Score
        template_score = self._calculate_template_score(result)
        self.template_scores[result.generation_result.template_hash] = template_score
        
        # Prüfe verschiedene Trigger
        decisions = []
        
        # Score-Improvement Check
        if result.optimization_result and result.optimization_result.quality_score_delta > self.thresholds["promotion_min_improvement"]:
            decisions.append(self._create_promotion_decision(result, template_score))
        
        # Score-Decline Check
        if result.evaluation_result.overall_score < self.thresholds["retry_threshold"]:
            decisions.append(self._create_retry_decision(result, template_score))
        
        # Drift Detection
        if self._detect_drift(segment, result):
            decisions.append(self._create_drift_decision(result, template_score))
        
        # Feedback-basierte Entscheidungen
        if result.feedback_entries:
            feedback_decision = self._evaluate_feedback(result)
            if feedback_decision:
                decisions.append(feedback_decision)
        
        # Wähle beste Entscheidung basierend auf Priorität
        if decisions:
            best_decision = max(decisions, key=lambda d: d.confidence)
            self.policy_history.append(best_decision)
            return best_decision
        
        # Default: Keine Aktion
        return PolicyDecision(
            action=PolicyAction.PROMOTE,
            trigger=PolicyTrigger.SCORE_IMPROVEMENT,
            confidence=0.5,
            reasoning="Keine spezifischen Trigger erkannt, behalte aktuelles Template",
            metadata={"segment": segment}
        )
    
    def _update_segment_performance(self, segment: str, result: PipelineResult):
        """Aktualisiert Segment-Performance-Tracking"""
        if segment not in self.segment_performance:
            self.segment_performance[segment] = {
                "runs": [],
                "avg_score": 0.0,
                "last_update": datetime.now()
            }
        
        performance = self.segment_performance[segment]
        performance["runs"].append({
            "timestamp": datetime.now(),
            "score": result.evaluation_result.overall_score,
            "template_hash": result.generation_result.template_hash,
            "feedback_rating": self._calculate_avg_feedback_rating(result.feedback_entries)
        })
        
        # Behalte nur die letzten 50 Runs
        if len(performance["runs"]) > 50:
            performance["runs"] = performance["runs"][-50:]
        
        # Update durchschnittlichen Score
        scores = [run["score"] for run in performance["runs"]]
        performance["avg_score"] = sum(scores) / len(scores)
        performance["last_update"] = datetime.now()
    
    def _calculate_template_score(self, result: PipelineResult) -> TemplateScore:
        """Berechnet Template-Score für Ranking"""
        template_hash = result.generation_result.template_hash
        
        # Sammle historische Daten für dieses Template
        historical_runs = []
        for segment_data in self.segment_performance.values():
            for run in segment_data["runs"]:
                if run["template_hash"] == template_hash:
                    historical_runs.append(run)
        
        if not historical_runs:
            # Neues Template
            return TemplateScore(
                template_hash=template_hash,
                quality_score=result.evaluation_result.overall_score,
                user_rating=self._calculate_avg_feedback_rating(result.feedback_entries),
                feedback_count=len(result.feedback_entries),
                drift_score=0.0,
                age_days=0,
                total_runs=1,
                success_rate=1.0 if result.compliance_status != "failed" else 0.0
            )
        
        # Berechne Metriken
        quality_scores = [run["score"] for run in historical_runs]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        feedback_ratings = [run.get("feedback_rating", 0) for run in historical_runs if run.get("feedback_rating", 0) > 0]
        avg_user_rating = sum(feedback_ratings) / len(feedback_ratings) if feedback_ratings else 0
        
        # Drift-Score (Abweichung von durchschnittlichem Score)
        drift_score = abs(result.evaluation_result.overall_score - avg_quality)
        
        # Alter des Templates
        first_run = min(historical_runs, key=lambda r: r["timestamp"])
        age_days = (datetime.now() - first_run["timestamp"]).days
        
        # Erfolgsrate
        success_count = sum(1 for run in historical_runs if run.get("success", True))
        success_rate = success_count / len(historical_runs)
        
        return TemplateScore(
            template_hash=template_hash,
            quality_score=avg_quality,
            user_rating=avg_user_rating,
            feedback_count=len(feedback_ratings),
            drift_score=drift_score,
            age_days=age_days,
            total_runs=len(historical_runs),
            success_rate=success_rate
        )
    
    def _calculate_avg_feedback_rating(self, feedback_entries: List[FeedbackEntry]) -> float:
        """Berechnet durchschnittliches Feedback-Rating"""
        if not feedback_entries:
            return 0.0
        
        ratings = [entry.user_rating for entry in feedback_entries]
        return sum(ratings) / len(ratings)
    
    def _detect_drift(self, segment: str, result: PipelineResult) -> bool:
        """Erkennt Drift in Segment-Performance"""
        if segment not in self.segment_performance:
            return False
        
        performance = self.segment_performance[segment]
        current_score = result.evaluation_result.overall_score
        avg_score = performance["avg_score"]
        
        # Drift wenn aktueller Score signifikant unter Durchschnitt
        drift = avg_score - current_score
        return drift > self.thresholds["drift_threshold"]
    
    def _create_promotion_decision(self, result: PipelineResult, template_score: TemplateScore) -> PolicyDecision:
        """Erstellt Promotion-Entscheidung"""
        segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
        
        return PolicyDecision(
            action=PolicyAction.PROMOTE,
            trigger=PolicyTrigger.SCORE_IMPROVEMENT,
            confidence=min(0.9, 0.5 + result.optimization_result.quality_score_delta),
            reasoning=f"Signifikante Verbesserung erkannt: +{result.optimization_result.quality_score_delta:.3f}",
            metadata={
                "segment": segment,
                "improvement": result.optimization_result.quality_score_delta,
                "new_template_hash": result.optimization_result.optimized_prompt_hash
            }
        )
    
    def _create_retry_decision(self, result: PipelineResult, template_score: TemplateScore) -> PolicyDecision:
        """Erstellt Retry-Entscheidung"""
        segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
        
        return PolicyDecision(
            action=PolicyAction.RETRY,
            trigger=PolicyTrigger.SCORE_DECLINE,
            confidence=0.8,
            reasoning=f"Score unter Schwellenwert: {result.evaluation_result.overall_score:.3f} < {self.thresholds['retry_threshold']}",
            metadata={
                "segment": segment,
                "current_score": result.evaluation_result.overall_score,
                "threshold": self.thresholds["retry_threshold"]
            }
        )
    
    def _create_drift_decision(self, result: PipelineResult, template_score: TemplateScore) -> PolicyDecision:
        """Erstellt Drift-Entscheidung"""
        segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
        
        return PolicyDecision(
            action=PolicyAction.RECALIBRATE,
            trigger=PolicyTrigger.DRIFT_DETECTED,
            confidence=0.7,
            reasoning="Performance-Drift erkannt, Rekalibrierung erforderlich",
            metadata={
                "segment": segment,
                "drift_score": template_score.drift_score
            }
        )
    
    def _evaluate_feedback(self, result: PipelineResult) -> Optional[PolicyDecision]:
        """Evaluiert Feedback und erstellt entsprechende Entscheidung"""
        if not result.feedback_entries:
            return None
        
        avg_rating = self._calculate_avg_feedback_rating(result.feedback_entries)
        segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
        
        if avg_rating >= 4.0:
            # Positives Feedback
            return PolicyDecision(
                action=PolicyAction.PROMOTE,
                trigger=PolicyTrigger.FEEDBACK_POSITIVE,
                confidence=0.8,
                reasoning=f"Positives Nutzerfeedback: {avg_rating:.1f}/5.0",
                metadata={
                    "segment": segment,
                    "avg_rating": avg_rating,
                    "feedback_count": len(result.feedback_entries)
                }
            )
        elif avg_rating <= 2.0:
            # Negatives Feedback
            return PolicyDecision(
                action=PolicyAction.EXPERIMENT,
                trigger=PolicyTrigger.FEEDBACK_NEGATIVE,
                confidence=0.9,
                reasoning=f"Negatives Nutzerfeedback: {avg_rating:.1f}/5.0, Experiment erforderlich",
                metadata={
                    "segment": segment,
                    "avg_rating": avg_rating,
                    "feedback_count": len(result.feedback_entries)
                }
            )
        
        return None
    
    def get_active_template_ranking(self, segment: str) -> List[Tuple[str, float]]:
        """Gibt Ranking der aktiven Templates für ein Segment zurück"""
        segment_templates = []
        
        for template_hash, score in self.template_scores.items():
            # Prüfe ob Template für dieses Segment verwendet wurde
            if segment in self.segment_performance:
                segment_runs = self.segment_performance[segment]["runs"]
                template_used = any(run["template_hash"] == template_hash for run in segment_runs)
                
                if template_used:
                    weighted_score = score.calculate_weighted_score(self.scoring_weights)
                    segment_templates.append((template_hash, weighted_score))
        
        # Sortiere nach gewichtetem Score (höchste zuerst)
        segment_templates.sort(key=lambda x: x[1], reverse=True)
        return segment_templates
    
    def should_start_experiment(self, segment: str) -> bool:
        """Prüft ob ein neues Experiment gestartet werden sollte"""
        if segment not in self.segment_performance:
            return True  # Neues Segment
        
        performance = self.segment_performance[segment]
        last_update = performance["last_update"]
        
        # Prüfe Zeit-basierten Trigger
        days_since_update = (datetime.now() - last_update).days
        if days_since_update >= self.thresholds["experiment_interval_days"]:
            return True
        
        # Prüfe Performance-basierten Trigger
        recent_runs = [run for run in performance["runs"] 
                      if (datetime.now() - run["timestamp"]).days <= 7]
        
        if recent_runs:
            recent_avg = sum(run["score"] for run in recent_runs) / len(recent_runs)
            if recent_avg < self.thresholds["retry_threshold"]:
                return True
        
        return False
    
    def get_experiment_suggestions(self, segment: str) -> List[Dict[str, Any]]:
        """Generiert Experiment-Vorschläge für ein Segment"""
        suggestions = []
        
        # Vorschlag 1: Emotional Anchor Variation
        suggestions.append({
            "type": "emotional_anchor_variation",
            "description": "Verschiedene emotionale Anker testen",
            "variations": ["wonder", "courage", "friendship", "growth", "mystery"],
            "priority": "high"
        })
        
        # Vorschlag 2: Layer-Gewicht-Anpassung
        suggestions.append({
            "type": "layer_weight_adjustment",
            "description": "Layer-Gewichte optimieren",
            "variations": [
                {"emotion_drama": 1.5, "style": 1.3},
                {"target_audience": 1.4, "genre": 1.2},
                {"constraints": 1.3, "language": 1.1}
            ],
            "priority": "medium"
        })
        
        # Vorschlag 3: Few-Shot-Erweiterung
        suggestions.append({
            "type": "few_shot_expansion",
            "description": "Few-Shot-Beispiele erweitern",
            "variations": ["style_examples", "dialogue_examples", "emotion_examples"],
            "priority": "low"
        })
        
        return suggestions
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Gibt Policy-Zusammenfassung zurück"""
        return {
            "total_decisions": len(self.policy_history),
            "decision_distribution": self._get_decision_distribution(),
            "active_segments": len(self.segment_performance),
            "total_templates": len(self.template_scores),
            "recent_activity": self._get_recent_activity(),
            "thresholds": self.thresholds,
            "scoring_weights": self.scoring_weights
        }
    
    def _get_decision_distribution(self) -> Dict[str, int]:
        """Gibt Verteilung der Entscheidungen zurück"""
        distribution = {}
        for decision in self.policy_history:
            action = decision.action.value
            distribution[action] = distribution.get(action, 0) + 1
        return distribution
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Gibt aktuelle Aktivität zurück"""
        recent_decisions = [d for d in self.policy_history 
                          if (datetime.now() - d.timestamp).days <= 7]
        
        return {
            "recent_decisions": len(recent_decisions),
            "segments_with_activity": len(set(d.metadata.get("segment", "") for d in recent_decisions)),
            "avg_confidence": sum(d.confidence for d in recent_decisions) / max(len(recent_decisions), 1)
        } 