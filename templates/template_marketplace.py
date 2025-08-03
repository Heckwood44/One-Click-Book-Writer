#!/usr/bin/env python3
"""
Template Marketplace
Lifecycle Management für Prompt-Templates mit Preset-Marketplace
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os

from core.architecture import PromptTemplate
from core.policy_engine import PolicyEngine
from core.drift_detector import DriftDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateStatus(Enum):
    """Template-Status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class TemplateCategory(Enum):
    """Template-Kategorien"""
    BEST_PERFORMING = "best_performing"
    COMMUNITY_FAVORITE = "community_favorite"
    EXPERIMENTAL = "experimental"
    STABLE = "stable"

@dataclass
class TemplateMetadata:
    """Template-Metadaten"""
    template_id: str
    name: str
    description: str
    version: str
    status: TemplateStatus
    category: TemplateCategory
    age_group: str
    genre: str
    emotion: str
    language: str
    rating: float
    usage_count: int
    created_at: datetime
    updated_at: datetime
    performance_metrics: Dict[str, Any]
    ab_test_history: List[Dict[str, Any]]
    feedback_summary: Dict[str, Any]
    tags: List[str]
    author: str
    license: str

@dataclass
class TemplateVersion:
    """Template-Version"""
    version: str
    template_hash: str
    changes: List[str]
    performance_delta: float
    created_at: datetime
    author: str
    rollback_available: bool

