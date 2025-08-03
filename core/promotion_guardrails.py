#!/usr/bin/env python3
"""
Promotion Guardrails Module
Sicherheitsmechanismen für Template-Promotion in der Policy Engine
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from statistics import mean, stdev
from core.security import secure_log

logger = logging.getLogger(__name__)

class PromotionStatus(str, Enum):
    """Status einer Promotion"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    COOLDOWN = "cooldown"
    INSUFFICIENT_SCORE = "insufficient_score"
    UNSTABLE = "unstable"

@dataclass
class PromotionRequest:
    """Promotion-Request"""
    template_id: str
    template_version: str
    quality_score: float
    user_feedback_score: float
    timestamp: float
    segment: str
    metadata: Dict[str, Any]

@dataclass
class PromotionResult:
    """Promotion-Ergebnis"""
    status: PromotionStatus
    approved: bool
    reason: str
    cooldown_remaining: Optional[float] = None
    score_delta: Optional[float] = None
    stability_score: Optional[float] = None
    recommendations: List[str] = None

class PromotionGuardrails:
    """Guardrails für Template-Promotion"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialisiert die Promotion Guardrails
        
        Args:
            config: Konfiguration für Guardrails
        """
        self.config = config or self._get_default_config()
        self.promotion_history: Dict[str, List[PromotionRequest]] = {}
        self.last_promotion_time: Dict[str, float] = {}
        self.score_history: Dict[str, List[float]] = {}
        
        secure_log("Promotion Guardrails initialisiert")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Gibt Standard-Konfiguration zurück"""
        return {
            "cooldown_hours": 24,  # Cooldown zwischen Promotions
            "min_quality_score": 0.7,  # Mindest-Quality-Score
            "min_feedback_score": 0.6,  # Mindest-Feedback-Score
            "stability_window": 10,  # Anzahl Scores für Stabilitätsprüfung
            "stability_threshold": 0.1,  # Max. Standardabweichung für Stabilität
            "min_score_count": 5,  # Mindestanzahl Scores für Stabilitätsprüfung
            "score_weight": 0.7,  # Gewichtung Quality-Score
            "feedback_weight": 0.3,  # Gewichtung Feedback-Score
        }
    
    def check_promotion_eligibility(self, request: PromotionRequest) -> PromotionResult:
        """
        Prüft ob eine Promotion erlaubt ist
        
        Args:
            request: Promotion-Request
            
        Returns:
            PromotionResult mit Entscheidung
        """
        try:
            # 1. Cooldown-Check
            cooldown_result = self._check_cooldown(request.template_id)
            if not cooldown_result[0]:
                # AUFZEICHNUNG: Auch abgelehnte Promotions aufzeichnen
                self._record_promotion_attempt(request, "cooldown")
                return PromotionResult(
                    status=PromotionStatus.COOLDOWN,
                    approved=False,
                    reason=f"Cooldown aktiv: {cooldown_result[1]:.1f} Stunden verbleibend",
                    cooldown_remaining=cooldown_result[1]
                )
            
            # 2. Quality-Score-Check
            score_result = self._check_quality_score(request)
            if not score_result[0]:
                # AUFZEICHNUNG: Auch abgelehnte Promotions aufzeichnen
                self._record_promotion_attempt(request, "insufficient_score")
                return PromotionResult(
                    status=PromotionStatus.INSUFFICIENT_SCORE,
                    approved=False,
                    reason=f"Unzureichender Score: {request.quality_score:.3f} < {self.config['min_quality_score']:.3f}",
                    score_delta=request.quality_score - self.config['min_quality_score']
                )
            
            # 3. Stabilitäts-Check
            stability_result = self._check_stability(request.template_id)
            if not stability_result[0]:
                # AUFZEICHNUNG: Auch abgelehnte Promotions aufzeichnen
                self._record_promotion_attempt(request, "unstable")
                return PromotionResult(
                    status=PromotionStatus.UNSTABLE,
                    approved=False,
                    reason=f"Instabile Scores: StdDev {stability_result[1]:.3f} > {self.config['stability_threshold']:.3f}",
                    stability_score=stability_result[1]
                )
            
            # 4. Kombinierter Score-Check
            combined_score = self._calculate_combined_score(request)
            min_combined_score = (
                self.config['score_weight'] * self.config['min_quality_score'] +
                self.config['feedback_weight'] * self.config['min_feedback_score']
            )
            
            if combined_score < min_combined_score:
                # AUFZEICHNUNG: Auch abgelehnte Promotions aufzeichnen
                self._record_promotion_attempt(request, "insufficient_combined_score")
                return PromotionResult(
                    status=PromotionStatus.INSUFFICIENT_SCORE,
                    approved=False,
                    reason=f"Unzureichender kombinierter Score: {combined_score:.3f} < {min_combined_score:.3f}",
                    score_delta=combined_score - min_combined_score
                )
            
            # 5. Promotion genehmigt
            self._record_promotion(request)
            
            recommendations = self._generate_recommendations(request)
            
            return PromotionResult(
                status=PromotionStatus.APPROVED,
                approved=True,
                reason="Promotion genehmigt - alle Kriterien erfüllt",
                score_delta=combined_score - min_combined_score,
                stability_score=stability_result[1],
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.exception(f"Fehler bei Promotion-Check: {e}")
            # AUFZEICHNUNG: Auch fehlgeschlagene Promotions aufzeichnen
            self._record_promotion_attempt(request, "error")
            return PromotionResult(
                status=PromotionStatus.REJECTED,
                approved=False,
                reason=f"Systemfehler: {e}"
            )
    
    def _check_cooldown(self, template_id: str) -> Tuple[bool, float]:
        """
        Prüft Cooldown für Template
        
        Args:
            template_id: Template ID
            
        Returns:
            (erlaubt, verbleibende Stunden)
        """
        if template_id not in self.last_promotion_time:
            return True, 0.0
        
        last_promotion = self.last_promotion_time[template_id]
        current_time = time.time()
        hours_since_last = (current_time - last_promotion) / 3600
        
        cooldown_hours = self.config['cooldown_hours']
        remaining_hours = max(0, cooldown_hours - hours_since_last)
        
        return remaining_hours <= 0, remaining_hours
    
    def _check_quality_score(self, request: PromotionRequest) -> Tuple[bool, float]:
        """
        Prüft Quality-Score
        
        Args:
            request: Promotion-Request
            
        Returns:
            (erfüllt, Score-Delta)
        """
        min_score = self.config['min_quality_score']
        score_delta = request.quality_score - min_score
        
        return request.quality_score >= min_score, score_delta
    
    def _check_stability(self, template_id: str) -> Tuple[bool, float]:
        """
        Prüft Stabilität der Scores
        
        Args:
            template_id: Template ID
            
        Returns:
            (stabil, Standardabweichung)
        """
        if template_id not in self.score_history:
            return True, 0.0
        
        scores = self.score_history[template_id]
        if len(scores) < self.config['min_score_count']:
            return True, 0.0
        
        # Verwende nur die letzten N Scores
        recent_scores = scores[-self.config['stability_window']:]
        
        if len(recent_scores) < 2:
            return True, 0.0
        
        std_dev = stdev(recent_scores)
        threshold = self.config['stability_threshold']
        
        return std_dev <= threshold, std_dev
    
    def _calculate_combined_score(self, request: PromotionRequest) -> float:
        """
        Berechnet kombinierten Score
        
        Args:
            request: Promotion-Request
            
        Returns:
            Kombinierter Score
        """
        quality_weight = self.config['score_weight']
        feedback_weight = self.config['feedback_weight']
        
        combined_score = (
            quality_weight * request.quality_score +
            feedback_weight * request.user_feedback_score
        )
        
        return combined_score
    
    def _record_promotion_attempt(self, request: PromotionRequest, reason: str) -> None:
        """
        Zeichnet einen Promotion-Versuch auf (auch abgelehnte)
        
        Args:
            request: Promotion-Request
            reason: Grund für Ablehnung
        """
        template_id = request.template_id
        
        # Füge zu History hinzu (auch abgelehnte Versuche)
        if template_id not in self.promotion_history:
            self.promotion_history[template_id] = []
        
        # Erstelle modifizierten Request mit Ablehnungsgrund
        attempt_request = PromotionRequest(
            template_id=request.template_id,
            template_version=request.template_version,
            quality_score=request.quality_score,
            user_feedback_score=request.user_feedback_score,
            timestamp=request.timestamp,
            segment=request.segment,
            metadata={**request.metadata, "rejection_reason": reason, "approved": False}
        )
        
        self.promotion_history[template_id].append(attempt_request)
        
        # Aktualisiere Score-History (auch für abgelehnte Versuche)
        if template_id not in self.score_history:
            self.score_history[template_id] = []
        
        self.score_history[template_id].append(request.quality_score)
        
        # Behalte nur die letzten N Scores
        max_scores = self.config['stability_window'] * 2
        if len(self.score_history[template_id]) > max_scores:
            self.score_history[template_id] = self.score_history[template_id][-max_scores:]
        
        secure_log(f"Promotion-Versuch für Template {template_id} aufgezeichnet (Grund: {reason})")
    
    def _record_promotion(self, request: PromotionRequest) -> None:
        """
        Zeichnet eine genehmigte Promotion auf
        
        Args:
            request: Promotion-Request
        """
        template_id = request.template_id
        
        # Aktualisiere Promotion-Zeit
        self.last_promotion_time[template_id] = request.timestamp
        
        # Füge zu History hinzu
        if template_id not in self.promotion_history:
            self.promotion_history[template_id] = []
        
        # Erstelle modifizierten Request mit Genehmigungsstatus
        approved_request = PromotionRequest(
            template_id=request.template_id,
            template_version=request.template_version,
            quality_score=request.quality_score,
            user_feedback_score=request.user_feedback_score,
            timestamp=request.timestamp,
            segment=request.segment,
            metadata={**request.metadata, "approved": True}
        )
        
        self.promotion_history[template_id].append(approved_request)
        
        # Aktualisiere Score-History
        if template_id not in self.score_history:
            self.score_history[template_id] = []
        
        self.score_history[template_id].append(request.quality_score)
        
        # Behalte nur die letzten N Scores
        max_scores = self.config['stability_window'] * 2
        if len(self.score_history[template_id]) > max_scores:
            self.score_history[template_id] = self.score_history[template_id][-max_scores:]
        
        secure_log(f"Promotion für Template {template_id} aufgezeichnet")
    
    def _generate_recommendations(self, request: PromotionRequest) -> List[str]:
        """
        Generiert Empfehlungen für Template
        
        Args:
            request: Promotion-Request
            
        Returns:
            Liste von Empfehlungen
        """
        recommendations = []
        
        # Score-basierte Empfehlungen
        if request.quality_score > 0.9:
            recommendations.append("Hervorragender Score - Template als Best Practice markieren")
        elif request.quality_score < 0.8:
            recommendations.append("Score verbesserungswürdig - weitere Optimierung empfohlen")
        
        # Feedback-basierte Empfehlungen
        if request.user_feedback_score > 0.8:
            recommendations.append("Sehr positives Feedback - für ähnliche Segmente empfehlen")
        elif request.user_feedback_score < 0.7:
            recommendations.append("Feedback verbesserungswürdig - Nutzerzufriedenheit erhöhen")
        
        # Stabilitäts-basierte Empfehlungen
        if request.template_id in self.score_history:
            scores = self.score_history[request.template_id]
            if len(scores) >= 5:
                avg_score = mean(scores[-5:])
                if avg_score > request.quality_score:
                    recommendations.append("Score unter Durchschnitt - Konsistenz verbessern")
        
        return recommendations
    
    def get_promotion_stats(self, template_id: str) -> Dict[str, Any]:
        """
        Gibt Promotions-Statistiken zurück
        
        Args:
            template_id: Template ID
            
        Returns:
            Statistiken
        """
        stats = {
            "total_promotions": 0,
            "last_promotion": None,
            "avg_quality_score": 0.0,
            "avg_feedback_score": 0.0,
            "stability_score": 0.0,
            "success_rate": 0.0
        }
        
        if template_id in self.promotion_history:
            history = self.promotion_history[template_id]
            stats["total_promotions"] = len(history)
            
            if history:
                stats["last_promotion"] = max(req.timestamp for req in history)
                stats["avg_quality_score"] = mean(req.quality_score for req in history)
                stats["avg_feedback_score"] = mean(req.user_feedback_score for req in history)
        
        if template_id in self.score_history:
            scores = self.score_history[template_id]
            if len(scores) >= 2:
                stats["stability_score"] = stdev(scores)
        
        return stats
    
    def reset_cooldown(self, template_id: str) -> bool:
        """
        Setzt Cooldown für Template zurück
        
        Args:
            template_id: Template ID
            
        Returns:
            True wenn erfolgreich
        """
        try:
            if template_id in self.last_promotion_time:
                del self.last_promotion_time[template_id]
                secure_log(f"Cooldown für Template {template_id} zurückgesetzt")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Zurücksetzen des Cooldowns: {e}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Aktualisiert Konfiguration
        
        Args:
            new_config: Neue Konfiguration
            
        Returns:
            True wenn erfolgreich
        """
        try:
            self.config.update(new_config)
            secure_log("Promotion Guardrails Konfiguration aktualisiert")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Konfiguration: {e}")
            return False

# Globaler Guardrails-Instanz
promotion_guardrails = PromotionGuardrails()

def check_promotion_eligibility(request: PromotionRequest) -> PromotionResult:
    """Globale Funktion für Promotion-Check"""
    return promotion_guardrails.check_promotion_eligibility(request)

def get_promotion_stats(template_id: str) -> Dict[str, Any]:
    """Globale Funktion für Promotions-Statistiken"""
    return promotion_guardrails.get_promotion_stats(template_id) 