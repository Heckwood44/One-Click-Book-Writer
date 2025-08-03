#!/usr/bin/env python3
"""
Production Monitoring Service
Kontinuierliche Überwachung und Drift-Alerting für das Framework
"""

import json
import logging
import asyncio
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os

from core.architecture import PipelineResult
from core.policy_engine import PolicyEngine
from core.drift_detector import DriftDetector
from core.feedback_intelligence import FeedbackIntelligence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertType(Enum):
    """Alert-Typen"""
    QUALITY_SCORE_DECLINE = "quality_score_decline"
    FEEDBACK_DIVERGENCE = "feedback_divergence"
    TEMPLATE_DRIFT = "template_drift"
    HIGH_LATENCY = "high_latency"
    ERROR_SPIKE = "error_spike"
    NEW_DRIFT_PATTERN = "new_drift_pattern"

class AlertSeverity(Enum):
    """Alert-Schweregrade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MonitoringAlert:
    """Monitoring-Alert"""
    alert_type: AlertType
    severity: AlertSeverity
    segment: str
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    metadata: Dict[str, Any]

class MonitoringService:
    """Produktions-Monitoring-Service"""
    
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.drift_detector = DriftDetector()
        self.feedback_intelligence = FeedbackIntelligence()
        
        # Monitoring-Konfiguration
        self.monitoring_config = {
            "quality_score_threshold": float(os.getenv("QUALITY_SCORE_THRESHOLD", "0.7")),
            "feedback_correlation_threshold": float(os.getenv("FEEDBACK_CORRELATION_THRESHOLD", "0.6")),
            "latency_threshold_seconds": float(os.getenv("LATENCY_THRESHOLD_SECONDS", "30.0")),
            "error_rate_threshold": float(os.getenv("ERROR_RATE_THRESHOLD", "0.1")),
            "drift_detection_interval_minutes": int(os.getenv("DRIFT_DETECTION_INTERVAL_MINUTES", "15")),
            "alert_cooldown_minutes": int(os.getenv("ALERT_COOLDOWN_MINUTES", "60"))
        }
        
        # Alert-Historie für Cooldown
        self.alert_history = {}
        
        # Monitoring-Daten
        self.monitoring_data = {
            "segments": {},
            "global_metrics": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_latency": 0.0,
                "average_quality_score": 0.0,
                "total_feedback": 0
            },
            "alerts": []
        }
        
        # Alert-Channels
        self.alert_channels = {
            "slack": self._send_slack_alert,
            "email": self._send_email_alert,
            "log": self._log_alert
        }
        
        # Aktiviere Alert-Channels basierend auf Konfiguration
        self.enabled_channels = []
        if os.getenv("SLACK_WEBHOOK_URL"):
            self.enabled_channels.append("slack")
        if os.getenv("EMAIL_SMTP_HOST"):
            self.enabled_channels.append("email")
        self.enabled_channels.append("log")  # Log ist immer aktiv
    
    async def start_monitoring(self):
        """Startet kontinuierliches Monitoring"""
        logger.info("Starting production monitoring service...")
        
        # Starte Monitoring-Tasks
        tasks = [
            asyncio.create_task(self._continuous_drift_monitoring()),
            asyncio.create_task(self._performance_monitoring()),
            asyncio.create_task(self._feedback_monitoring()),
            asyncio.create_task(self._metrics_collection())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Monitoring service error: {e}")
    
    async def process_pipeline_result(self, result: PipelineResult):
        """Verarbeitet Pipeline-Ergebnis für Monitoring"""
        try:
            segment = f"{result.prompt_frame.age_group}_{result.prompt_frame.genre}"
            
            # Update Segment-Daten
            if segment not in self.monitoring_data["segments"]:
                self.monitoring_data["segments"][segment] = {
                    "requests": [],
                    "quality_scores": [],
                    "latencies": [],
                    "feedback_ratings": [],
                    "last_update": datetime.now()
                }
            
            segment_data = self.monitoring_data["segments"][segment]
            
            # Füge Request hinzu
            request_data = {
                "timestamp": datetime.now(),
                "run_id": result.run_id,
                "quality_score": result.evaluation_result.overall_score,
                "latency": result.execution_time,
                "success": result.compliance_status != "failed",
                "template_hash": result.generation_result.template_hash
            }
            
            segment_data["requests"].append(request_data)
            segment_data["quality_scores"].append(result.evaluation_result.overall_score)
            segment_data["latencies"].append(result.execution_time)
            
            # Behalte nur die letzten 100 Requests
            if len(segment_data["requests"]) > 100:
                segment_data["requests"] = segment_data["requests"][-100:]
                segment_data["quality_scores"] = segment_data["quality_scores"][-100:]
                segment_data["latencies"] = segment_data["latencies"][-100:]
            
            segment_data["last_update"] = datetime.now()
            
            # Update globale Metriken
            self.monitoring_data["global_metrics"]["total_requests"] += 1
            if result.compliance_status != "failed":
                self.monitoring_data["global_metrics"]["successful_requests"] += 1
            else:
                self.monitoring_data["global_metrics"]["failed_requests"] += 1
            
            # Prüfe Alerts
            await self._check_alerts(segment, result)
            
        except Exception as e:
            logger.error(f"Error processing pipeline result: {e}")
    
    async def _continuous_drift_monitoring(self):
        """Kontinuierliche Drift-Überwachung"""
        while True:
            try:
                # Prüfe alle Segmente auf Drift
                for segment in self.monitoring_data["segments"]:
                    await self._check_segment_drift(segment)
                
                # Warte bis zur nächsten Prüfung
                await asyncio.sleep(self.monitoring_config["drift_detection_interval_minutes"] * 60)
                
            except Exception as e:
                logger.error(f"Error in drift monitoring: {e}")
                await asyncio.sleep(60)  # Kurze Pause bei Fehler
    
    async def _performance_monitoring(self):
        """Performance-Monitoring"""
        while True:
            try:
                # Prüfe globale Performance-Metriken
                await self._check_global_performance()
                
                # Warte 5 Minuten
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _feedback_monitoring(self):
        """Feedback-Monitoring"""
        while True:
            try:
                # Prüfe Feedback-Korrelationen
                await self._check_feedback_correlations()
                
                # Warte 10 Minuten
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error in feedback monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_collection(self):
        """Sammelt Metriken für Dashboard"""
        while True:
            try:
                # Berechne durchschnittliche Metriken
                self._calculate_average_metrics()
                
                # Exportiere Metriken (Prometheus-style)
                await self._export_metrics()
                
                # Warte 1 Minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def _check_alerts(self, segment: str, result: PipelineResult):
        """Prüft Alerts für ein Pipeline-Ergebnis"""
        alerts = []
        
        # Quality Score Alert
        if result.evaluation_result.overall_score < self.monitoring_config["quality_score_threshold"]:
            alerts.append(MonitoringAlert(
                alert_type=AlertType.QUALITY_SCORE_DECLINE,
                severity=AlertSeverity.HIGH if result.evaluation_result.overall_score < 0.5 else AlertSeverity.MEDIUM,
                segment=segment,
                message=f"Quality score below threshold: {result.evaluation_result.overall_score:.3f} < {self.monitoring_config['quality_score_threshold']}",
                current_value=result.evaluation_result.overall_score,
                threshold_value=self.monitoring_config["quality_score_threshold"],
                timestamp=datetime.now(),
                metadata={"run_id": result.run_id, "template_hash": result.generation_result.template_hash}
            ))
        
        # Latency Alert
        if result.execution_time > self.monitoring_config["latency_threshold_seconds"]:
            alerts.append(MonitoringAlert(
                alert_type=AlertType.HIGH_LATENCY,
                severity=AlertSeverity.MEDIUM,
                segment=segment,
                message=f"High latency detected: {result.execution_time:.2f}s > {self.monitoring_config['latency_threshold_seconds']}s",
                current_value=result.execution_time,
                threshold_value=self.monitoring_config["latency_threshold_seconds"],
                timestamp=datetime.now(),
                metadata={"run_id": result.run_id}
            ))
        
        # Sende Alerts
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _check_segment_drift(self, segment: str):
        """Prüft Drift für ein Segment"""
        try:
            segment_data = self.monitoring_data["segments"][segment]
            
            if len(segment_data["quality_scores"]) < 10:
                return  # Nicht genug Daten
            
            # Berechne durchschnittlichen Score der letzten 10 Requests
            recent_scores = segment_data["quality_scores"][-10:]
            avg_recent_score = sum(recent_scores) / len(recent_scores)
            
            # Berechne durchschnittlichen Score der vorherigen 10 Requests
            if len(segment_data["quality_scores"]) >= 20:
                previous_scores = segment_data["quality_scores"][-20:-10]
                avg_previous_score = sum(previous_scores) / len(previous_scores)
                
                # Prüfe auf signifikanten Rückgang
                decline = avg_previous_score - avg_recent_score
                if decline > 0.1:  # 10% Rückgang
                    alert = MonitoringAlert(
                        alert_type=AlertType.TEMPLATE_DRIFT,
                        severity=AlertSeverity.MEDIUM if decline > 0.2 else AlertSeverity.LOW,
                        segment=segment,
                        message=f"Template drift detected: {decline:.3f} decline in quality score",
                        current_value=avg_recent_score,
                        threshold_value=avg_previous_score,
                        timestamp=datetime.now(),
                        metadata={"decline_percentage": decline / avg_previous_score}
                    )
                    await self._send_alert(alert)
        
        except Exception as e:
            logger.error(f"Error checking segment drift for {segment}: {e}")
    
    async def _check_global_performance(self):
        """Prüft globale Performance-Metriken"""
        try:
            metrics = self.monitoring_data["global_metrics"]
            
            # Error Rate Alert
            if metrics["total_requests"] > 0:
                error_rate = metrics["failed_requests"] / metrics["total_requests"]
                if error_rate > self.monitoring_config["error_rate_threshold"]:
                    alert = MonitoringAlert(
                        alert_type=AlertType.ERROR_SPIKE,
                        severity=AlertSeverity.HIGH if error_rate > 0.2 else AlertSeverity.MEDIUM,
                        segment="global",
                        message=f"High error rate detected: {error_rate:.3f} > {self.monitoring_config['error_rate_threshold']}",
                        current_value=error_rate,
                        threshold_value=self.monitoring_config["error_rate_threshold"],
                        timestamp=datetime.now(),
                        metadata={"total_requests": metrics["total_requests"], "failed_requests": metrics["failed_requests"]}
                    )
                    await self._send_alert(alert)
        
        except Exception as e:
            logger.error(f"Error checking global performance: {e}")
    
    async def _check_feedback_correlations(self):
        """Prüft Feedback-Korrelationen"""
        try:
            # In der Praxis würde hier die Feedback-Korrelations-Analyse stehen
            # Für jetzt ist es ein Platzhalter
            pass
        
        except Exception as e:
            logger.error(f"Error checking feedback correlations: {e}")
    
    def _calculate_average_metrics(self):
        """Berechnet durchschnittliche Metriken"""
        try:
            metrics = self.monitoring_data["global_metrics"]
            
            # Berechne durchschnittliche Latenz
            all_latencies = []
            for segment_data in self.monitoring_data["segments"].values():
                all_latencies.extend(segment_data["latencies"])
            
            if all_latencies:
                metrics["average_latency"] = sum(all_latencies) / len(all_latencies)
            
            # Berechne durchschnittlichen Quality Score
            all_scores = []
            for segment_data in self.monitoring_data["segments"].values():
                all_scores.extend(segment_data["quality_scores"])
            
            if all_scores:
                metrics["average_quality_score"] = sum(all_scores) / len(all_scores)
        
        except Exception as e:
            logger.error(f"Error calculating average metrics: {e}")
    
    async def _export_metrics(self):
        """Exportiert Metriken im Prometheus-Format"""
        try:
            metrics = self.monitoring_data["global_metrics"]
            
            # Prometheus-style Metriken
            prometheus_metrics = f"""
