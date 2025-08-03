#!/usr/bin/env python3
"""
Prompt Calibration System
Claude A/B-Optimierung mit strukturierter Diff-Analyse und Template-Versionierung
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import difflib
import re

import sys
sys.path.append(str(Path(__file__).parent.parent))

from compiler.modular_prompt_templates import PromptTemplateManager, ModularPromptTemplate
from engine.claude_adapter import ClaudeAdapter
from engine.openai_adapter import OpenAIAdapter
from utils.quality_evaluator import QualityEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptCalibrationSystem:
    """System für Prompt-Calibration mit Claude A/B-Optimierung"""
    
    def __init__(self):
        self.claude_client = ClaudeAdapter()
        self.openai_client = OpenAIAdapter()
        self.quality_evaluator = QualityEvaluator()
        self.template_manager = PromptTemplateManager()
    
    def calibrate_prompt_template(self, 
                                 template_id: str,
                                 optimization_focus: str = "emotional_depth",
                                 target_metrics: Optional[Dict] = None) -> Dict:
        """
        Kalibriert Prompt-Template mit Claude-Optimierung
        
        Args:
            template_id: ID des zu optimierenden Templates
            optimization_focus: Fokus der Optimierung (emotional_depth, clarity, etc.)
            target_metrics: Ziel-Metriken für Optimierung
        """
        logger.info(f"Starte Prompt-Calibration für Template: {template_id}")
        
        try:
            # Lade Template
            template = self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} nicht gefunden")
            
            # Schritt 1: Rohen Prompt kompilieren
            raw_prompt = template.compile_prompt("de")
            raw_metrics = self._evaluate_prompt_performance(raw_prompt, "de")
            
            # Schritt 2: Claude-Optimierung
            optimized_prompt = self._optimize_prompt_with_claude(
                raw_prompt, template, optimization_focus
            )
            optimized_metrics = self._evaluate_prompt_performance(optimized_prompt, "de")
            
            # Schritt 3: Diff-Analyse
            prompt_diff = self._analyze_prompt_diff(raw_prompt, optimized_prompt)
            
            # Schritt 4: Template-Mutation erstellen
            mutated_template = self._create_mutated_template(
                template, optimized_prompt, prompt_diff
            )
            
            # Schritt 5: Performance-Vergleich
            performance_comparison = self._compare_performance(
                raw_metrics, optimized_metrics, target_metrics
            )
            
            # Schritt 6: Ergebnisse zusammenfassen
            results = {
                "calibration_timestamp": datetime.now().isoformat(),
                "template_id": template_id,
                "optimization_focus": optimization_focus,
                "raw_template_hash": template.template_hash,
                "mutated_template_hash": mutated_template.template_hash,
                "performance_comparison": performance_comparison,
                "prompt_diff": prompt_diff,
                "optimization_success": performance_comparison["overall_improvement"] > 0,
                "recommendations": self._generate_calibration_recommendations(performance_comparison)
            }
            
            # Schritt 7: Mutiertes Template speichern
            self.template_manager.templates[f"{template_id}_mutated"] = mutated_template
            self.template_manager.save_templates()
            
            logger.info(f"Prompt-Calibration abgeschlossen für Template: {template_id}")
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei Prompt-Calibration: {e}")
            return {"error": str(e)}
    
    def _optimize_prompt_with_claude(self, 
                                   raw_prompt: str, 
                                   template: ModularPromptTemplate,
                                   optimization_focus: str) -> str:
        """Optimiert Prompt mit Claude basierend auf Fokus"""
        
        optimization_instructions = {
            "emotional_depth": """
OPTIMIERUNGS-AUFTRAG: EMOTIONALE TIEFE VERSTÄRKEN

Verbessere diesen Prompt für ein Kinderbuch, um die emotionale Tiefe zu verstärken:

{raw_prompt}

ZIELE:
1. Erhöhe emotionale Verbindung zu jungen Lesern
2. Verstärke bildhafte Sprache und Metaphern
3. Füge spezifische Anweisungen für emotionale Entwicklung hinzu
4. Behalte alle Zielvorgaben bei (Wortanzahl, Charaktere, Handlung)
5. Stelle sicher, dass beide Sprachversionen gleichwertig optimiert werden

WICHTIG:
- Gib NUR den optimierten Prompt zurück
- Markiere Änderungen mit [+EMOTIONAL] Kommentaren
- Behalte die System Note Signatur bei
- Fokussiere auf emotionale Tiefe ohne andere Aspekte zu vernachlässigen

