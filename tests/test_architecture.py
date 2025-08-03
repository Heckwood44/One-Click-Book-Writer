#!/usr/bin/env python3
"""
Architecture Tests für One Click Book Writer
"""

import unittest
import json
from pathlib import Path

class TestArchitecture(unittest.TestCase):
    """Tests für Architektur-Validierung"""
    
    def setUp(self):
        """Setup für Architecture Tests"""
        self.project_root = Path(__file__).parent.parent
        
    def test_module_structure(self):
        """Testet die Modul-Struktur"""
        print("🏗️  Teste Modul-Struktur...")
        
        # Erwartete Verzeichnisse
        expected_dirs = [
            "core",
            "engine", 
            "gui",
            "compiler",
            "schema",
            "utils",
            "tests"
        ]
        
        for dir_name in expected_dirs:
            dir_path = self.project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Verzeichnis {dir_name} sollte existieren")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} sollte ein Verzeichnis sein")
        
        print("✅ Modul-Struktur ist korrekt")
    
    def test_core_modules_exist(self):
        """Testet, dass alle Core-Module existieren"""
        print("🏗️  Teste Core-Module...")
        
        # Erwartete Core-Module
        expected_core_modules = [
            "enhanced_pipeline.py",
            "feedback_intelligence.py", 
            "prompt_optimizer.py",
            "robustness_manager.py",
            "architecture.py"
        ]
        
        core_dir = self.project_root / "core"
        for module_name in expected_core_modules:
            module_path = core_dir / module_name
            self.assertTrue(module_path.exists(), f"Core-Modul {module_name} sollte existieren")
        
        print("✅ Alle Core-Module existieren")
    
    def test_engine_modules_exist(self):
        """Testet, dass alle Engine-Module existieren"""
        print("🏗️  Teste Engine-Module...")
        
        # Erwartete Engine-Module
        expected_engine_modules = [
            "openai_adapter.py",
            "claude_adapter.py"
        ]
        
        engine_dir = self.project_root / "engine"
        for module_name in expected_engine_modules:
            module_path = engine_dir / module_name
            self.assertTrue(module_path.exists(), f"Engine-Modul {module_name} sollte existieren")
        
        print("✅ Alle Engine-Module existieren")
    
    def test_data_structures(self):
        """Testet Datenstrukturen"""
        print("🏗️  Teste Datenstrukturen...")
        
        # Prüfe architecture.py für Datenstrukturen
        architecture_file = self.project_root / "core" / "architecture.py"
        if architecture_file.exists():
            with open(architecture_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Prüfe auf wichtige Datenstrukturen
            expected_classes = [
                "PromptFrame",
                "PromptTemplate", 
                "GenerationResult",
                "EvaluationResult",
                "OptimizationResult",
                "ABTestResult",
                "PipelineResult"
            ]
            
            for class_name in expected_classes:
                self.assertIn(class_name, content, f"Datenstruktur {class_name} sollte definiert sein")
        
        print("✅ Datenstrukturen sind definiert")
    
    def test_import_structure(self):
        """Testet Import-Struktur"""
        print("🏗️  Teste Import-Struktur...")
        
        # Prüfe wichtige Module auf korrekte Imports
        important_modules = [
            "core/enhanced_pipeline.py",
            "engine/openai_adapter.py",
            "engine/claude_adapter.py"
        ]
        
        for module_path in important_modules:
            full_path = self.project_root / module_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Prüfe auf Standard-Imports
                self.assertIn("import", content, f"{module_path} sollte Imports enthalten")
                
                # Prüfe auf relative Imports
                if "from ." in content or "from .." in content:
                    print(f"⚠️  {module_path} verwendet relative Imports")
        
        print("✅ Import-Struktur ist korrekt")
    
    def test_configuration_files(self):
        """Testet Konfigurationsdateien"""
        print("🏗️  Teste Konfigurationsdateien...")
        
        # Erwartete Konfigurationsdateien
        expected_config_files = [
            "requirements.txt",
            "README.md",
            ".gitignore"
        ]
        
        for config_file in expected_config_files:
            file_path = self.project_root / config_file
            self.assertTrue(file_path.exists(), f"Konfigurationsdatei {config_file} sollte existieren")
        
        # Prüfe requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Prüfe auf wichtige Dependencies
            important_deps = [
                "openai",
                "anthropic", 
                "pytest",
                "pytest-cov"
            ]
            
            for dep in important_deps:
                self.assertIn(dep, content, f"Dependency {dep} sollte in requirements.txt stehen")
        
        print("✅ Konfigurationsdateien sind korrekt")
    
    def test_test_structure(self):
        """Testet Test-Struktur"""
        print("🏗️  Teste Test-Struktur...")
        
        tests_dir = self.project_root / "tests"
        
        # Prüfe auf wichtige Test-Dateien
        expected_test_files = [
            "test_security.py",
            "test_promotion_guardrails.py", 
            "test_architecture.py",
            "smoke_test.py"
        ]
        
        for test_file in expected_test_files:
            file_path = tests_dir / test_file
            self.assertTrue(file_path.exists(), f"Test-Datei {test_file} sollte existieren")
        
        print("✅ Test-Struktur ist korrekt")
    
    def test_ci_cd_configuration(self):
        """Testet CI/CD-Konfiguration"""
        print("🏗️  Teste CI/CD-Konfiguration...")
        
        # Prüfe GitHub Actions
        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml"))
            self.assertGreater(len(workflow_files), 0, "GitHub Actions Workflows sollten existieren")
            
            # Prüfe CI-Pipeline
            ci_file = workflows_dir / "ci.yml"
            if ci_file.exists():
                with open(ci_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Prüfe auf wichtige CI-Schritte
                expected_steps = [
                    "test",
                    "lint", 
                    "security"
                ]
                
                for step in expected_steps:
                    self.assertIn(step, content, f"CI-Schritt {step} sollte in ci.yml definiert sein")
        
        print("✅ CI/CD-Konfiguration ist korrekt")

if __name__ == "__main__":
    unittest.main(verbosity=2) 