# HELP bookwriter_total_requests Total number of requests
# TYPE bookwriter_total_requests counter
bookwriter_total_requests {metrics['total_requests']}

# HELP bookwriter_successful_requests Total number of successful requests
# TYPE bookwriter_successful_requests counter
bookwriter_successful_requests {metrics['successful_requests']}

# HELP bookwriter_failed_requests Total number of failed requests
# TYPE bookwriter_failed_requests counter
bookwriter_failed_requests {metrics['failed_requests']}

# HELP bookwriter_average_latency Average request latency in seconds
# TYPE bookwriter_average_latency gauge
bookwriter_average_latency {metrics['average_latency']:.3f}

# HELP bookwriter_average_quality_score Average quality score
# TYPE bookwriter_average_quality_score gauge
bookwriter_average_quality_score {metrics['average_quality_score']:.3f}

# HELP bookwriter_total_feedback Total number of feedback submissions
# TYPE bookwriter_total_feedback counter
bookwriter_total_feedback {metrics['total_feedback']}
"""
            
            # Speichere Metriken
            with open("monitoring/metrics.prom", "w") as f:
                f.write(prometheus_metrics)
            
            # JSON-Metriken für Dashboard
            json_metrics = {
                "timestamp": datetime.now().isoformat(),
                "global_metrics": metrics,
                "segments": {
                    segment: {
                        "total_requests": len(data["requests"]),
                        "avg_quality_score": sum(data["quality_scores"]) / len(data["quality_scores"]) if data["quality_scores"] else 0,
                        "avg_latency": sum(data["latencies"]) / len(data["latencies"]) if data["latencies"] else 0,
                        "last_update": data["last_update"].isoformat()
                    }
                    for segment, data in self.monitoring_data["segments"].items()
                }
            }
            
            with open("monitoring/metrics.json", "w") as f:
                json.dump(json_metrics, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
    
    async def _send_alert(self, alert: MonitoringAlert):
        """Sendet Alert über alle konfigurierten Channels"""
        try:
            # Prüfe Cooldown
            alert_key = f"{alert.alert_type.value}_{alert.segment}"
            if alert_key in self.alert_history:
                last_alert_time = self.alert_history[alert_key]
                if (datetime.now() - last_alert_time).total_seconds() < self.monitoring_config["alert_cooldown_minutes"] * 60:
                    return  # Cooldown aktiv
            
            # Update Alert-Historie
            self.alert_history[alert_key] = datetime.now()
            
            # Speichere Alert
            self.monitoring_data["alerts"].append(alert.__dict__)
            
            # Sende über alle konfigurierten Channels
            for channel in self.enabled_channels:
                try:
                    await self.alert_channels[channel](alert)
                except Exception as e:
                    logger.error(f"Error sending alert via {channel}: {e}")
        
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def _send_slack_alert(self, alert: MonitoringAlert):
        """Sendet Slack-Alert"""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return
        
        # Slack Message
        color = {
            AlertSeverity.LOW: "#36a64f",
            AlertSeverity.MEDIUM: "#ffa500",
            AlertSeverity.HIGH: "#ff0000",
            AlertSeverity.CRITICAL: "#8b0000"
        }[alert.severity]
        
        message = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 {alert.alert_type.value.replace('_', ' ').title()}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Segment",
                            "value": alert.segment,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": alert.severity.value,
                            "short": True
                        },
                        {
                            "title": "Current Value",
                            "value": f"{alert.current_value:.3f}",
                            "short": True
                        },
                        {
                            "title": "Threshold",
                            "value": f"{alert.threshold_value:.3f}",
                            "short": True
                        }
                    ],
                    "footer": "One Click Book Writer Monitoring",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }
        
        # Sende Request
        response = requests.post(webhook_url, json=message)
        if response.status_code != 200:
            logger.error(f"Slack alert failed: {response.status_code}")
    
    async def _send_email_alert(self, alert: MonitoringAlert):
        """Sendet Email-Alert"""
        smtp_host = os.getenv("EMAIL_SMTP_HOST")
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        smtp_user = os.getenv("EMAIL_SMTP_USER")
        smtp_password = os.getenv("EMAIL_SMTP_PASSWORD")
        alert_email = os.getenv("ALERT_EMAIL")
        
        if not all([smtp_host, smtp_user, smtp_password, alert_email]):
            return
        
        # Email Content
        subject = f"[{alert.severity.value.upper()}] {alert.alert_type.value.replace('_', ' ').title()}"
        
        body = f"""