OPTIMIERTER PROMPT:
""",
            "clarity": """
OPTIMIERUNGS-AUFTRAG: KLARHEIT UND STRUKTUR VERBESSERN

Verbessere diesen Prompt für ein Kinderbuch, um Klarheit und Struktur zu optimieren:

{raw_prompt}

ZIELE:
1. Verbessere Klarheit der Anweisungen
2. Strukturiere den Prompt logischer
3. Mache Anweisungen spezifischer und handlungsorientierter
4. Behalte alle Zielvorgaben bei
5. Stelle sicher, dass beide Sprachversionen gleichwertig optimiert werden

WICHTIG:
- Gib NUR den optimierten Prompt zurück
- Markiere Änderungen mit [+CLARITY] Kommentaren
- Behalte die System Note Signatur bei
- Fokussiere auf Klarheit ohne andere Aspekte zu vernachlässigen

OPTIMIERTER PROMPT:
""",
            "child_friendliness": """
OPTIMIERUNGS-AUFTRAG: KINDERFREUNDLICHKEIT VERSTÄRKEN

Verbessere diesen Prompt für ein Kinderbuch, um die Kinderfreundlichkeit zu optimieren:

{raw_prompt}

ZIELE:
1. Verstärke altersgerechte Sprache (6 Jahre)
2. Füge mehr spielerische Elemente hinzu
3. Betone positive, ermutigende Botschaften
4. Behalte alle Zielvorgaben bei
5. Stelle sicher, dass beide Sprachversionen gleichwertig optimiert werden

WICHTIG:
- Gib NUR den optimierten Prompt zurück
- Markiere Änderungen mit [+CHILD_FRIENDLY] Kommentaren
- Behalte die System Note Signatur bei
- Fokussiere auf Kinderfreundlichkeit ohne andere Aspekte zu vernachlässigen

