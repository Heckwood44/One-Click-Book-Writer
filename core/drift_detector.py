#!/usr/bin/env python3
"""
Drift Detector
Überwachung und automatische Rekalibrierung bei Performance-Drift
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import statistics
from dataclasses import dataclass
from enum import Enum

from core.architecture import PipelineResult, PromptTemplate
from core.layered_compiler import LayeredCompositionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftType(Enum):
    """Drift-Typen"""
    SCORE_DECLINE = "score_decline"
    FEEDBACK_DECLINE = "feedback_decline"
    CONSISTENCY_LOSS = "consistency_loss"
    TEMPLATE_AGING = "template_aging"
    SEGMENT_DRIFT = "segment_drift"

@dataclass
class DriftAlert:
    """Drift-Alert"""
    drift_type: DriftType
    segment: str
    severity: str  # low, medium, high, critical
    current_value: float
    baseline_value: float
    drift_percentage: float
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class CalibrationResult:
    """Rekalibrierungs-Ergebnis"""
    success: bool
    original_template_hash: str
    recalibrated_template_hash: str
    adjustments_made: List[str]
    performance_improvement: float
    metadata: Dict[str, Any]

class DriftDetector:
    """Drift Detection und Rekalibrierung"""
    
    def __init__(self):
        self.segment_history = {}
        self.drift_alerts = []
        self.calibration_history = []
        self.compiler = LayeredCompositionEngine()
        
        # Drift-Schwellenwerte
        self.drift_thresholds = {
            "score_decline": 0.15,  # 15% Score-Rückgang
            "feedback_decline": 0.20,  # 20% Feedback-Rückgang
            "consistency_threshold": 0.25,  # 25% Varianz
            "aging_threshold_days": 30,  # 30 Tage Template-Alter
            "segment_drift_threshold": 0.10  # 10% Segment-Drift
        }
        
        # Rekalibrierungs-Strategien
        self.recalibration_strategies = {
            "layer_weight_adjustment": {
                "description": "Layer-Gewichte anpassen",
                "priority": "high"
            },
            "few_shot_addition": {
                "description": "Few-Shot-Beispiele hinzufügen",
                "priority": "medium"
            },
            "style_anchor_update": {
                "description": "Style-Anker aktualisieren",
                "priority": "medium"
            },
            "constraint_relaxation": {
                "description": "Constraints lockern",
                "priority": "low"
            }
        }
    
    def monitor_pipeline_result(self, result: PipelineResult) -> List[DriftAlert]:
        """Überwacht Pipeline-Ergebnis auf Drift"""
        segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
        alerts = []
        
        # Aktualisiere Segment-Historie
        self._update_segment_history(segment, result)
        
        # Prüfe verschiedene Drift-Typen
        alerts.extend(self._check_score_drift(segment, result))
        alerts.extend(self._check_feedback_drift(segment, result))
        alerts.extend(self._check_consistency_drift(segment, result))
        alerts.extend(self._check_template_aging(segment, result))
        alerts.extend(self._check_segment_drift(segment, result))
        
        # Speichere Alerts
        self.drift_alerts.extend(alerts)
        
        return alerts
    
    def _update_segment_history(self, segment: str, result: PipelineResult):
        """Aktualisiert Segment-Historie"""
        if segment not in self.segment_history:
            self.segment_history[segment] = {
                "runs": [],
                "baseline_score": None,
                "baseline_feedback": None,
                "template_versions": {},
                "last_calibration": None
            }
        
        history = self.segment_history[segment]
        
        # Füge Run hinzu
        run_data = {
            "timestamp": datetime.now(),
            "score": result.evaluation_result.overall_score,
            "template_hash": result.generation_result.template_hash,
            "feedback_rating": self._calculate_avg_feedback_rating(result.feedback_entries),
            "word_count": result.generation_result.word_count,
            "execution_time": result.execution_time
        }
        
        history["runs"].append(run_data)
        
        # Behalte nur die letzten 100 Runs
        if len(history["runs"]) > 100:
            history["runs"] = history["runs"][-100:]
        
        # Update Baseline nach 10 Runs
        if len(history["runs"]) >= 10 and history["baseline_score"] is None:
            baseline_runs = history["runs"][:10]
            history["baseline_score"] = statistics.mean(run["score"] for run in baseline_runs)
            history["baseline_feedback"] = statistics.mean(run["feedback_rating"] for run in baseline_runs if run["feedback_rating"] > 0)
        
        # Update Template-Versionen
        template_hash = result.generation_result.template_hash
        if template_hash not in history["template_versions"]:
            history["template_versions"][template_hash] = {
                "first_used": datetime.now(),
                "runs_count": 0,
                "avg_score": 0.0
            }
        
        template_version = history["template_versions"][template_hash]
        template_version["runs_count"] += 1
        
        # Update durchschnittlichen Score für Template
        template_runs = [run for run in history["runs"] if run["template_hash"] == template_hash]
        template_version["avg_score"] = statistics.mean(run["score"] for run in template_runs)
    
    def _check_score_drift(self, segment: str, result: PipelineResult) -> List[DriftAlert]:
        """Prüft Score-Drift"""
        alerts = []
        history = self.segment_history[segment]
        
        if history["baseline_score"] is None:
            return alerts
        
        current_score = result.evaluation_result.overall_score
        baseline_score = history["baseline_score"]
        
        if current_score < baseline_score:
            decline_percentage = (baseline_score - current_score) / baseline_score
            
            if decline_percentage > self.drift_thresholds["score_decline"]:
                severity = self._determine_severity(decline_percentage, 0.15, 0.25, 0.35)
                
                alerts.append(DriftAlert(
                    drift_type=DriftType.SCORE_DECLINE,
                    segment=segment,
                    severity=severity,
                    current_value=current_score,
                    baseline_value=baseline_score,
                    drift_percentage=decline_percentage,
                    confidence=min(0.9, decline_percentage * 2),
                    timestamp=datetime.now(),
                    metadata={
                        "template_hash": result.generation_result.template_hash,
                        "recent_runs": len([r for r in history["runs"] if (datetime.now() - r["timestamp"]).days <= 7])
                    }
                ))
        
        return alerts
    
    def _check_feedback_drift(self, segment: str, result: PipelineResult) -> List[DriftAlert]:
        """Prüft Feedback-Drift"""
        alerts = []
        history = self.segment_history[segment]
        
        if history["baseline_feedback"] is None:
            return alerts
        
        current_feedback = self._calculate_avg_feedback_rating(result.feedback_entries)
        
        if current_feedback > 0 and current_feedback < history["baseline_feedback"]:
            decline_percentage = (history["baseline_feedback"] - current_feedback) / history["baseline_feedback"]
            
            if decline_percentage > self.drift_thresholds["feedback_decline"]:
                severity = self._determine_severity(decline_percentage, 0.20, 0.30, 0.40)
                
                alerts.append(DriftAlert(
                    drift_type=DriftType.FEEDBACK_DECLINE,
                    segment=segment,
                    severity=severity,
                    current_value=current_feedback,
                    baseline_value=history["baseline_feedback"],
                    drift_percentage=decline_percentage,
                    confidence=min(0.8, decline_percentage * 1.5),
                    timestamp=datetime.now(),
                    metadata={
                        "feedback_count": len(result.feedback_entries),
                        "template_hash": result.generation_result.template_hash
                    }
                ))
        
        return alerts
    
    def _check_consistency_drift(self, segment: str, result: PipelineResult) -> List[DriftAlert]:
        """Prüft Konsistenz-Drift"""
        alerts = []
        history = self.segment_history[segment]
        
        if len(history["runs"]) < 10:
            return alerts
        
        # Berechne Varianz der letzten 10 Runs
        recent_scores = [run["score"] for run in history["runs"][-10:]]
        variance = statistics.variance(recent_scores)
        mean_score = statistics.mean(recent_scores)
        
        if mean_score > 0:
            coefficient_of_variation = (variance ** 0.5) / mean_score
            
            if coefficient_of_variation > self.drift_thresholds["consistency_threshold"]:
                alerts.append(DriftAlert(
                    drift_type=DriftType.CONSISTENCY_LOSS,
                    segment=segment,
                    severity="medium",
                    current_value=coefficient_of_variation,
                    baseline_value=self.drift_thresholds["consistency_threshold"],
                    drift_percentage=coefficient_of_variation - self.drift_thresholds["consistency_threshold"],
                    confidence=0.7,
                    timestamp=datetime.now(),
                    metadata={
                        "variance": variance,
                        "mean_score": mean_score,
                        "recent_scores": recent_scores
                    }
                ))
        
        return alerts
    
    def _check_template_aging(self, segment: str, result: PipelineResult) -> List[DriftAlert]:
        """Prüft Template-Aging"""
        alerts = []
        history = self.segment_history[segment]
        template_hash = result.generation_result.template_hash
        
        if template_hash in history["template_versions"]:
            template_version = history["template_versions"][template_hash]
            age_days = (datetime.now() - template_version["first_used"]).days
            
            if age_days > self.drift_thresholds["aging_threshold_days"]:
                alerts.append(DriftAlert(
                    drift_type=DriftType.TEMPLATE_AGING,
                    segment=segment,
                    severity="low",
                    current_value=age_days,
                    baseline_value=self.drift_thresholds["aging_threshold_days"],
                    drift_percentage=age_days - self.drift_thresholds["aging_threshold_days"],
                    confidence=0.6,
                    timestamp=datetime.now(),
                    metadata={
                        "template_hash": template_hash,
                        "runs_count": template_version["runs_count"],
                        "avg_score": template_version["avg_score"]
                    }
                ))
        
        return alerts
    
    def _check_segment_drift(self, segment: str, result: PipelineResult) -> List[DriftAlert]:
        """Prüft Segment-Drift im Vergleich zu anderen Segmenten"""
        alerts = []
        
        if len(self.segment_history) < 2:
            return alerts
        
        # Berechne durchschnittlichen Score aller Segmente
        all_segments_avg = []
        for seg, history in self.segment_history.items():
            if history["runs"]:
                recent_scores = [run["score"] for run in history["runs"][-10:]]
                if recent_scores:
                    all_segments_avg.append(statistics.mean(recent_scores))
        
        if all_segments_avg:
            global_avg = statistics.mean(all_segments_avg)
            current_score = result.evaluation_result.overall_score
            
            if current_score < global_avg:
                drift_percentage = (global_avg - current_score) / global_avg
                
                if drift_percentage > self.drift_thresholds["segment_drift_threshold"]:
                    alerts.append(DriftAlert(
                        drift_type=DriftType.SEGMENT_DRIFT,
                        segment=segment,
                        severity="medium",
                        current_value=current_score,
                        baseline_value=global_avg,
                        drift_percentage=drift_percentage,
                        confidence=0.7,
                        timestamp=datetime.now(),
                        metadata={
                            "global_avg": global_avg,
                            "segment_count": len(self.segment_history)
                        }
                    ))
        
        return alerts
    
    def _determine_severity(self, value: float, low_threshold: float, medium_threshold: float, high_threshold: float) -> str:
        """Bestimmt Schweregrad basierend auf Schwellenwerten"""
        if value >= high_threshold:
            return "critical"
        elif value >= medium_threshold:
            return "high"
        elif value >= low_threshold:
            return "medium"
        else:
            return "low"
    
    def _calculate_avg_feedback_rating(self, feedback_entries) -> float:
        """Berechnet durchschnittliches Feedback-Rating"""
        if not feedback_entries:
            return 0.0
        
        ratings = [entry.user_rating for entry in feedback_entries]
        return sum(ratings) / len(ratings)
    
    def trigger_recalibration(self, alert: DriftAlert) -> CalibrationResult:
        """Löst Rekalibrierung basierend auf Drift-Alert aus"""
        segment = alert.segment
        history = self.segment_history[segment]
        
        # Wähle Rekalibrierungs-Strategie basierend auf Drift-Typ
        strategy = self._select_recalibration_strategy(alert)
        
        try:
            # Führe Rekalibrierung durch
            recalibrated_template = self._perform_recalibration(segment, strategy, alert)
            
            # Erstelle Calibration-Result
            result = CalibrationResult(
                success=True,
                original_template_hash=alert.metadata.get("template_hash", ""),
                recalibrated_template_hash=recalibrated_template.get_hash() if recalibrated_template else "",
                adjustments_made=[strategy["description"]],
                performance_improvement=0.0,  # Wird später gemessen
                metadata={
                    "drift_type": alert.drift_type.value,
                    "strategy": strategy,
                    "segment": segment
                }
            )
            
            # Update Kalibrierungs-Historie
            history["last_calibration"] = datetime.now()
            self.calibration_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Rekalibrierung fehlgeschlagen: {e}")
            
            return CalibrationResult(
                success=False,
                original_template_hash=alert.metadata.get("template_hash", ""),
                recalibrated_template_hash="",
                adjustments_made=[],
                performance_improvement=0.0,
                metadata={
                    "error": str(e),
                    "drift_type": alert.drift_type.value,
                    "segment": segment
                }
            )
    
    def _select_recalibration_strategy(self, alert: DriftAlert) -> Dict[str, Any]:
        """Wählt Rekalibrierungs-Strategie basierend auf Drift-Typ"""
        if alert.drift_type == DriftType.SCORE_DECLINE:
            return self.recalibration_strategies["layer_weight_adjustment"]
        elif alert.drift_type == DriftType.FEEDBACK_DECLINE:
            return self.recalibration_strategies["few_shot_addition"]
        elif alert.drift_type == DriftType.CONSISTENCY_LOSS:
            return self.recalibration_strategies["style_anchor_update"]
        elif alert.drift_type == DriftType.TEMPLATE_AGING:
            return self.recalibration_strategies["constraint_relaxation"]
        else:
            return self.recalibration_strategies["layer_weight_adjustment"]
    
    def _perform_recalibration(self, segment: str, strategy: Dict[str, Any], alert: DriftAlert) -> Optional[PromptTemplate]:
        """Führt Rekalibrierung durch"""
        # Extrahiere Segment-Informationen
        age_group, genre = segment.split("_", 1)
        
        # Erstelle Basis-PromptFrame
        from core.architecture import PromptFrame
        prompt_frame = PromptFrame(
            age_group=age_group,
            genre=genre,
            emotion="courage",  # Default, könnte angepasst werden
            language="de"
        )
        
        # Erstelle Basis-Template
        base_template = self.compiler.compile_template(prompt_frame)
        
        # Wende Rekalibrierungs-Strategie an
        if strategy["description"] == "Layer-Gewichte anpassen":
            return self._adjust_layer_weights(base_template, alert)
        elif strategy["description"] == "Few-Shot-Beispiele hinzufügen":
            return self._add_few_shot_examples(base_template, alert)
        elif strategy["description"] == "Style-Anker aktualisieren":
            return self._update_style_anchors(base_template, alert)
        elif strategy["description"] == "Constraints lockern":
            return self._relax_constraints(base_template, alert)
        
        return base_template
    
    def _adjust_layer_weights(self, template: PromptTemplate, alert: DriftAlert) -> PromptTemplate:
        """Passt Layer-Gewichte an"""
        # Erstelle neue Layer mit angepassten Gewichten
        adjusted_layers = []
        
        for layer in template.layers:
            # Erhöhe Gewicht für wichtige Layer basierend auf Drift-Typ
            if alert.drift_type == DriftType.SCORE_DECLINE:
                if layer.layer_type.value in ["emotion_drama", "style"]:
                    adjusted_weight = layer.weight * 1.2
                else:
                    adjusted_weight = layer.weight
            else:
                adjusted_weight = layer.weight
            
            # Erstelle neuen Layer mit angepasstem Gewicht
            from core.architecture import Layer
            adjusted_layer = Layer(
                layer_type=layer.layer_type,
                content=layer.content,
                weight=adjusted_weight,
                version=f"{layer.version}_recalibrated",
                metadata=layer.metadata
            )
            adjusted_layers.append(adjusted_layer)
        
        # Erstelle neues Template
        from core.architecture import PromptTemplate
        return PromptTemplate(
            template_id=f"{template.template_id}_recalibrated",
            name=f"{template.name} (Rekalibriert)",
            description=f"Rekalibriertes Template für {alert.drift_type.value}",
            layers=adjusted_layers,
            version=f"{template.version}_recalibrated",
            metadata={
                "original_template": template.template_id,
                "recalibration_reason": alert.drift_type.value,
                "recalibration_timestamp": datetime.now().isoformat()
            }
        )
    
    def _add_few_shot_examples(self, template: PromptTemplate, alert: DriftAlert) -> PromptTemplate:
        """Fügt Few-Shot-Beispiele hinzu"""
        # Vereinfachte Implementierung - in der Praxis würden hier echte Few-Shot-Beispiele hinzugefügt
        return template
    
    def _update_style_anchors(self, template: PromptTemplate, alert: DriftAlert) -> PromptTemplate:
        """Aktualisiert Style-Anker"""
        # Vereinfachte Implementierung - in der Praxis würden hier Style-Anker aktualisiert
        return template
    
    def _relax_constraints(self, template: PromptTemplate, alert: DriftAlert) -> PromptTemplate:
        """Lockert Constraints"""
        # Vereinfachte Implementierung - in der Praxis würden hier Constraints gelockert
        return template
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Gibt Drift-Zusammenfassung zurück"""
        return {
            "total_alerts": len(self.drift_alerts),
            "active_segments": len(self.segment_history),
            "recent_alerts": len([a for a in self.drift_alerts if (datetime.now() - a.timestamp).days <= 7]),
            "calibration_count": len(self.calibration_history),
            "drift_distribution": self._get_drift_distribution(),
            "thresholds": self.drift_thresholds
        }
    
    def _get_drift_distribution(self) -> Dict[str, int]:
        """Gibt Verteilung der Drift-Typen zurück"""
        distribution = {}
        for alert in self.drift_alerts:
            drift_type = alert.drift_type.value
            distribution[drift_type] = distribution.get(drift_type, 0) + 1
        return distribution 