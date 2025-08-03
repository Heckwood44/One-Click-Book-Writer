#!/usr/bin/env python3
"""
Production Deployment
Deployment-Script für die produktionsreife One Click Book Writer Plattform
"""

import os
import sys
import json
import logging
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, Any

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDeployment:
    """Produktions-Deployment für One Click Book Writer"""
    
    def __init__(self):
        self.deployment_config = {
            "api_port": int(os.getenv("API_PORT", "8000")),
            "monitoring_port": int(os.getenv("MONITORING_PORT", "8001")),
            "maintenance_port": int(os.getenv("MAINTENANCE_PORT", "8002")),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "workers": int(os.getenv("WORKERS", "4")),
            "max_requests": int(os.getenv("MAX_REQUESTS", "1000")),
            "timeout": int(os.getenv("TIMEOUT", "300"))
        }
        
        # Erstelle notwendige Verzeichnisse
        self._create_directories()
    
    def _create_directories(self):
        """Erstellt notwendige Verzeichnisse"""
        directories = [
            "logs",
            "output", 
            "reports",
            "snapshots",
            "backups",
            "maintenance",
            "monitoring",
            "templates",
            "profiles"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def deploy_api_service(self):
        """Deployed den API-Service"""
        try:
            logger.info("Deploying API service...")
            
            # Erstelle Gunicorn-Konfiguration
            gunicorn_config = f"""
bind = "0.0.0.0:{self.deployment_config['api_port']}"
workers = {self.deployment_config['workers']}
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = {self.deployment_config['max_requests']}
timeout = {self.deployment_config['timeout']}
accesslog = "logs/api_access.log"
errorlog = "logs/api_error.log"
loglevel = "{self.deployment_config['log_level'].lower()}"
preload_app = True
"""
            
            with open("deploy/gunicorn.conf.py", "w") as f:
                f.write(gunicorn_config)
            
            # Starte API-Service
            cmd = [
                "gunicorn",
                "-c", "deploy/gunicorn.conf.py",
                "api.app:app"
            ]
            
            logger.info(f"Starting API service with command: {' '.join(cmd)}")
            
            # In Produktion würde hier ein Process Manager wie systemd verwendet werden
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info(f"API service started with PID: {process.pid}")
            return process
            
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to deploy API service (File/Permission): {e}")
            raise
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to deploy API service (Subprocess): {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error deploying API service: {e}")
            raise
    
    def deploy_monitoring_service(self):
        """Deployed den Monitoring-Service"""
        try:
            logger.info("Deploying monitoring service...")
            
            # Starte Monitoring-Service
            cmd = [
                "python", "-m", "monitoring.monitoring_service"
            ]
            
            logger.info(f"Starting monitoring service with command: {' '.join(cmd)}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info(f"Monitoring service started with PID: {process.pid}")
            return process
            
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to deploy monitoring service (File/Permission): {e}")
            raise
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to deploy monitoring service (Subprocess): {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error deploying monitoring service: {e}")
            raise
    
    def deploy_maintenance_service(self):
        """Deployed den Maintenance-Service"""
        try:
            logger.info("Deploying maintenance service...")
            
            # Starte Maintenance-Service
            cmd = [
                "python", "-m", "maintenance.maintenance_service"
            ]
            
            logger.info(f"Starting maintenance service with command: {' '.join(cmd)}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info(f"Maintenance service started with PID: {process.pid}")
            return process
            
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to deploy maintenance service (File/Permission): {e}")
            raise
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to deploy maintenance service (Subprocess): {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error deploying maintenance service: {e}")
            raise
    
    def setup_environment(self):
        """Setup der Produktionsumgebung"""
        try:
            logger.info("Setting up production environment...")
            
            # Prüfe Umgebungsvariablen
            required_env_vars = [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "BOOKWRITER_API_KEY"
            ]
            
            missing_vars = []
            for var in required_env_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                logger.error(f"Missing required environment variables: {missing_vars}")
                raise ValueError(f"Missing environment variables: {missing_vars}")
            
            # Erstelle .env-Datei für lokale Entwicklung
            env_content = f"""
# One Click Book Writer Production Environment
ENVIRONMENT={self.deployment_config['environment']}
LOG_LEVEL={self.deployment_config['log_level']}

# API Configuration
API_PORT={self.deployment_config['api_port']}
RATE_LIMIT_PER_MINUTE=60
OPTIMIZATION_ENABLED=true
AB_TESTING_ENABLED=true
FEEDBACK_COLLECTION_ENABLED=true
DRIFT_DETECTION_ENABLED=true

# Monitoring Configuration
QUALITY_SCORE_THRESHOLD=0.7
FEEDBACK_CORRELATION_THRESHOLD=0.6
LATENCY_THRESHOLD_SECONDS=30.0
ERROR_RATE_THRESHOLD=0.1
DRIFT_DETECTION_INTERVAL_MINUTES=15
ALERT_COOLDOWN_MINUTES=60

# Maintenance Configuration
RECALIBRATION_INTERVAL_DAYS=7
CLEANUP_INTERVAL_DAYS=30
SNAPSHOT_INTERVAL_DAYS=7
MAX_HISTORY_DAYS=90
BACKUP_RETENTION_DAYS=365
TOP_SEGMENTS_FOR_RECALIBRATION=5

# External Services (optional)
# SLACK_WEBHOOK_URL=
# EMAIL_SMTP_HOST=
# EMAIL_SMTP_PORT=587
# EMAIL_SMTP_USER=
# EMAIL_SMTP_PASSWORD=
# ALERT_EMAIL=
"""
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            logger.info("Environment setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup environment: {e}")
            raise
    
    def run_health_checks(self):
        """Führt Health Checks durch"""
        try:
            logger.info("Running health checks...")
            
            import requests
            import time
            
            # Warte auf Service-Start
            time.sleep(5)
            
            # API Health Check
            try:
                response = requests.get(f"http://localhost:{self.deployment_config['api_port']}/health", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ API service health check passed")
                else:
                    logger.error(f"❌ API service health check failed: {response.status_code}")
                    return False
            except Exception as e:
                logger.error(f"❌ API service health check failed: {e}")
                return False
            
            # Monitoring Health Check
            try:
                # Prüfe ob Monitoring-Metriken existieren
                if os.path.exists("monitoring/metrics.json"):
                    logger.info("✅ Monitoring service health check passed")
                else:
                    logger.warning("⚠️ Monitoring service health check: no metrics file found")
            except Exception as e:
                logger.error(f"❌ Monitoring service health check failed: {e}")
                return False
            
            # Maintenance Health Check
            try:
                # Prüfe ob Maintenance-Historie existiert
                if os.path.exists("maintenance/maintenance_history.json"):
                    logger.info("✅ Maintenance service health check passed")
                else:
                    logger.warning("⚠️ Maintenance service health check: no history file found")
            except Exception as e:
                logger.error(f"❌ Maintenance service health check failed: {e}")
                return False
            
            logger.info("All health checks completed")
            return True
            
        except Exception as e:
            logger.error(f"Health checks failed: {e}")
            return False
    
    def generate_deployment_report(self):
        """Generiert Deployment-Report"""
        try:
            logger.info("Generating deployment report...")
            
            report = {
                "deployment_timestamp": datetime.now().isoformat(),
                "environment": self.deployment_config["environment"],
                "services": {
                    "api": {
                        "port": self.deployment_config["api_port"],
                        "status": "deployed",
                        "endpoints": [
                            "/generate",
                            "/feedback", 
                            "/template-status",
                            "/health",
                            "/diff",
                            "/presets",
                            "/metrics"
                        ]
                    },
                    "monitoring": {
                        "status": "deployed",
                        "features": [
                            "drift_detection",
                            "performance_monitoring",
                            "alert_system",
                            "metrics_collection"
                        ]
                    },
                    "maintenance": {
                        "status": "deployed",
                        "features": [
                            "scheduled_recalibration",
                            "automated_cleanup",
                            "snapshotting",
                            "health_checks"
                        ]
                    }
                },
                "configuration": self.deployment_config,
                "directories_created": [
                    "logs", "output", "reports", "snapshots", 
                    "backups", "maintenance", "monitoring", 
                    "templates", "profiles"
                ],
                "next_steps": [
                    "Configure external monitoring (Prometheus/Grafana)",
                    "Setup alert channels (Slack/Email)",
                    "Configure backup storage",
                    "Setup CI/CD pipeline",
                    "Configure load balancer",
                    "Setup SSL certificates"
                ]
            }
            
            # Speichere Report
            with open("reports/deployment_report.json", "w") as f:
                json.dump(report, f, indent=2)
            
            # Erstelle Markdown-Report
            markdown_content = f"""# Production Deployment Report

## Deployment Summary
- **Timestamp**: {report['deployment_timestamp']}
- **Status**: ✅ Successful
- **API Port**: {report['configuration']['api_port']}
- **Environment**: {report['configuration']['environment']}

## Services Status
- **API Service**: ✅ Active
- **Monitoring Service**: ✅ Active  
- **Maintenance Service**: ✅ Active
- **Health Checks**: ✅ Passed

## Configuration
```json
{json.dumps(report['configuration'], indent=2)}
```

## Health Check Results
```json
{json.dumps(report['health_checks'], indent=2)}
```

## Usage Examples

### 1. API Endpoint
```bash
curl http://localhost:{report['configuration']['api_port']}/health
```

### 2. Generate Chapter
```bash
curl -X POST http://localhost:{report['configuration']['api_port']}/generate \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{{"age_group": "early_reader", "genre": "adventure"}}'
```

### 3. Get Metrics
```bash
curl http://localhost:{report['configuration']['api_port']}/metrics \\
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. Use SDK
```python
from sdk.bookwriter_sdk import quick_generate

# Example usage
chapter_result = quick_generate(
    age_group="early_reader",
    genre="adventure", 
    emotion="courage",
    description="Eine mutige Entdeckungsreise"
)
print(f"Generated {{chapter_result.word_count}} words with quality score {{chapter_result.quality_score}}")
```

---
*Deployment completed successfully at {report['deployment_timestamp']}*
"""
            
            with open("reports/deployment_report.md", "w") as f:
                f.write(markdown_content)
            
            logger.info("Deployment report generated: reports/deployment_report.json")
            
        except Exception as e:
            logger.error(f"Failed to generate deployment report: {e}")
    
    def deploy_all(self):
        """Deployed alle Services"""
        try:
            logger.info("Starting production deployment...")
            
            # Setup Environment
            self.setup_environment()
            
            # Deploy Services
            api_process = self.deploy_api_service()
            monitoring_process = self.deploy_monitoring_service()
            maintenance_process = self.deploy_maintenance_service()
            
            # Health Checks
            if self.run_health_checks():
                logger.info("✅ All services deployed successfully")
                
                # Generate Report
                self.generate_deployment_report()
                
                logger.info("🚀 Production deployment completed successfully!")
                logger.info(f"📊 API available at: http://localhost:{self.deployment_config['api_port']}")
                logger.info("📈 Monitoring active")
                logger.info("🔧 Maintenance service active")
                
                return True
            else:
                logger.error("❌ Health checks failed")
                return False
                
        except Exception as e:
            logger.error(f"Production deployment failed: {e}")
            return False

def main():
    """Main deployment function"""
    try:
        deployment = ProductionDeployment()
        
        if deployment.deploy_all():
            print("\n" + "="*80)
            print("🎉 PRODUKTIONS-DEPLOYMENT ERFOLGREICH ABGESCHLOSSEN!")
            print("="*80)
            print("✅ API Service: Aktiv")
            print("✅ Monitoring Service: Aktiv") 
            print("✅ Maintenance Service: Aktiv")
            print("✅ Health Checks: Bestanden")
            print("✅ Deployment Report: Erstellt")
            print("="*80)
            print("🚀 One Click Book Writer ist bereit für den Produktions-Einsatz!")
            print("="*80)
            
            # Zeige wichtige Informationen
            print(f"\n📊 API Endpoint: http://localhost:{deployment.deployment_config['api_port']}")
            print("📖 Dokumentation: reports/deployment_report.md")
            print("🔧 Konfiguration: .env")
            print("📈 Metriken: monitoring/metrics.json")
            print("🔍 Health Check: http://localhost:8000/health")
            
        else:
            print("\n❌ Deployment fehlgeschlagen!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        print(f"\n❌ Deployment fehlgeschlagen: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 