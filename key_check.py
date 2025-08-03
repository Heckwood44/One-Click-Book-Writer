#!/usr/bin/env python3
"""
One Click Book Writer - API Key Validation Module

Dieses Modul prüft die Verfügbarkeit und Gültigkeit der API Keys für:
- OpenAI (ChatGPT) - Für Kapitelgenerierung
- Anthropic (Claude) - Für Prompt-Optimierung und Story-Entwicklung

Author: One Click Book Writer Team
Version: 1.0.0
"""

import os
from dotenv import load_dotenv
from typing import Dict
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIKeyChecker:
    """API Key Validierung und Status-Management"""

    def __init__(self):
        """Initialisiert den API Key Checker"""
        self.load_environment()
        self.openai_key = None
        self.claude_key = None
        self.check_keys()

    def load_environment(self):
        """Lädt die Umgebungsvariablen aus .env Datei"""
        try:
            load_dotenv()
            logger.info("Umgebungsvariablen erfolgreich geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Umgebungsvariablen: {e}")

    def check_keys(self):
        """Prüft die Verfügbarkeit der API Keys"""
        # OpenAI API Key prüfen
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if self.openai_key:
            # Entferne Leerzeichen und prüfe auf Platzhalter
            self.openai_key = self.openai_key.strip()
            if not self.openai_key or self.openai_key in [
                "your_openai_api_key_here",
                "",
            ]:
                self.openai_key = None
                logger.warning("OpenAI API Key ist leer oder Platzhalter")
            else:
                logger.info("OpenAI API Key gefunden")
        else:
            logger.warning("OpenAI API Key nicht gefunden")

        # Claude API Key prüfen
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")
        if self.claude_key:
            # Entferne Leerzeichen und prüfe auf Platzhalter
            self.claude_key = self.claude_key.strip()
            if not self.claude_key or self.claude_key in [
                "your_anthropic_api_key_here",
                "",
            ]:
                self.claude_key = None
                logger.warning("Claude API Key ist leer oder Platzhalter")
            else:
                logger.info("Claude API Key gefunden")
        else:
            logger.warning("Claude API Key nicht gefunden")

    def get_status(self) -> Dict[str, bool]:
        """Gibt den Status der API Keys zurück"""
        return {
            "openai_available": bool(self.openai_key),
            "claude_available": bool(self.claude_key),
        }

    def get_status_text(self) -> str:
        """Gibt eine benutzerfreundliche Status-Text zurück"""
        openai_status = "✅ Verfügbar" if self.openai_key else "❌ Fehlt"
        claude_status = "✅ Verfügbar" if self.claude_key else "❌ Fehlt"
        return f"OpenAI: {openai_status} | Claude: {claude_status}"

    def validate_key_format(self, key: str, key_type: str) -> bool:
        """Validiert das Format eines API Keys"""
        if not key:
            return False

        if key_type == "openai":
            # OpenAI Keys beginnen normalerweise mit 'sk-'
            return key.startswith("sk-") and len(key) > 20
        elif key_type == "claude":
            # Claude Keys beginnen normalerweise mit 'sk-ant-'
            return key.startswith("sk-ant-") and len(key) > 20
        else:
            return False

    def get_validation_report(self) -> Dict[str, Dict[str, any]]:
        """Erstellt einen detaillierten Validierungsbericht"""
        report = {
            "openai": {
                "available": bool(self.openai_key),
                "valid_format": self.validate_key_format(self.openai_key, "openai")
                if self.openai_key
                else False,
                "key_preview": f"{self.openai_key[:10]}..."
                if self.openai_key
                else None,
            },
            "claude": {
                "available": bool(self.claude_key),
                "valid_format": self.validate_key_format(self.claude_key, "claude")
                if self.claude_key
                else False,
                "key_preview": f"{self.claude_key[:10]}..."
                if self.claude_key
                else None,
            },
        }
        return report

    def can_generate_chapters(self) -> bool:
        """Prüft ob Kapitelgenerierung möglich ist (benötigt OpenAI)"""
        return bool(
            self.openai_key and self.validate_key_format(self.openai_key, "openai")
        )

    def can_optimize_prompts(self) -> bool:
        """Prüft ob Prompt-Optimierung möglich ist (benötigt Claude)"""
        return bool(
            self.claude_key and self.validate_key_format(self.claude_key, "claude")
        )

    def get_missing_services(self) -> list:
        """Gibt eine Liste der fehlenden Services zurück"""
        missing = []
        if not self.can_generate_chapters():
            missing.append("OpenAI (Kapitelgenerierung)")
        if not self.can_optimize_prompts():
            missing.append("Claude (Prompt-Optimierung)")
        return missing

    def print_status(self):
        """Gibt den aktuellen Status aus"""
        print("=" * 50)
        print("🔑 One Click Book Writer - API Key Status")
        print("=" * 50)

        # Status für OpenAI
        if self.can_generate_chapters():
            print("✅ OpenAI (ChatGPT): Verfügbar - Kapitelgenerierung möglich")
        else:
            print(
                "❌ OpenAI (ChatGPT): Nicht verfügbar - Kapitelgenerierung nicht möglich"
            )

        # Status für Claude
        if self.can_optimize_prompts():
            print("✅ Claude: Verfügbar - Prompt-Optimierung möglich")
        else:
            print("❌ Claude: Nicht verfügbar - Prompt-Optimierung nicht möglich")

        # Fehlende Services
        missing = self.get_missing_services()
        if missing:
            print(f"\n⚠️  Fehlende Services: {', '.join(missing)}")
            print("💡 Tipp: Füge die entsprechenden API Keys zur .env Datei hinzu")
        else:
            print("\n🎉 Alle Services verfügbar!")

        print("=" * 50)


def main():
    """Hauptfunktion für Kommandozeilen-Test"""
    checker = APIKeyChecker()
    checker.print_status()

    # Detaillierter Bericht
    report = checker.get_validation_report()
    print("\n📊 Detaillierter Bericht:")
    for service, details in report.items():
        print(f"  {service.upper()}:")
        print(f"    Verfügbar: {details['available']}")
        print(f"    Gültiges Format: {details['valid_format']}")
        if details["key_preview"]:
            print(f"    Key Preview: {details['key_preview']}")
        print()


if __name__ == "__main__":
    main()
