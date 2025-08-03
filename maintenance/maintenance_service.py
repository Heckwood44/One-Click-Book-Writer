#!/usr/bin/env python3
"""
Maintenance Service
Automatisierte Wartungsaufgaben für das Framework
"""

import json
import logging
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import shutil
import zipfile

from core.architecture import PromptFrame
from core.enhanced_pipeline import EnhancedPipeline
from core.policy_engine import PolicyEngine
from core.drift_detector import DriftDetector
from core.feedback_intelligence import FeedbackIntelligence
from templates.template_marketplace import template_marketplace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaintenanceService:
    """Automatisierte Wartungsaufgaben"""
    
    def __init__(self):
        self.pipeline = EnhancedPipeline()
        self.policy_engine = PolicyEngine()
        self.drift_detector = DriftDetector()
        self.feedback_intelligence = FeedbackIntelligence()
        
        # Maintenance-Konfiguration
        self.maintenance_config = {
            "recalibration_interval_days": int(os.getenv("RECALIBRATION_INTERVAL_DAYS", "7")),
            "cleanup_interval_days": int(os.getenv("CLEANUP_INTERVAL_DAYS", "30")),
            "snapshot_interval_days": int(os.getenv("SNAPSHOT_INTERVAL_DAYS", "7")),
            "max_history_days": int(os.getenv("MAX_HISTORY_DAYS", "90")),
            "backup_retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "365")),
            "top_segments_for_recalibration": int(os.getenv("TOP_SEGMENTS_FOR_RECALIBRATION", "5"))
        }
        
        # Maintenance-Historie
        self.maintenance_history = []
        
        # Lade Maintenance-Historie
        self._load_maintenance_history()
    
    def _load_maintenance_history(self):
        """Lädt Maintenance-Historie"""
        try:
            if os.path.exists("maintenance/maintenance_history.json"):
                with open("maintenance/maintenance_history.json", "r") as f:
                    self.maintenance_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading maintenance history: {e}")
    
    def _save_maintenance_history(self):
        """Speichert Maintenance-Historie"""
        try:
            with open("maintenance/maintenance_history.json", "w") as f:
                json.dump(self.maintenance_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving maintenance history: {e}")
    
    def start_maintenance_scheduler(self):
        """Startet den Maintenance-Scheduler"""
        logger.info("Starting maintenance scheduler...")
        
        # Scheduled Jobs
        schedule.every(self.maintenance_config["recalibration_interval_days"]).days.do(self.scheduled_recalibration)
        schedule.every(self.maintenance_config["cleanup_interval_days"]).days.do(self.scheduled_cleanup)
        schedule.every(self.maintenance_config["snapshot_interval_days"]).days.do(self.scheduled_snapshot)
        
        # Tägliche Health Checks
        schedule.every().day.at("02:00").do(self.daily_health_check)
        
        # Wöchentliche Reports
        schedule.every().sunday.at("03:00").do(self.weekly_maintenance_report)
        
        # Scheduler-Loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Prüfe jede Minute
            except Exception as e:
                logger.error(f"Maintenance scheduler error: {e}")
                time.sleep(300)  # 5 Minuten Pause bei Fehler
    
    def scheduled_recalibration(self):
        """Scheduled Recalibration für Top-Segmente"""
        try:
            logger.info("Starting scheduled recalibration...")
            
            # Identifiziere Top-Segmente
            top_segments = self._identify_top_segments()
            
            recalibration_results = []
            
            for segment in top_segments:
                try:
                    result = self._perform_segment_recalibration(segment)
                    recalibration_results.append(result)
                    logger.info(f"Recalibration completed for {segment}: {result['status']}")
                except Exception as e:
                    logger.error(f"Recalibration failed for {segment}: {e}")
                    recalibration_results.append({
                        "segment": segment,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Speichere Recalibration-Ergebnisse
            self._save_recalibration_results(recalibration_results)
            
            # Update Maintenance-Historie
            self.maintenance_history.append({
                "type": "scheduled_recalibration",
                "timestamp": datetime.now().isoformat(),
                "segments_processed": len(top_segments),
                "successful_recalibrations": len([r for r in recalibration_results if r["status"] == "success"]),
                "results": recalibration_results
            })
            
            self._save_maintenance_history()
            
            logger.info(f"Scheduled recalibration completed: {len(recalibration_results)} segments processed")
            
        except Exception as e:
            logger.error(f"Scheduled recalibration failed: {e}")
    
    def _identify_top_segments(self) -> List[str]:
        """Identifiziert Top-Segmente für Recalibration"""
        try:
            # Sammle Segment-Performance-Daten
            segment_performance = {}
            
            for segment, history in self.drift_detector.segment_history.items():
                if history["runs"]:
                    recent_runs = [run for run in history["runs"] 
                                 if (datetime.now() - run["timestamp"]).days <= 7]
                    
                    if recent_runs:
                        avg_score = sum(run["score"] for run in recent_runs) / len(recent_runs)
                        usage_count = len(recent_runs)
                        
                        segment_performance[segment] = {
                            "avg_score": avg_score,
                            "usage_count": usage_count,
                            "priority_score": avg_score * 0.7 + min(usage_count / 10, 1.0) * 0.3
                        }
            
            # Sortiere nach Priority Score
            sorted_segments = sorted(segment_performance.items(), 
                                   key=lambda x: x[1]["priority_score"], 
                                   reverse=True)
            
            # Wähle Top-Segmente
            top_segments = [segment for segment, _ in sorted_segments[:self.maintenance_config["top_segments_for_recalibration"]]]
            
            return top_segments
            
        except Exception as e:
            logger.error(f"Error identifying top segments: {e}")
            return []
    
    def _perform_segment_recalibration(self, segment: str) -> Dict[str, Any]:
        """Führt Recalibration für ein Segment durch"""
        try:
            # Extrahiere Segment-Informationen
            age_group, genre = segment.split("_", 1)
            
            # Erstelle Test-PromptFrame
            prompt_frame = PromptFrame(
                age_group=age_group,
                genre=genre,
                emotion="courage",  # Default
                language="de"
            )
            
            # Führe A/B-Test durch
            ab_test_results = []
            
            # Test 1: Aktuelles Template
            result_current = self.pipeline.run_enhanced_pipeline(
                prompt_frame=prompt_frame,
                enable_optimization=False,
                enable_ab_testing=False,
                enable_feedback_collection=False
            )
            
            ab_test_results.append({
                "template": "current",
                "quality_score": result_current.evaluation_result.overall_score,
                "template_hash": result_current.generation_result.template_hash
            })
            
            # Test 2: Optimiertes Template
            result_optimized = self.pipeline.run_enhanced_pipeline(
                prompt_frame=prompt_frame,
                enable_optimization=True,
                enable_ab_testing=False,
                enable_feedback_collection=False
            )
            
            ab_test_results.append({
                "template": "optimized",
                "quality_score": result_optimized.evaluation_result.overall_score,
                "template_hash": result_optimized.generation_result.template_hash,
                "optimization_delta": result_optimized.optimization_result.quality_score_delta if result_optimized.optimization_result else 0
            })
            
            # Test 3: Experiment-Template
            experiment_suggestions = self.policy_engine.get_experiment_suggestions(segment)
            if experiment_suggestions:
                # Verwende erste Experiment-Suggestion
                experiment = experiment_suggestions[0]
                
                # Erstelle experimentelles PromptFrame
                if experiment["type"] == "emotional_anchor_variation":
                    for emotion in experiment["variations"][:2]:  # Teste erste 2 Emotionen
                        exp_prompt_frame = PromptFrame(
                            age_group=age_group,
                            genre=genre,
                            emotion=emotion,
                            language="de"
                        )
                        
                        result_exp = self.pipeline.run_enhanced_pipeline(
                            prompt_frame=exp_prompt_frame,
                            enable_optimization=False,
                            enable_ab_testing=False,
                            enable_feedback_collection=False
                        )
                        
                        ab_test_results.append({
                            "template": f"experiment_{emotion}",
                            "quality_score": result_exp.evaluation_result.overall_score,
                            "template_hash": result_exp.generation_result.template_hash,
                            "experiment_type": experiment["type"],
                            "variation": emotion
                        })
            
            # Finde bestes Template
            best_result = max(ab_test_results, key=lambda x: x["quality_score"])
            
            # Erstelle Recalibration-Ergebnis
            recalibration_result = {
                "segment": segment,
                "status": "success",
                "ab_test_results": ab_test_results,
                "best_template": best_result,
                "improvement": best_result["quality_score"] - ab_test_results[0]["quality_score"],
                "recommendation": self._generate_recalibration_recommendation(ab_test_results)
            }
            
            return recalibration_result
            
        except Exception as e:
            logger.error(f"Error performing segment recalibration for {segment}: {e}")
            return {
                "segment": segment,
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_recalibration_recommendation(self, ab_test_results: List[Dict[str, Any]]) -> str:
        """Generiert Recalibration-Empfehlung"""
        try:
            current_score = ab_test_results[0]["quality_score"]
            best_score = max(result["quality_score"] for result in ab_test_results)
            
            if best_score > current_score + 0.1:
                best_template = max(ab_test_results, key=lambda x: x["quality_score"])
                
                if best_template["template"] == "optimized":
                    return f"Promote optimized template (improvement: {best_score - current_score:.3f})"
                elif best_template["template"].startswith("experiment_"):
                    variation = best_template.get("variation", "unknown")
                    return f"Promote experiment template with {variation} emotion (improvement: {best_score - current_score:.3f})"
                else:
                    return f"Keep current template (best performing)"
            else:
                return "No significant improvement found, keep current template"
                
        except Exception as e:
            logger.error(f"Error generating recalibration recommendation: {e}")
            return "Unable to generate recommendation"
    
    def _save_recalibration_results(self, results: List[Dict[str, Any]]):
        """Speichert Recalibration-Ergebnisse"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"maintenance/recalibration_results_{timestamp}.json"
            
            with open(filename, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "results": results,
                    "summary": {
                        "total_segments": len(results),
                        "successful_recalibrations": len([r for r in results if r["status"] == "success"]),
                        "average_improvement": sum(r.get("improvement", 0) for r in results if r["status"] == "success") / max(len([r for r in results if r["status"] == "success"]), 1)
                    }
                }, f, indent=2)
            
            logger.info(f"Recalibration results saved: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving recalibration results: {e}")
    
    def scheduled_cleanup(self):
        """Scheduled Cleanup und Snapshotting"""
        try:
            logger.info("Starting scheduled cleanup...")
            
            cleanup_results = {
                "files_cleaned": 0,
                "space_freed_mb": 0,
                "backups_created": 0,
                "old_files_removed": 0
            }
            
            # Cleanup alte Log-Dateien
            cleanup_results.update(self._cleanup_old_logs())
            
            # Cleanup alte Reports
            cleanup_results.update(self._cleanup_old_reports())
            
            # Cleanup alte Backups
            cleanup_results.update(self._cleanup_old_backups())
            
            # Cleanup alte Maintenance-Dateien
            cleanup_results.update(self._cleanup_old_maintenance_files())
            
            # Update Maintenance-Historie
            self.maintenance_history.append({
                "type": "scheduled_cleanup",
                "timestamp": datetime.now().isoformat(),
                "results": cleanup_results
            })
            
            self._save_maintenance_history()
            
            logger.info(f"Scheduled cleanup completed: {cleanup_results}")
            
        except Exception as e:
            logger.error(f"Scheduled cleanup failed: {e}")
    
    def _cleanup_old_logs(self) -> Dict[str, int]:
        """Cleanup alte Log-Dateien"""
        try:
            files_removed = 0
            space_freed = 0
            
            log_dirs = ["logs", "output"]
            cutoff_date = datetime.now() - timedelta(days=self.maintenance_config["max_history_days"])
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    for filename in os.listdir(log_dir):
                        filepath = os.path.join(log_dir, filename)
                        
                        if os.path.isfile(filepath):
                            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                            
                            if file_time < cutoff_date:
                                file_size = os.path.getsize(filepath)
                                os.remove(filepath)
                                files_removed += 1
                                space_freed += file_size
            
            return {
                "files_cleaned": files_removed,
                "space_freed_mb": space_freed / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")
            return {"files_cleaned": 0, "space_freed_mb": 0}
    
    def _cleanup_old_reports(self) -> Dict[str, int]:
        """Cleanup alte Reports"""
        try:
            files_removed = 0
            space_freed = 0
            
            report_dirs = ["output", "reports"]
            cutoff_date = datetime.now() - timedelta(days=self.maintenance_config["max_history_days"])
            
            for report_dir in report_dirs:
                if os.path.exists(report_dir):
                    for filename in os.listdir(report_dir):
                        if filename.endswith((".json", ".md", ".txt")):
                            filepath = os.path.join(report_dir, filename)
                            
                            if os.path.isfile(filepath):
                                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                                
                                if file_time < cutoff_date:
                                    file_size = os.path.getsize(filepath)
                                    os.remove(filepath)
                                    files_removed += 1
                                    space_freed += file_size
            
            return {
                "old_files_removed": files_removed,
                "space_freed_mb": space_freed / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old reports: {e}")
            return {"old_files_removed": 0, "space_freed_mb": 0}
    
    def _cleanup_old_backups(self) -> Dict[str, int]:
        """Cleanup alte Backups"""
        try:
            files_removed = 0
            space_freed = 0
            
            backup_dirs = ["backups", "snapshots"]
            cutoff_date = datetime.now() - timedelta(days=self.maintenance_config["backup_retention_days"])
            
            for backup_dir in backup_dirs:
                if os.path.exists(backup_dir):
                    for filename in os.listdir(backup_dir):
                        filepath = os.path.join(backup_dir, filename)
                        
                        if os.path.isfile(filepath):
                            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                            
                            if file_time < cutoff_date:
                                file_size = os.path.getsize(filepath)
                                os.remove(filepath)
                                files_removed += 1
                                space_freed += file_size
            
            return {
                "backups_removed": files_removed,
                "space_freed_mb": space_freed / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return {"backups_removed": 0, "space_freed_mb": 0}
    
    def _cleanup_old_maintenance_files(self) -> Dict[str, int]:
        """Cleanup alte Maintenance-Dateien"""
        try:
            files_removed = 0
            space_freed = 0
            
            maintenance_dir = "maintenance"
            cutoff_date = datetime.now() - timedelta(days=self.maintenance_config["max_history_days"])
            
            if os.path.exists(maintenance_dir):
                for filename in os.listdir(maintenance_dir):
                    if filename.startswith("recalibration_results_") and filename.endswith(".json"):
                        filepath = os.path.join(maintenance_dir, filename)
                        
                        if os.path.isfile(filepath):
                            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                            
                            if file_time < cutoff_date:
                                file_size = os.path.getsize(filepath)
                                os.remove(filepath)
                                files_removed += 1
                                space_freed += file_size
            
            return {
                "maintenance_files_removed": files_removed,
                "space_freed_mb": space_freed / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old maintenance files: {e}")
            return {"maintenance_files_removed": 0, "space_freed_mb": 0}
    
    def scheduled_snapshot(self):
        """Scheduled Snapshotting"""
        try:
            logger.info("Starting scheduled snapshot...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_dir = f"snapshots/snapshot_{timestamp}"
            
            # Erstelle Snapshot-Verzeichnis
            os.makedirs(snapshot_dir, exist_ok=True)
            
            # Snapshot-Daten sammeln
            snapshot_data = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_stats": self.pipeline.get_pipeline_stats(),
                "policy_summary": self.policy_engine.get_policy_summary(),
                "drift_summary": self.drift_detector.get_drift_summary(),
                "feedback_summary": self.feedback_intelligence.get_feedback_summary(),
                "marketplace_summary": template_marketplace.get_marketplace_summary(),
                "maintenance_history": self.maintenance_history[-100:],  # Letzte 100 Einträge
                "segment_performance": self.drift_detector.segment_history,
                "template_registry": template_marketplace.templates
            }
            
            # Speichere Snapshot
            with open(f"{snapshot_dir}/snapshot_data.json", "w") as f:
                json.dump(snapshot_data, f, indent=2)
            
            # Erstelle Backup-Archiv
            self._create_backup_archive(snapshot_dir, timestamp)
            
            # Update Maintenance-Historie
            self.maintenance_history.append({
                "type": "scheduled_snapshot",
                "timestamp": datetime.now().isoformat(),
                "snapshot_dir": snapshot_dir,
                "data_size_mb": os.path.getsize(f"{snapshot_dir}/snapshot_data.json") / (1024 * 1024)
            })
            
            self._save_maintenance_history()
            
            logger.info(f"Scheduled snapshot completed: {snapshot_dir}")
            
        except Exception as e:
            logger.error(f"Scheduled snapshot failed: {e}")
    
    def _create_backup_archive(self, snapshot_dir: str, timestamp: str):
        """Erstellt Backup-Archiv"""
        try:
            archive_name = f"snapshots/backup_{timestamp}.zip"
            
            with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Füge Snapshot-Daten hinzu
                zipf.write(f"{snapshot_dir}/snapshot_data.json", "snapshot_data.json")
                
                # Füge wichtige Konfigurationsdateien hinzu
                config_files = [
                    "templates/template_registry.json",
                    "maintenance/maintenance_history.json",
                    "profiles/age_group_profiles.json",
                    "profiles/genre_profiles.json"
                ]
                
                for config_file in config_files:
                    if os.path.exists(config_file):
                        zipf.write(config_file, config_file)
            
            logger.info(f"Backup archive created: {archive_name}")
            
        except Exception as e:
            logger.error(f"Error creating backup archive: {e}")
    
    def daily_health_check(self):
        """Täglicher Health Check"""
        try:
            logger.info("Starting daily health check...")
            
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_health": self._check_pipeline_health(),
                "policy_engine_health": self._check_policy_engine_health(),
                "drift_detector_health": self._check_drift_detector_health(),
                "marketplace_health": self._check_marketplace_health(),
                "overall_status": "healthy"
            }
            
            # Prüfe Gesamtstatus
            if any(status["status"] != "healthy" for status in health_status.values() if isinstance(status, dict) and "status" in status):
                health_status["overall_status"] = "warning"
            
            # Speichere Health Check
            with open(f"maintenance/health_check_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
                json.dump(health_status, f, indent=2)
            
            logger.info(f"Daily health check completed: {health_status['overall_status']}")
            
        except Exception as e:
            logger.error(f"Daily health check failed: {e}")
    
    def _check_pipeline_health(self) -> Dict[str, Any]:
        """Prüft Pipeline-Gesundheit"""
        try:
            stats = self.pipeline.get_pipeline_stats()
            
            # Prüfe Erfolgsrate
            success_rate = stats["successful_runs"] / max(stats["total_runs"], 1)
            
            return {
                "status": "healthy" if success_rate >= 0.9 else "warning",
                "success_rate": success_rate,
                "total_runs": stats["total_runs"],
                "average_execution_time": stats["average_execution_time"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_policy_engine_health(self) -> Dict[str, Any]:
        """Prüft Policy Engine-Gesundheit"""
        try:
            summary = self.policy_engine.get_policy_summary()
            
            return {
                "status": "healthy",
                "total_decisions": summary["total_decisions"],
                "active_segments": summary["active_segments"],
                "total_templates": summary["total_templates"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_drift_detector_health(self) -> Dict[str, Any]:
        """Prüft Drift Detector-Gesundheit"""
        try:
            summary = self.drift_detector.get_drift_summary()
            
            # Prüfe Anzahl kritischer Alerts
            critical_alerts = len([a for a in self.drift_detector.drift_alerts 
                                 if a.severity in ["high", "critical"]])
            
            return {
                "status": "healthy" if critical_alerts == 0 else "warning",
                "total_alerts": summary["total_alerts"],
                "critical_alerts": critical_alerts,
                "active_segments": summary["active_segments"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_marketplace_health(self) -> Dict[str, Any]:
        """Prüft Marketplace-Gesundheit"""
        try:
            summary = template_marketplace.get_marketplace_summary()
            
            return {
                "status": "healthy",
                "total_templates": summary["total_templates"],
                "active_templates": summary["active_templates"],
                "best_performing_templates": summary["best_performing_templates"]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def weekly_maintenance_report(self):
        """Wöchentlicher Maintenance-Report"""
        try:
            logger.info("Generating weekly maintenance report...")
            
            # Sammle Wochendaten
            week_ago = datetime.now() - timedelta(days=7)
            
            weekly_data = {
                "period": {
                    "start": week_ago.isoformat(),
                    "end": datetime.now().isoformat()
                },
                "maintenance_activities": [
                    entry for entry in self.maintenance_history
                    if datetime.fromisoformat(entry["timestamp"]) >= week_ago
                ],
                "pipeline_performance": self.pipeline.get_pipeline_stats(),
                "drift_alerts": [
                    alert.__dict__ for alert in self.drift_detector.drift_alerts
                    if alert.timestamp >= week_ago
                ],
                "template_activity": template_marketplace.get_marketplace_summary(),
                "recommendations": self._generate_weekly_recommendations()
            }
            
            # Speichere Report
            timestamp = datetime.now().strftime("%Y%m%d")
            with open(f"reports/weekly_maintenance_report_{timestamp}.json", "w") as f:
                json.dump(weekly_data, f, indent=2)
            
            # Erstelle Markdown-Report
            self._create_markdown_report(weekly_data, timestamp)
            
            logger.info(f"Weekly maintenance report generated: reports/weekly_maintenance_report_{timestamp}.json")
            
        except Exception as e:
            logger.error(f"Weekly maintenance report failed: {e}")
    
    def _generate_weekly_recommendations(self) -> List[str]:
        """Generiert wöchentliche Empfehlungen"""
        recommendations = []
        
        try:
            # Prüfe Pipeline-Performance
            stats = self.pipeline.get_pipeline_stats()
            if stats["successful_runs"] / max(stats["total_runs"], 1) < 0.95:
                recommendations.append("Pipeline success rate below 95% - investigate recent failures")
            
            # Prüfe Drift-Alerts
            recent_alerts = [a for a in self.drift_detector.drift_alerts 
                           if (datetime.now() - a.timestamp).days <= 7]
            if len(recent_alerts) > 5:
                recommendations.append(f"High number of drift alerts ({len(recent_alerts)}) - review template performance")
            
            # Prüfe Template-Aktivität
            marketplace_summary = template_marketplace.get_marketplace_summary()
            if marketplace_summary["recent_activity"]["templates_added_7d"] == 0:
                recommendations.append("No new templates added this week - consider template experimentation")
            
            # Prüfe Maintenance-Aktivität
            recent_maintenance = [entry for entry in self.maintenance_history 
                                if (datetime.now() - datetime.fromisoformat(entry["timestamp"])).days <= 7]
            if not recent_maintenance:
                recommendations.append("No maintenance activities this week - schedule recalibration")
            
        except Exception as e:
            logger.error(f"Error generating weekly recommendations: {e}")
            recommendations.append("Unable to generate recommendations due to error")
        
        return recommendations
    
    def _create_markdown_report(self, weekly_data: Dict[str, Any], timestamp: str):
        """Erstellt Markdown-Report"""
        try:
            markdown_content = f"""# Weekly Maintenance Report - {timestamp}

## Executive Summary
- **Period**: {weekly_data['period']['start']} to {weekly_data['period']['end']}
- **Maintenance Activities**: {len(weekly_data['maintenance_activities'])}
- **Drift Alerts**: {len(weekly_data['drift_alerts'])}
- **Pipeline Success Rate**: {(weekly_data['pipeline_performance']['successful_runs'] / max(weekly_data['pipeline_performance']['total_runs'], 1)) * 100:.1f}%

## Pipeline Performance
- Total Runs: {weekly_data['pipeline_performance']['total_runs']}
- Successful Runs: {weekly_data['pipeline_performance']['successful_runs']}
- Average Execution Time: {weekly_data['pipeline_performance']['average_execution_time']:.2f}s
- Total Cost: ${weekly_data['pipeline_performance']['total_cost']:.4f}

## Template Activity
- Total Templates: {weekly_data['template_activity']['total_templates']}
- Active Templates: {weekly_data['template_activity']['active_templates']}
- Best Performing Templates: {weekly_data['template_activity']['best_performing_templates']}

## Recommendations
{chr(10).join(f"- {rec}" for rec in weekly_data['recommendations'])}

## Maintenance Activities
{chr(10).join(f"- {activity['type']} ({activity['timestamp']})" for activity in weekly_data['maintenance_activities'])}

---
*Report generated automatically by One Click Book Writer Maintenance Service*
"""
            
            with open(f"reports/weekly_maintenance_report_{timestamp}.md", "w") as f:
                f.write(markdown_content)
            
        except Exception as e:
            logger.error(f"Error creating markdown report: {e}")

# Singleton Instance
maintenance_service = MaintenanceService()

if __name__ == "__main__":
    # Starte Maintenance-Scheduler
    maintenance_service.start_maintenance_scheduler() 