OPTIMIERTER PROMPT:
"""
        }
        
        instruction = optimization_instructions.get(
            optimization_focus, 
            optimization_instructions["emotional_depth"]
        ).format(raw_prompt=raw_prompt)
        
        logger.info(f"Optimiere Prompt mit Claude (Fokus: {optimization_focus})")
        optimized_prompt = self.claude_client.generate_text(instruction)
        
        # Bereinige Claude-Antwort
        if "OPTIMIERTER PROMPT:" in optimized_prompt:
            optimized_prompt = optimized_prompt.split("OPTIMIERTER PROMPT:")[1].strip()
        
        return optimized_prompt
    
    def _evaluate_prompt_performance(self, prompt: str, language: str) -> Dict:
        """Evaluiert Performance eines Prompts"""
        try:
            # Generiere Test-Kapitel
            response = self.openai_client.generate_text(prompt)
            
            # Parse Antwort (vereinfacht)
            test_text = response[:1000] if len(response) > 1000 else response
            
            # Qualitäts-Evaluation
            quality_metrics = self.quality_evaluator.calculate_overall_quality_score(
                text=test_text,
                target_words=800,
                target_emotion="wonder",
                target_audience="children",
                language=language
            )
            
            return {
                "prompt_length": len(prompt),
                "response_length": len(response),
                "quality_score": quality_metrics.get("overall_score", 0),
                "quality_level": quality_metrics.get("quality_level", "Unknown"),
                "individual_scores": quality_metrics.get("individual_scores", {}),
                "flags": quality_metrics.get("flags", [])
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Prompt-Performance-Evaluation: {e}")
            return {
                "prompt_length": len(prompt),
                "response_length": 0,
                "quality_score": 0,
                "quality_level": "Error",
                "individual_scores": {},
                "flags": ["EVALUATION_ERROR"]
            }
    
    def _analyze_prompt_diff(self, raw_prompt: str, optimized_prompt: str) -> Dict:
        """Analysiert Diff zwischen rohem und optimiertem Prompt"""
        try:
            raw_lines = raw_prompt.split('\n')
            opt_lines = optimized_prompt.split('\n')
            
            # Zeilenweise Diff
            diff_lines = list(difflib.unified_diff(
                raw_lines, opt_lines,
                fromfile='raw_prompt',
                tofile='optimized_prompt',
                lineterm=''
            ))
            
            # Strukturelle Analyse
            changes = {
                "added_lines": [],
                "removed_lines": [],
                "modified_lines": [],
                "total_changes": 0,
                "layer_changes": {},
                "semantic_changes": []
            }
            
            # Analysiere Diff-Lines
            for line in diff_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    changes["added_lines"].append(line[1:])
                    changes["total_changes"] += 1
                elif line.startswith('-') and not line.startswith('---'):
                    changes["removed_lines"].append(line[1:])
                    changes["total_changes"] += 1
            
            # Layer-spezifische Änderungen
            changes["layer_changes"] = self._analyze_layer_changes(raw_lines, opt_lines)
            
            # Semantische Änderungen
            changes["semantic_changes"] = self._analyze_semantic_changes(raw_prompt, optimized_prompt)
            
            return {
                "diff_lines": diff_lines,
                "changes": changes,
                "raw_length": len(raw_prompt),
                "optimized_length": len(optimized_prompt),
                "length_change": len(optimized_prompt) - len(raw_prompt),
                "change_ratio": len(optimized_prompt) / max(len(raw_prompt), 1)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Prompt-Diff-Analyse: {e}")
            return {}
    
    def _analyze_layer_changes(self, raw_lines: List[str], opt_lines: List[str]) -> Dict:
        """Analysiert Änderungen nach Prompt-Layern"""
        layer_changes = {}
        
        # Definiere Layer-Marker
        layer_markers = {
            "system_note": "SYSTEM NOTE SIGNATURE",
            "context": "CONTEXT",
            "style": "STYLE GUIDELINES",
            "emotion": "EMOTIONAL LAYER",
            "instructions": "SPECIFIC INSTRUCTIONS",
            "constraints": "CONSTRAINTS"
        }
        
        for layer_name, marker in layer_markers.items():
            raw_layer_content = self._extract_layer_content(raw_lines, marker)
            opt_layer_content = self._extract_layer_content(opt_lines, marker)
            
            if raw_layer_content != opt_layer_content:
                layer_changes[layer_name] = {
                    "changed": True,
                    "raw_content": raw_layer_content,
                    "optimized_content": opt_layer_content,
                    "change_type": "modified"
                }
            else:
                layer_changes[layer_name] = {
                    "changed": False,
                    "change_type": "unchanged"
                }
        
        return layer_changes
    
    def _extract_layer_content(self, lines: List[str], marker: str) -> str:
        """Extrahiert Layer-Inhalt basierend auf Marker"""
        content = []
        in_layer = False
        
        for line in lines:
            if marker in line:
                in_layer = True
                continue
            elif in_layer and line.strip() == "---":
                break
            elif in_layer:
                content.append(line)
        
        return "\n".join(content).strip()
    
    def _analyze_semantic_changes(self, raw_prompt: str, optimized_prompt: str) -> List[str]:
        """Analysiert semantische Änderungen"""
        semantic_changes = []
        
        # Einfache Schlüsselwort-Analyse
        keywords = {
            "emotional": ["emotion", "gefühle", "herz", "warm", "liebevoll"],
            "clarity": ["klar", "einfach", "verständlich", "strukturiert"],
            "child_friendly": ["kind", "spielerisch", "freundlich", "positiv"],
            "descriptive": ["beschreibung", "bildhaft", "metaphor", "detail"]
        }
        
        for category, words in keywords.items():
            raw_count = sum(1 for word in words if word.lower() in raw_prompt.lower())
            opt_count = sum(1 for word in words if word.lower() in optimized_prompt.lower())
            
            if opt_count > raw_count:
                semantic_changes.append(f"+{category}: {opt_count - raw_count} mehr Erwähnungen")
            elif raw_count > opt_count:
                semantic_changes.append(f"-{category}: {raw_count - opt_count} weniger Erwähnungen")
        
        return semantic_changes
    
    def _create_mutated_template(self, 
                                original_template: ModularPromptTemplate,
                                optimized_prompt: str,
                                prompt_diff: Dict) -> ModularPromptTemplate:
        """Erstellt mutiertes Template basierend auf optimiertem Prompt"""
        
        # Erstelle neues Template
        mutated_id = f"{original_template.template_id}_mutated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        mutated_template = ModularPromptTemplate(mutated_id, f"Mutiertes {original_template.name}")
        
        # Kopiere Layer von Original-Template
        for layer_type, layer in original_template.layers.items():
            mutated_template.add_layer(layer)
        
        # Aktualisiere Layer basierend auf Diff-Analyse
        layer_changes = prompt_diff.get("changes", {}).get("layer_changes", {})
        
        for layer_name, change_info in layer_changes.items():
            if change_info.get("changed", False):
                optimized_content = change_info.get("optimized_content", "")
                if optimized_content:
                    # Erhöhe Gewicht für veränderte Layer
                    current_weight = original_template.get_layer(layer_name).weight
                    new_weight = min(current_weight * 1.2, 2.0)  # Max 2.0
                    
                    mutated_template.update_layer(
                        layer_name, 
                        optimized_content, 
                        new_weight
                    )
        
        return mutated_template
    
    def _compare_performance(self, 
                           raw_metrics: Dict, 
                           optimized_metrics: Dict,
                           target_metrics: Optional[Dict]) -> Dict:
        """Vergleicht Performance zwischen rohem und optimiertem Prompt"""
        
        comparison = {
            "raw_metrics": raw_metrics,
            "optimized_metrics": optimized_metrics,
            "improvements": {},
            "overall_improvement": 0,
            "target_achievement": {}
        }
        
        # Berechne Verbesserungen
        quality_delta = optimized_metrics.get("quality_score", 0) - raw_metrics.get("quality_score", 0)
        length_delta = optimized_metrics.get("response_length", 0) - raw_metrics.get("response_length", 0)
        
        comparison["improvements"] = {
            "quality_score_delta": quality_delta,
            "quality_score_percentage": (quality_delta / max(raw_metrics.get("quality_score", 1), 1)) * 100,
            "response_length_delta": length_delta,
            "prompt_length_delta": optimized_metrics.get("prompt_length", 0) - raw_metrics.get("prompt_length", 0)
        }
        
        comparison["overall_improvement"] = quality_delta
        
        # Prüfe Ziel-Metriken
        if target_metrics:
            for metric, target_value in target_metrics.items():
                current_value = optimized_metrics.get(metric, 0)
                achievement = (current_value / max(target_value, 1)) * 100
                comparison["target_achievement"][metric] = {
                    "current": current_value,
                    "target": target_value,
                    "achievement_percentage": achievement,
                    "achieved": current_value >= target_value
                }
        
        return comparison
    
    def _generate_calibration_recommendations(self, performance_comparison: Dict) -> List[str]:
        """Generiert Empfehlungen basierend auf Performance-Vergleich"""
        recommendations = []
        
        improvement = performance_comparison.get("overall_improvement", 0)
        
        if improvement > 0.1:
            recommendations.append("Mutiertes Template für Produktion übernehmen")
        elif improvement > 0.05:
            recommendations.append("Mutiertes Template weiter testen")
        else:
            recommendations.append("Optimierungsstrategie überarbeiten")
        
        # Spezifische Empfehlungen basierend auf Metriken
        improvements = performance_comparison.get("improvements", {})
        
        if improvements.get("quality_score_percentage", 0) > 20:
            recommendations.append("Optimierung erfolgreich - Qualitätsverbesserung signifikant")
        
        if improvements.get("response_length_delta", 0) < -100:
            recommendations.append("Antwortlänge reduzieren - zu ausführlich")
        
        return recommendations

def main():
    """Beispiel für Prompt-Calibration"""
    calibration_system = PromptCalibrationSystem()
    
    # Erstelle Standard-Template falls nicht vorhanden
    if not calibration_system.template_manager.get_template("children_book_v1"):
        calibration_system.template_manager.create_default_children_book_template()
        calibration_system.template_manager.save_templates()
    
    # Führe Calibration durch
    results = calibration_system.calibrate_prompt_template(
        template_id="children_book_v1",
        optimization_focus="emotional_depth",
        target_metrics={"quality_score": 0.8}
    )
    
    if "error" not in results:
        print("\n" + "="*60)
        print("PROMPT-CALIBRATION ERGEBNISSE")
        print("="*60)
        print(f"Template ID: {results['template_id']}")
        print(f"Optimization Focus: {results['optimization_focus']}")
        print(f"Raw Template Hash: {results['raw_template_hash']}")
        print(f"Mutated Template Hash: {results['mutated_template_hash']}")
        print(f"Overall Improvement: {results['performance_comparison']['overall_improvement']:.3f}")
        print(f"Optimization Success: {'✅ JA' if results['optimization_success'] else '❌ NEIN'}")
        
        print("\nEmpfehlungen:")
        for rec in results['recommendations']:
            print(f"• {rec}")
        
        print("="*60)
    else:
        print(f"Fehler bei Prompt-Calibration: {results['error']}")

if __name__ == "__main__":
    main() 