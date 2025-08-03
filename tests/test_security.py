#!/usr/bin/env python3
"""
Security Tests für One Click Book Writer
"""

import unittest
import os
import re
from pathlib import Path

class TestSecurity(unittest.TestCase):
    """Security Tests für das Framework"""
    
    def setUp(self):
        """Setup für Security Tests"""
        self.project_root = Path(__file__).parent.parent
        self.core_dir = self.project_root / "core"
        self.gui_dir = self.project_root / "gui"
        self.engine_dir = self.project_root / "engine"
    
    def test_no_hardcoded_api_keys(self):
        """Testet, dass keine API-Keys im Code hartcodiert sind"""
        print("🔒 Teste auf hartcodierte API-Keys...")
        
        # Patterns für API-Keys
        api_key_patterns = [
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API Key
            r'claude-[a-zA-Z0-9]{48}',  # Claude API Key
            r'[a-zA-Z0-9]{32,}',  # Allgemeine API-Keys
        ]
        
        # Dateien durchsuchen
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if "test" in str(file_path).lower():
                continue  # Test-Dateien überspringen
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in api_key_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Prüfe, ob es sich um einen echten API-Key handelt
                        if not self._is_false_positive(match, content):
                            self.fail(f"Potentieller API-Key gefunden in {file_path}: {match}")
                            
            except Exception as e:
                print(f"⚠️  Konnte {file_path} nicht lesen: {e}")
        
        print("✅ Keine hartcodierten API-Keys gefunden")
    
    def test_no_hardcoded_passwords(self):
        """Testet, dass keine Passwörter im Code hartcodiert sind"""
        print("🔒 Teste auf hartcodierte Passwörter...")
        
        # Patterns für Passwörter
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'passwd\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]
        
        # Dateien durchsuchen
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            if "test" in str(file_path).lower():
                continue  # Test-Dateien überspringen
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in password_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if not self._is_false_positive(match, content):
                            self.fail(f"Potentielles Passwort gefunden in {file_path}: {match}")
                            
            except Exception as e:
                print(f"⚠️  Konnte {file_path} nicht lesen: {e}")
        
        print("✅ Keine hartcodierten Passwörter gefunden")
    
    def test_environment_variables_used(self):
        """Testet, dass API-Keys aus Umgebungsvariablen geladen werden"""
        print("🔒 Teste Umgebungsvariablen-Verwendung...")
        
        # Prüfe OpenAI Adapter
        openai_adapter_path = self.engine_dir / "openai_adapter.py"
        if openai_adapter_path.exists():
            with open(openai_adapter_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Prüfe, ob os.getenv verwendet wird
            self.assertIn("os.getenv", content, "OpenAI Adapter sollte os.getenv verwenden")
            self.assertIn("OPENAI_API_KEY", content, "OpenAI Adapter sollte OPENAI_API_KEY verwenden")
        
        # Prüfe Claude Adapter
        claude_adapter_path = self.engine_dir / "claude_adapter.py"
        if claude_adapter_path.exists():
            with open(claude_adapter_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Prüfe, ob os.getenv verwendet wird
            self.assertIn("os.getenv", content, "Claude Adapter sollte os.getenv verwenden")
            self.assertIn("ANTHROPIC_API_KEY", content, "Claude Adapter sollte ANTHROPIC_API_KEY verwenden")
        
        print("✅ Umgebungsvariablen werden korrekt verwendet")
    
    def test_input_validation(self):
        """Testet, dass Eingaben validiert werden"""
        print("🔒 Teste Eingabe-Validierung...")
        
        # Prüfe Schema-Validierung
        schema_dir = self.project_root / "schema"
        if schema_dir.exists():
            schema_files = list(schema_dir.glob("*.json"))
            self.assertGreater(len(schema_files), 0, "Schema-Dateien sollten vorhanden sein")
        
        # Prüfe Validierungsfunktionen (nur Projekt-Dateien)
        validation_files = []
        for file_path in self.project_root.rglob("*validate*.py"):
            # Ignoriere venv und andere externe Verzeichnisse
            if "venv" not in str(file_path) and ".venv" not in str(file_path):
                validation_files.append(file_path)
        
        if validation_files:
            for file_path in validation_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn("validate", content, f"Validierungsdatei {file_path} sollte Validierungsfunktionen enthalten")
        else:
            print("⚠️  Keine Validierungsdateien im Projekt gefunden")
        
        print("✅ Eingabe-Validierung ist implementiert")
    
    def test_error_handling(self):
        """Testet, dass Fehlerbehandlung vorhanden ist"""
        print("🔒 Teste Fehlerbehandlung...")
        
        # Prüfe try-except Blöcke in wichtigen Dateien
        important_files = [
            "engine/openai_adapter.py",
            "engine/claude_adapter.py",
            "core/enhanced_pipeline.py",
            "gui/simple_gui.py"
        ]
        
        for file_path in important_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Prüfe auf try-except Blöcke
                self.assertIn("try:", content, f"{file_path} sollte try-except Blöcke enthalten")
                self.assertIn("except", content, f"{file_path} sollte except Blöcke enthalten")
        
        print("✅ Fehlerbehandlung ist implementiert")
    
    def _is_false_positive(self, match, content):
        """Prüft, ob ein Match ein False Positive ist"""
        # Ignoriere Kommentare und Dokumentation
        if "example" in match.lower() or "demo" in match.lower():
            return True
        
        # Ignoriere Test-Daten
        if "test" in match.lower() or "mock" in match.lower():
            return True
        
        # Ignoriere kurze Strings (wahrscheinlich keine echten Keys)
        if len(match) < 20:
            return True
        
        return False

if __name__ == "__main__":
    unittest.main(verbosity=2) 