class TemplateMarketplace:
    """Template Marketplace mit Lifecycle Management"""
    
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.drift_detector = DriftDetector()
        
        # Template-Registry
        self.templates = {}
        self.template_versions = {}
        self.template_ratings = {}
        self.template_usage = {}
        
        # Marketplace-Konfiguration
        self.marketplace_config = {
            "auto_promotion_threshold": 0.8,
            "auto_deprecation_threshold": 0.6,
            "min_usage_for_rating": 10,
            "rating_weight_recent": 0.7,
            "rating_weight_historical": 0.3
        }
        
        # Lade bestehende Templates
        self._load_templates()
    
    def _load_templates(self):
        """Lädt bestehende Templates"""
        try:
            if os.path.exists("templates/template_registry.json"):
                with open("templates/template_registry.json", "r") as f:
                    data = json.load(f)
                    self.templates = data.get("templates", {})
                    self.template_versions = data.get("versions", {})
                    self.template_ratings = data.get("ratings", {})
                    self.template_usage = data.get("usage", {})
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def _save_templates(self):
        """Speichert Templates"""
        try:
            data = {
                "templates": self.templates,
                "versions": self.template_versions,
                "ratings": self.template_ratings,
                "usage": self.template_usage,
                "last_updated": datetime.now().isoformat()
            }
            
            with open("templates/template_registry.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving templates: {e}")
    
    def register_template(self, template: PromptTemplate, metadata: Dict[str, Any]) -> str:
        """Registriert ein neues Template"""
        try:
            template_id = template.template_id
            
            # Erstelle Template-Metadaten
            template_metadata = TemplateMetadata(
                template_id=template_id,
                name=metadata.get("name", template.name),
                description=metadata.get("description", template.description),
                version=template.version,
                status=TemplateStatus.DRAFT,
                category=TemplateCategory.EXPERIMENTAL,
                age_group=metadata.get("age_group", "unknown"),
                genre=metadata.get("genre", "unknown"),
                emotion=metadata.get("emotion", "unknown"),
                language=metadata.get("language", "de"),
                rating=0.0,
                usage_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                performance_metrics={
                    "quality_score": 0.0,
                    "success_rate": 0.0,
                    "avg_latency": 0.0
                },
                ab_test_history=[],
                feedback_summary={
                    "total_feedback": 0,
                    "avg_rating": 0.0,
                    "positive_feedback": 0,
                    "negative_feedback": 0
                },
                tags=metadata.get("tags", []),
                author=metadata.get("author", "system"),
                license=metadata.get("license", "MIT")
            )
            
            # Speichere Template
            self.templates[template_id] = template_metadata.__dict__
            self.template_versions[template_id] = []
            self.template_ratings[template_id] = []
            self.template_usage[template_id] = []
            
            # Erstelle erste Version
            self._create_template_version(template_id, template, "Initial version")
            
            # Speichere Registry
            self._save_templates()
            
            logger.info(f"Template registered: {template_id}")
            return template_id
            
        except Exception as e:
            logger.error(f"Error registering template: {e}")
            raise
    
    def _create_template_version(self, template_id: str, template: PromptTemplate, changes: str):
        """Erstellt eine neue Template-Version"""
        try:
            version = TemplateVersion(
                version=template.version,
                template_hash=template.get_hash(),
                changes=[changes],
                performance_delta=0.0,
                created_at=datetime.now(),
                author="system",
                rollback_available=True
            )
            
            self.template_versions[template_id].append(version.__dict__)
            
        except Exception as e:
            logger.error(f"Error creating template version: {e}")
    
    def update_template_performance(self, template_id: str, performance_data: Dict[str, Any]):
        """Aktualisiert Template-Performance"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template not found: {template_id}")
                return
            
            template = self.templates[template_id]
            
            # Update Performance-Metriken
            current_metrics = template["performance_metrics"]
            new_metrics = performance_data.get("metrics", {})
            
            # Gewichtete Durchschnittsberechnung
            weight_current = 0.7
            weight_new = 0.3
            
            for key in ["quality_score", "success_rate", "avg_latency"]:
                if key in new_metrics:
                    current_value = current_metrics.get(key, 0.0)
                    new_value = new_metrics[key]
                    current_metrics[key] = (current_value * weight_current + new_value * weight_new)
            
            # Update Usage Count
            template["usage_count"] += performance_data.get("usage_count", 1)
            
            # Update Timestamp
            template["updated_at"] = datetime.now().isoformat()
            
            # Prüfe Auto-Promotion/Deprecation
            self._check_auto_status_change(template_id)
            
            # Speichere Änderungen
            self._save_templates()
            
        except Exception as e:
            logger.error(f"Error updating template performance: {e}")
    
    def _check_auto_status_change(self, template_id: str):
        """Prüft automatische Status-Änderungen"""
        try:
            template = self.templates[template_id]
            current_status = TemplateStatus(template["status"])
            quality_score = template["performance_metrics"]["quality_score"]
            usage_count = template["usage_count"]
            
            # Auto-Promotion
            if (current_status == TemplateStatus.DRAFT and 
                quality_score >= self.marketplace_config["auto_promotion_threshold"] and
                usage_count >= self.marketplace_config["min_usage_for_rating"]):
                
                template["status"] = TemplateStatus.ACTIVE.value
                template["category"] = TemplateCategory.STABLE.value
                logger.info(f"Template auto-promoted: {template_id}")
            
            # Auto-Deprecation
            elif (current_status == TemplateStatus.ACTIVE and 
                  quality_score < self.marketplace_config["auto_deprecation_threshold"]):
                
                template["status"] = TemplateStatus.DEPRECATED.value
                logger.warning(f"Template auto-deprecated: {template_id}")
        
        except Exception as e:
            logger.error(f"Error checking auto status change: {e}")
    
    def add_template_rating(self, template_id: str, rating: float, feedback: str = ""):
        """Fügt Template-Bewertung hinzu"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template not found: {template_id}")
                return
            
            # Füge Rating hinzu
            rating_entry = {
                "rating": rating,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            self.template_ratings[template_id].append(rating_entry)
            
            # Update Template-Rating
            template = self.templates[template_id]
            ratings = [r["rating"] for r in self.template_ratings[template_id]]
            
            if ratings:
                # Gewichtete Durchschnittsberechnung (recente Ratings haben mehr Gewicht)
                recent_ratings = ratings[-10:]  # Letzte 10 Ratings
                historical_ratings = ratings[:-10] if len(ratings) > 10 else []
                
                recent_avg = sum(recent_ratings) / len(recent_ratings) if recent_ratings else 0
                historical_avg = sum(historical_ratings) / len(historical_ratings) if historical_ratings else 0
                
                template["rating"] = (
                    recent_avg * self.marketplace_config["rating_weight_recent"] +
                    historical_avg * self.marketplace_config["rating_weight_historical"]
                )
            
            # Update Feedback Summary
            feedback_summary = template["feedback_summary"]
            feedback_summary["total_feedback"] += 1
            feedback_summary["avg_rating"] = template["rating"]
            
            if rating >= 4:
                feedback_summary["positive_feedback"] += 1
            elif rating <= 2:
                feedback_summary["negative_feedback"] += 1
            
            # Speichere Änderungen
            self._save_templates()
            
        except Exception as e:
            logger.error(f"Error adding template rating: {e}")
    
    def get_best_performing_templates(self, segment: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Gibt die besten Templates zurück"""
        try:
            templates = []
            
            for template_id, template in self.templates.items():
                # Filter nach Segment
                if segment:
                    template_segment = f"{template['age_group']}_{template['genre']}"
                    if template_segment != segment:
                        continue
                
                # Nur aktive Templates
                if template["status"] != TemplateStatus.ACTIVE.value:
                    continue
                
                # Berechne Gesamtscore
                quality_score = template["performance_metrics"]["quality_score"]
                rating = template["rating"]
                usage_count = template["usage_count"]
                
                # Gewichteter Score
                total_score = (
                    quality_score * 0.4 +
                    rating * 0.3 +
                    min(usage_count / 100, 1.0) * 0.3
                )
                
                templates.append({
                    "template_id": template_id,
                    "name": template["name"],
                    "description": template["description"],
                    "segment": f"{template['age_group']}_{template['genre']}",
                    "quality_score": quality_score,
                    "rating": rating,
                    "usage_count": usage_count,
                    "total_score": total_score,
                    "category": template["category"],
                    "tags": template["tags"]
                })
            
            # Sortiere nach Gesamtscore
            templates.sort(key=lambda x: x["total_score"], reverse=True)
            
            return templates[:limit]
            
        except Exception as e:
            logger.error(f"Error getting best performing templates: {e}")
            return []
    
    def search_templates(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Sucht Templates"""
        try:
            results = []
            
            for template_id, template in self.templates.items():
                # Text-Suche
                searchable_text = f"{template['name']} {template['description']} {' '.join(template['tags'])}".lower()
                if query.lower() not in searchable_text:
                    continue
                
                # Filter anwenden
                if filters:
                    if not self._apply_filters(template, filters):
                        continue
                
                results.append({
                    "template_id": template_id,
                    "name": template["name"],
                    "description": template["description"],
                    "segment": f"{template['age_group']}_{template['genre']}",
                    "status": template["status"],
                    "category": template["category"],
                    "rating": template["rating"],
                    "usage_count": template["usage_count"],
                    "tags": template["tags"]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching templates: {e}")
            return []
    
    def _apply_filters(self, template: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Wendet Filter auf Template an"""
        try:
            for key, value in filters.items():
                if key == "age_group" and template["age_group"] != value:
                    return False
                elif key == "genre" and template["genre"] != value:
                    return False
                elif key == "language" and template["language"] != value:
                    return False
                elif key == "status" and template["status"] != value:
                    return False
                elif key == "category" and template["category"] != value:
                    return False
                elif key == "min_rating" and template["rating"] < value:
                    return False
                elif key == "min_usage" and template["usage_count"] < value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return False
    
    def promote_template(self, template_id: str, category: TemplateCategory = None) -> bool:
        """Promoted ein Template"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template not found: {template_id}")
                return False
            
            template = self.templates[template_id]
            template["status"] = TemplateStatus.ACTIVE.value
            
            if category:
                template["category"] = category.value
            
            template["updated_at"] = datetime.now().isoformat()
            
            # Speichere Änderungen
            self._save_templates()
            
            logger.info(f"Template promoted: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error promoting template: {e}")
            return False
    
    def deprecate_template(self, template_id: str, reason: str = "") -> bool:
        """Deprecated ein Template"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template not found: {template_id}")
                return False
            
            template = self.templates[template_id]
            template["status"] = TemplateStatus.DEPRECATED.value
            template["updated_at"] = datetime.now().isoformat()
            
            # Füge Grund zur Version hinzu
            if self.template_versions[template_id]:
                latest_version = self.template_versions[template_id][-1]
                latest_version["changes"].append(f"Deprecated: {reason}")
            
            # Speichere Änderungen
            self._save_templates()
            
            logger.info(f"Template deprecated: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deprecating template: {e}")
            return False
    
    def rollback_template(self, template_id: str, target_version: str) -> bool:
        """Rollback eines Templates"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template not found: {template_id}")
                return False
            
            versions = self.template_versions[template_id]
            
            # Finde Target-Version
            target_version_data = None
            for version in versions:
                if version["version"] == target_version:
                    target_version_data = version
                    break
            
            if not target_version_data:
                logger.warning(f"Target version not found: {target_version}")
                return False
            
            # Erstelle Rollback-Version
            rollback_version = TemplateVersion(
                version=f"{target_version}_rollback",
                template_hash=target_version_data["template_hash"],
                changes=[f"Rollback to version {target_version}"],
                performance_delta=0.0,
                created_at=datetime.now(),
                author="system",
                rollback_available=False
            )
            
            versions.append(rollback_version.__dict__)
            
            # Update Template
            template = self.templates[template_id]
            template["version"] = rollback_version.version
            template["updated_at"] = datetime.now().isoformat()
            
            # Speichere Änderungen
            self._save_templates()
            
            logger.info(f"Template rollback: {template_id} to {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back template: {e}")
            return False
    
    def export_template(self, template_id: str) -> Dict[str, Any]:
        """Exportiert ein Template"""
        try:
            if template_id not in self.templates:
                logger.warning(f"Template not found: {template_id}")
                return {}
            
            template = self.templates[template_id]
            versions = self.template_versions[template_id]
            ratings = self.template_ratings[template_id]
            usage = self.template_usage[template_id]
            
            return {
                "template": template,
                "versions": versions,
                "ratings": ratings,
                "usage": usage,
                "export_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exporting template: {e}")
            return {}
    
    def import_template(self, template_data: Dict[str, Any]) -> str:
        """Importiert ein Template"""
        try:
            template = template_data["template"]
            template_id = template["template_id"]
            
            # Prüfe ob Template bereits existiert
            if template_id in self.templates:
                template_id = f"{template_id}_imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                template["template_id"] = template_id
            
            # Importiere Template
            self.templates[template_id] = template
            self.template_versions[template_id] = template_data.get("versions", [])
            self.template_ratings[template_id] = template_data.get("ratings", [])
            self.template_usage[template_id] = template_data.get("usage", [])
            
            # Speichere Registry
            self._save_templates()
            
            logger.info(f"Template imported: {template_id}")
            return template_id
            
        except Exception as e:
            logger.error(f"Error importing template: {e}")
            raise
    
    def get_marketplace_summary(self) -> Dict[str, Any]:
        """Gibt Marketplace-Zusammenfassung zurück"""
        try:
            total_templates = len(self.templates)
            active_templates = len([t for t in self.templates.values() if t["status"] == TemplateStatus.ACTIVE.value])
            best_performing = len([t for t in self.templates.values() if t["category"] == TemplateCategory.BEST_PERFORMING.value])
            
            # Top-Segmente
            segments = {}
            for template in self.templates.values():
                segment = f"{template['age_group']}_{template['genre']}"
                if segment not in segments:
                    segments[segment] = {"count": 0, "avg_rating": 0.0, "total_usage": 0}
                
                segments[segment]["count"] += 1
                segments[segment]["avg_rating"] += template["rating"]
                segments[segment]["total_usage"] += template["usage_count"]
            
            # Berechne Durchschnitte
            for segment_data in segments.values():
                if segment_data["count"] > 0:
                    segment_data["avg_rating"] /= segment_data["count"]
            
            return {
                "total_templates": total_templates,
                "active_templates": active_templates,
                "best_performing_templates": best_performing,
                "top_segments": sorted(segments.items(), key=lambda x: x[1]["total_usage"], reverse=True)[:5],
                "recent_activity": {
                    "templates_added_7d": len([t for t in self.templates.values() 
                                             if (datetime.now() - datetime.fromisoformat(t["created_at"])).days <= 7]),
                    "templates_updated_7d": len([t for t in self.templates.values() 
                                               if (datetime.now() - datetime.fromisoformat(t["updated_at"])).days <= 7])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting marketplace summary: {e}")
            return {}

# Singleton Instance
template_marketplace = TemplateMarketplace() 