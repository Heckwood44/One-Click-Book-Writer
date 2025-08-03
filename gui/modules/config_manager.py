#!/usr/bin/env python3
"""
Configuration Manager Module
Zentrale Konfigurationsverwaltung für One Click Book Writer
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Zentrale Konfigurationsverwaltung"""
    
    def __init__(self, config_file: str = "config.json") -> None:
        """
        Initialisiert den Config Manager
        
        Args:
            config_file: Pfad zur Konfigurationsdatei
        """
        self.config_file: str = config_file
        self.config: Dict[str, Any] = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Lädt die Konfiguration aus der Datei"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Konfiguration aus {self.config_file} geladen")
                    return config
            else:
                logger.info(f"Konfigurationsdatei {self.config_file} nicht gefunden, verwende Standard")
                return self._get_default_config()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.exception(f"Unerwarteter Fehler beim Laden der Konfiguration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Gibt Standard-Konfiguration zurück"""
        return {
            "api": {
                "openai_model": "gpt-4",
                "claude_model": "claude-3-sonnet-20240229",
                "max_tokens": 8000,
                "temperature": 0.4,
                "timeout": 30
            },
            "gui": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "default",
                "auto_save": True,
                "auto_save_interval": 300
            },
            "generation": {
                "default_engine": "claude",
                "batch_size": 3,
                "max_workers": 3,
                "quality_threshold": 0.7
            },
            "output": {
                "default_format": "markdown",
                "save_path": "output/",
                "backup_enabled": True,
                "backup_count": 5
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "file_path": "logs/",
                "max_file_size": 10485760,  # 10MB
                "backup_count": 5
            }
        }
    
    def save_config(self) -> bool:
        """Speichert die Konfiguration"""
        try:
            # Erstelle Verzeichnis falls nicht vorhanden
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Konfiguration in {self.config_file} gespeichert")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unerwarteter Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Konfigurationswert
        
        Args:
            key: Konfigurationsschlüssel (dot notation: "api.openai_model")
            default: Standardwert falls nicht gefunden
            
        Returns:
            Konfigurationswert oder Standardwert
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Konfiguration '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Setzt einen Konfigurationswert
        
        Args:
            key: Konfigurationsschlüssel (dot notation: "api.openai_model")
            value: Neuer Wert
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigiere zu dem entsprechenden Dictionary
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Setze den Wert
            config[keys[-1]] = value
            logger.info(f"Konfiguration '{key}' auf '{value}' gesetzt")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Setzen der Konfiguration '{key}': {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        Aktualisiert mehrere Konfigurationswerte
        
        Args:
            updates: Dictionary mit Updates
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            for key, value in updates.items():
                if not self.set(key, value):
                    return False
            return True
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Konfiguration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Setzt Konfiguration auf Standardwerte zurück"""
        try:
            self.config = self._get_default_config()
            logger.info("Konfiguration auf Standardwerte zurückgesetzt")
            return self.save_config()
        except Exception as e:
            logger.error(f"Fehler beim Zurücksetzen der Konfiguration: {e}")
            return False
    
    def get_api_config(self) -> Dict[str, Any]:
        """Gibt API-Konfiguration zurück"""
        return self.get("api", {})
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Gibt GUI-Konfiguration zurück"""
        return self.get("gui", {})
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Gibt Generierungs-Konfiguration zurück"""
        return self.get("generation", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Gibt Output-Konfiguration zurück"""
        return self.get("output", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Gibt Logging-Konfiguration zurück"""
        return self.get("logging", {})
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validiert die Konfiguration
        
        Returns:
            Dictionary mit Validierungsergebnissen
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Prüfe API-Konfiguration
            api_config = self.get_api_config()
            if not api_config.get("openai_model"):
                validation_results["warnings"].append("OpenAI Model nicht konfiguriert")
            
            if not api_config.get("claude_model"):
                validation_results["warnings"].append("Claude Model nicht konfiguriert")
            
            # Prüfe GUI-Konfiguration
            gui_config = self.get_gui_config()
            if gui_config.get("window_width", 0) <= 0:
                validation_results["errors"].append("Ungültige Fensterbreite")
                validation_results["valid"] = False
            
            if gui_config.get("window_height", 0) <= 0:
                validation_results["errors"].append("Ungültige Fensterhöhe")
                validation_results["valid"] = False
            
            # Prüfe Generierungs-Konfiguration
            gen_config = self.get_generation_config()
            if gen_config.get("max_workers", 0) <= 0:
                validation_results["errors"].append("Ungültige Anzahl Worker")
                validation_results["valid"] = False
            
            # Prüfe Output-Konfiguration
            output_config = self.get_output_config()
            save_path = output_config.get("save_path", "")
            if save_path and not os.path.exists(save_path):
                validation_results["warnings"].append(f"Output-Pfad existiert nicht: {save_path}")
            
        except Exception as e:
            validation_results["errors"].append(f"Validierungsfehler: {e}")
            validation_results["valid"] = False
        
        return validation_results 