Alert Details:
- Type: {alert.alert_type.value}
- Severity: {alert.severity.value}
- Segment: {alert.segment}
- Message: {alert.message}
- Current Value: {alert.current_value:.3f}
- Threshold: {alert.threshold_value:.3f}
- Timestamp: {alert.timestamp.isoformat()}

Metadata: {json.dumps(alert.metadata, indent=2)}
"""
        
        # Sende Email
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                
                message = f"Subject: {subject}\n\n{body}"
                server.sendmail(smtp_user, alert_email, message)
        
        except Exception as e:
            logger.error(f"Email alert failed: {e}")
    
    async def _log_alert(self, alert: MonitoringAlert):
        """Loggt Alert"""
        logger.warning(f"ALERT [{alert.severity.value.upper()}] {alert.alert_type.value}: {alert.message}")
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Gibt Monitoring-Zusammenfassung zurück"""
        return {
            "status": "active",
            "segments_monitored": len(self.monitoring_data["segments"]),
            "total_alerts": len(self.monitoring_data["alerts"]),
            "recent_alerts": len([a for a in self.monitoring_data["alerts"] 
                                if (datetime.now() - datetime.fromisoformat(a["timestamp"])).days <= 1]),
            "global_metrics": self.monitoring_data["global_metrics"],
            "enabled_channels": self.enabled_channels,
            "config": self.monitoring_config
        }

# Singleton Instance
monitoring_service = MonitoringService() 