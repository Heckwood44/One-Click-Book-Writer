#!/usr/bin/env python3
"""
One Click Book Writer - Pipeline Audit Script
Version: 2.0.0
"""

import json
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from compiler.prompt_compiler import compile_prompt_for_chatgpt, validate_prompt_structure, generate_prompt_hash
from schema.validate_input import validate_json_schema
from utils.quality_evaluator import QualityEvaluator
from prompt_router import PromptRouter
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

class PipelineAuditor:
    def __init__(self):
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "audit_version": "2.0.0",
            "sections": {},
            "summary": {},
            "errors": [],
            "warnings": [],
            "fallbacks_applied": [],
            "quality_metrics": {},
            "costs": {}
        }
        
        self.router = PromptRouter()
        self.evaluator = QualityEvaluator()
        
    def run_full_audit(self) -> Dict[str, Any]:
        """Führt das vollständige Audit durch"""
        print("🔍 Starting One Click Book Writer Pipeline Audit")
        print("=" * 60)
        
        # A. Environment & Setup
        self.audit_environment()
        
        # B. Input & Validation
        self.audit_input_validation()
        
        # C. Prompt-Erzeugung
        self.audit_prompt_generation()
        
        # D. Textgenerierung
        self.audit_text_generation()
        
        # E. Output & Meta
        self.audit_output_metadata()
        
        # F. Qualitätsbewertung
        self.audit_quality_evaluation()
        
        # G. Testing & CI
        self.audit_testing_ci()
        
        # H. UI / Integration
        self.audit_ui_integration()
        
        # Zusammenfassung erstellen
        self.create_summary()
        
        return self.audit_results
    
    def audit_environment(self):
        """A. Environment & Setup Audit"""
        print("\n📋 A. Environment & Setup")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # Python Version
            python_version = sys.version
            section["details"]["python_version"] = python_version
            
            # Virtual Environment
            virtual_env = sys.prefix
            section["details"]["virtual_env"] = virtual_env
            
            # Requirements
            requirements_file = project_root / "requirements.txt"
            if requirements_file.exists():
                section["details"]["requirements_file"] = "present"
            else:
                section["errors"].append("requirements.txt nicht gefunden")
            
            # Environment Variables
            openai_key = os.getenv('OPENAI_API_KEY')
            claude_key = os.getenv('ANTHROPIC_API_KEY')
            
            if openai_key:
                section["details"]["openai_key"] = "present"
            else:
                section["errors"].append("OPENAI_API_KEY nicht gefunden")
            
            if claude_key:
                section["details"]["claude_key"] = "present"
            else:
                section["warnings"].append("ANTHROPIC_API_KEY nicht gefunden (Claude-Optimierung nicht verfügbar)")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Environment-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["environment"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_input_validation(self):
        """B. Input & Validation Audit"""
        print("\n📋 B. Input & Validation")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # JSON-Datei laden
            input_file = project_root / "data" / "generate_chapter_full_extended.json"
            if not input_file.exists():
                section["errors"].append("Input-JSON-Datei nicht gefunden")
                section["status"] = "failed"
                self.audit_results["sections"]["input_validation"] = section
                return
            
            with open(input_file, 'r', encoding='utf-8') as f:
                prompt_frame = json.load(f)
            
            section["details"]["input_file"] = "loaded"
            section["details"]["input_size"] = len(json.dumps(prompt_frame))
            
            # Schema-Validierung
            schema_file = project_root / "schema" / "prompt_frame.schema.json"
            if schema_file.exists():
                success, message = validate_json_schema(prompt_frame, str(schema_file))
                if success:
                    section["details"]["schema_validation"] = "passed"
                else:
                    section["errors"].append(f"Schema-Validierung fehlgeschlagen: {message}")
            else:
                section["warnings"].append("Schema-Datei nicht gefunden")
            
            # Prompt-Struktur-Validierung
            if validate_prompt_structure(prompt_frame):
                section["details"]["structure_validation"] = "passed"
                
                # Fallback-Check
                language_config = prompt_frame.get("input", {}).get("language", {})
                if not language_config.get("bilingual_output", False):
                    section["fallbacks_applied"] = ["bilingual_output auf False gesetzt"]
            else:
                section["errors"].append("Prompt-Struktur-Validierung fehlgeschlagen")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Input-Validation-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["input_validation"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_prompt_generation(self):
        """C. Prompt-Erzeugung Audit"""
        print("\n📋 C. Prompt-Erzeugung")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # Prompt kompilieren
            input_file = project_root / "data" / "generate_chapter_full_extended.json"
            with open(input_file, 'r', encoding='utf-8') as f:
                prompt_frame = json.load(f)
            
            prompt = compile_prompt_for_chatgpt(prompt_frame)
            section["details"]["prompt_length"] = len(prompt)
            section["details"]["prompt_hash"] = generate_prompt_hash(prompt)
            
            # Prompt-Inhalt prüfen
            required_elements = [
                "---",
                "DEUTSCHE VERSION",
                "ENGLISH VERSION"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in prompt:
                    missing_elements.append(element)
            
            # System Note mit Signatur prüfen - Canvas Execution Plan
            system_note_signature = "SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"
            if system_note_signature in prompt:
                section["details"]["system_note"] = "present_with_signature"
                section["details"]["canvas_compliance"] = "full"
            elif "Ein Weltklasse-Autor ist kein" in prompt:
                section["details"]["system_note"] = "present_fuzzy_match"
                section["details"]["canvas_compliance"] = "partial"
            else:
                missing_elements.append("System Note")
                section["details"]["canvas_compliance"] = "missing"
            
            # Bilinguale Struktur mit Mindestlängen prüfen
            if "---" in prompt:
                parts = prompt.split("---")
                if len(parts) >= 2:
                    german_part = parts[0].strip()
                    english_part = parts[1].strip()
                    
                    # Mindestlängen prüfen (50 Wörter pro Sprache)
                    german_words = len(german_part.split())
                    english_words = len(english_part.split())
                    
                    if german_words >= 50 and english_words >= 50:
                        section["details"]["bilingual_split"] = "valid_with_minimum_length"
                        section["details"]["german_words"] = german_words
                        section["details"]["english_words"] = english_words
                    else:
                        section["details"]["bilingual_split"] = "invalid_insufficient_length"
                        section["errors"].append(f"Bilinguale Teile zu kurz: DE={german_words}, EN={english_words} Wörter")
                else:
                    section["details"]["bilingual_split"] = "invalid_structure"
                    section["errors"].append("Bilinguale Struktur unvollständig")
            else:
                section["details"]["bilingual_split"] = "missing"
                section["errors"].append("Keine bilinguale Trennung gefunden")
            
            if missing_elements:
                section["errors"].extend([f"Fehlendes Element: {elem}" for elem in missing_elements])
            else:
                section["details"]["prompt_elements"] = "complete"
            
            # Bilingual-Check
            if "---" in prompt:
                section["details"]["bilingual_format"] = "correct"
            else:
                section["errors"].append("Bilinguale Trennung (---) nicht gefunden")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Prompt-Generation-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["prompt_generation"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_text_generation(self):
        """D. Textgenerierung Audit"""
        print("\n📋 D. Textgenerierung")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # Pipeline ausführen
            result = self.router.run_full_pipeline(
                prompt_frame_path="data/generate_chapter_full_extended.json",
                optimize_with_claude=True,
                chapter_number=1
            )
            
            if result["success"]:
                section["details"]["generation"] = "successful"
                section["details"]["quality_score"] = result.get("quality_evaluation", {}).get("overall_bilingual_score", "N/A")
                
                # Output-Dateien prüfen
                output_files = result.get("output_files", {})
                for lang, file_path in output_files.items():
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        section["details"][f"{lang}_file"] = f"present ({file_size} bytes)"
                        
                        if file_size == 0:
                            section["errors"].append(f"{lang}_file ist leer")
                    else:
                        section["errors"].append(f"{lang}_file nicht gefunden")
                
                # Token-Logging
                if "token_usage" in result:
                    section["details"]["token_logging"] = "active"
                    section["costs"] = result["token_usage"]
                
                # Bilinguale Trennung prüfen
                de_file = output_files.get("german", "")
                en_file = output_files.get("english", "")
                
                if os.path.exists(de_file) and os.path.exists(en_file):
                    with open(de_file, 'r', encoding='utf-8') as f:
                        de_content = f.read()
                    with open(en_file, 'r', encoding='utf-8') as f:
                        en_content = f.read()
                    
                    if de_content.strip() and en_content.strip():
                        section["details"]["bilingual_separation"] = "successful"
                    else:
                        section["errors"].append("Eine oder beide Sprachversionen sind leer")
                
            else:
                section["errors"].extend(result.get("errors", ["Unbekannter Generierungsfehler"]))
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Text-Generation-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["text_generation"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_output_metadata(self):
        """E. Output & Meta Audit"""
        print("\n📋 E. Output & Meta")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # Metadaten-Datei prüfen
            meta_file = project_root / "output" / "chapter_1_meta.json"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                section["details"]["metadata_file"] = "present"
                
                # Erforderliche Felder prüfen
                required_fields = [
                    "chapter_number",
                    "prompt_versioning",
                    "book_metadata",
                    "quality_evaluation"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in metadata:
                        missing_fields.append(field)
                
                if missing_fields:
                    section["errors"].extend([f"Fehlendes Metadaten-Feld: {field}" for field in missing_fields])
                else:
                    section["details"]["metadata_structure"] = "complete"
                
                # Prompt-Hash prüfen
                if "prompt_versioning" in metadata:
                    prompt_hash = metadata["prompt_versioning"].get("latest_version_hash")
                    if prompt_hash:
                        section["details"]["prompt_hash"] = prompt_hash
                        
                        # Hash mit tatsächlichem Prompt abgleichen
                        try:
                            from compiler.prompt_compiler import generate_prompt_hash
                            # Hier würden wir den tatsächlichen Prompt laden
                            # Für jetzt nur den Hash validieren
                            if len(prompt_hash) >= 8:
                                section["details"]["hash_validation"] = "valid_format"
                            else:
                                section["details"]["hash_validation"] = "invalid_format"
                                section["warnings"].append("Prompt-Hash Format ungültig")
                        except Exception as e:
                            section["warnings"].append(f"Hash-Validierung fehlgeschlagen: {e}")
                    else:
                        section["warnings"].append("Prompt-Hash nicht in Metadaten")
                
                # Canvas-Compliance prüfen
                if "canvas_compliance" in metadata:
                    compliance = metadata["canvas_compliance"]
                    section["details"]["canvas_compliance"] = compliance.get("overall_compliance", "unknown")
                    if compliance.get("overall_compliance") != "full":
                        section["warnings"].append("Canvas-Compliance nicht vollständig")
                else:
                    section["details"]["canvas_compliance"] = "missing"
                    section["warnings"].append("Canvas-Compliance in Meta fehlt")
                
                # Review-Flags prüfen
                if "review_required" in metadata:
                    section["details"]["review_flags"] = "present"
                    if metadata["review_required"]:
                        section["warnings"].append("Review erforderlich")
                else:
                    section["details"]["review_flags"] = "missing"
                    section["warnings"].append("Review-Flags in Meta fehlen")
                
                # Qualitätsbewertung prüfen
                if "quality_evaluation" in metadata:
                    quality_data = metadata["quality_evaluation"]
                    if "german_evaluation" in quality_data and "english_evaluation" in quality_data:
                        section["details"]["quality_evaluation"] = "complete"
                        section["quality_metrics"] = quality_data
                    else:
                        section["warnings"].append("Unvollständige Qualitätsbewertung")
                
            else:
                section["errors"].append("Metadaten-Datei nicht gefunden")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Output-Meta-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["output_metadata"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_quality_evaluation(self):
        """F. Qualitätsbewertung Audit"""
        print("\n📋 F. Qualitätsbewertung")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # Qualitätsbewertung aus Metadaten
            meta_file = project_root / "output" / "chapter_1_meta.json"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                quality_data = metadata.get("quality_evaluation", {})
                
                # Deutsche Bewertung
                de_eval = quality_data.get("german_evaluation", {})
                if de_eval:
                    de_score = de_eval.get("overall_score", 0)
                    section["details"]["german_score"] = de_score
                    section["details"]["german_level"] = de_eval.get("quality_level", "Unknown")
                    
                    if de_score < 0.5:
                        section["warnings"].append(f"Deutsche Qualität kritisch: {de_score}")
                
                # Englische Bewertung
                en_eval = quality_data.get("english_evaluation", {})
                if en_eval:
                    en_score = en_eval.get("overall_score", 0)
                    section["details"]["english_score"] = en_score
                    section["details"]["english_level"] = en_eval.get("quality_level", "Unknown")
                    
                    if en_score < 0.5:
                        section["warnings"].append(f"Englische Qualität kritisch: {en_score}")
                
                # Gesamtbewertung
                if "german_score" in section["details"] and "english_score" in section["details"]:
                    overall_score = (de_score + en_score) / 2
                    section["details"]["overall_score"] = overall_score
                    
                    if overall_score < 0.7:
                        section["warnings"].append(f"Gesamtqualität unter Schwellenwert: {overall_score}")
                
                # Review-Flags prüfen
                review_required = de_eval.get("review_required", False) or en_eval.get("review_required", False)
                if review_required:
                    section["details"]["review_required"] = True
                    section["warnings"].append("Manuelle Review erforderlich")
                
            else:
                section["errors"].append("Metadaten-Datei für Qualitätsbewertung nicht gefunden")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Quality-Evaluation-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["quality_evaluation"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_testing_ci(self):
        """G. Testing & CI Audit"""
        print("\n📋 G. Testing & CI")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # Smoke-Test prüfen
            smoke_test_file = project_root / "tests" / "smoke_test.py"
            if smoke_test_file.exists():
                section["details"]["smoke_test_file"] = "present"
                
                # Smoke-Test ausführen
                import subprocess
                result = subprocess.run([sys.executable, str(smoke_test_file)], 
                                      capture_output=True, text=True, cwd=project_root)
                
                if result.returncode == 0:
                    section["details"]["smoke_test"] = "passed"
                else:
                    section["errors"].append(f"Smoke-Test fehlgeschlagen: {result.stderr}")
            else:
                section["errors"].append("Smoke-Test-Datei nicht gefunden")
            
            # GitHub Actions prüfen
            github_workflow = project_root / ".github" / "workflows" / "ci.yml"
            if github_workflow.exists():
                section["details"]["github_actions"] = "present"
            else:
                section["warnings"].append("GitHub Actions Workflow nicht gefunden")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"Testing-CI-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["testing_ci"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def audit_ui_integration(self):
        """H. UI / Integration Audit"""
        print("\n📋 H. UI / Integration")
        section = {"status": "unknown", "details": {}, "errors": [], "warnings": []}
        
        try:
            # GUI-Dateien prüfen
            gui_files = [
                "simple_gui.py",
                "gui_enhanced.py"
            ]
            
            for gui_file in gui_files:
                file_path = project_root / gui_file
                if file_path.exists():
                    section["details"][gui_file] = "present"
                else:
                    section["warnings"].append(f"{gui_file} nicht gefunden")
            
            # GUI-Import-Test
            try:
                import tkinter
                section["details"]["tkinter"] = "available"
            except ImportError:
                section["warnings"].append("tkinter nicht verfügbar")
            
            # Status bestimmen
            if section["errors"]:
                section["status"] = "failed"
            elif section["warnings"]:
                section["status"] = "partial"
            else:
                section["status"] = "passed"
                
        except Exception as e:
            section["status"] = "failed"
            section["errors"].append(f"UI-Integration-Audit-Fehler: {e}")
        
        self.audit_results["sections"]["ui_integration"] = section
        print(f"   Status: {section['status'].upper()}")
    
    def create_summary(self):
        """Erstellt die Audit-Zusammenfassung"""
        print("\n📊 Audit-Zusammenfassung")
        print("=" * 60)
        
        # Statistiken berechnen
        total_sections = len(self.audit_results["sections"])
        passed_sections = sum(1 for section in self.audit_results["sections"].values() 
                            if section["status"] == "passed")
        failed_sections = sum(1 for section in self.audit_results["sections"].values() 
                            if section["status"] == "failed")
        partial_sections = sum(1 for section in self.audit_results["sections"].values() 
                             if section["status"] == "partial")
        
        # Alle Fehler und Warnungen sammeln
        all_errors = []
        all_warnings = []
        all_fallbacks = []
        
        for section_name, section_data in self.audit_results["sections"].items():
            all_errors.extend([f"{section_name}: {error}" for error in section_data.get("errors", [])])
            all_warnings.extend([f"{section_name}: {warning}" for warning in section_data.get("warnings", [])])
            all_fallbacks.extend(section_data.get("fallbacks_applied", []))
        
        # Zusammenfassung erstellen
        summary = {
            "total_sections": total_sections,
            "passed_sections": passed_sections,
            "failed_sections": failed_sections,
            "partial_sections": partial_sections,
            "success_rate": (passed_sections / total_sections) * 100 if total_sections > 0 else 0,
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "total_fallbacks": len(all_fallbacks),
            "overall_status": "passed" if failed_sections == 0 else "failed"
        }
        
        self.audit_results["summary"] = summary
        self.audit_results["errors"] = all_errors
        self.audit_results["warnings"] = all_warnings
        self.audit_results["fallbacks_applied"] = all_fallbacks
        
        # Ausgabe
        print(f"✅ Bestanden: {passed_sections}/{total_sections} Sektionen")
        print(f"⚠️  Teilweise: {partial_sections}/{total_sections} Sektionen")
        print(f"❌ Fehlgeschlagen: {failed_sections}/{total_sections} Sektionen")
        print(f"📈 Erfolgsrate: {summary['success_rate']:.1f}%")
        print(f"🚨 Fehler: {len(all_errors)}")
        print(f"⚠️  Warnungen: {len(all_warnings)}")
        print(f"🔄 Fallbacks: {len(all_fallbacks)}")
        
        if all_errors:
            print("\n🚨 Top 5 Fehler:")
            for i, error in enumerate(all_errors[:5], 1):
                print(f"   {i}. {error}")
        
        if all_warnings:
            print("\n⚠️  Top 5 Warnungen:")
            for i, warning in enumerate(all_warnings[:5], 1):
                print(f"   {i}. {warning}")

def main():
    """Hauptfunktion für das Audit"""
    auditor = PipelineAuditor()
    results = auditor.run_full_audit()
    
    # Ergebnisse speichern
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    
    # JSON-Report
    json_file = output_dir / "audit_report.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Markdown-Report
    md_file = output_dir / "audit_report.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# One Click Book Writer - Pipeline Audit Report\n\n")
        f.write(f"**Datum:** {results['timestamp']}\n")
        f.write(f"**Audit-Version:** {results['audit_version']}\n\n")
        
        f.write("## Zusammenfassung\n\n")
        summary = results['summary']
        f.write(f"- **Gesamtstatus:** {summary['overall_status'].upper()}\n")
        f.write(f"- **Erfolgsrate:** {summary['success_rate']:.1f}%\n")
        f.write(f"- **Bestanden:** {summary['passed_sections']}/{summary['total_sections']}\n")
        f.write(f"- **Fehler:** {summary['total_errors']}\n")
        f.write(f"- **Warnungen:** {summary['total_warnings']}\n\n")
        
        f.write("## Detaillierte Ergebnisse\n\n")
        for section_name, section_data in results['sections'].items():
            f.write(f"### {section_name.upper()}\n")
            f.write(f"- **Status:** {section_data['status'].upper()}\n")
            if section_data.get('errors'):
                f.write("- **Fehler:**\n")
                for error in section_data['errors']:
                    f.write(f"  - {error}\n")
            if section_data.get('warnings'):
                f.write("- **Warnungen:**\n")
                for warning in section_data['warnings']:
                    f.write(f"  - {warning}\n")
            f.write("\n")
    
    print(f"\n📄 Audit-Reports gespeichert:")
    print(f"   JSON: {json_file}")
    print(f"   Markdown: {md_file}")
    
    return results

if __name__ == "__main__":
    main() 