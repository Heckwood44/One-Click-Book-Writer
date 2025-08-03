#!/usr/bin/env python3
"""
Prompt Optimizer
Erweiterte Prompt-Optimierung mit Claude A/B-Optimierung, Diffing und Ensembles
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import difflib
import re

from core.architecture import (
    ComponentInterface, ComponentType, PromptTemplate, 
    OptimizationResult, register_component
)
from engine.claude_adapter import ClaudeAdapter
from engine.openai_adapter import OpenAIAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptOptimizer(ComponentInterface):
    """Erweiterter Prompt-Optimizer mit Claude A/B-Optimierung"""
    
    def __init__(self):
        super().__init__(ComponentType.OPTIMIZER, version="2.0.0")
        self.claude_client = ClaudeAdapter()
        self.openai_client = OpenAIAdapter()
        self.optimization_history = []
        
    def optimize_prompt_with_claude(self, 
                                  template: PromptTemplate,
                                  prompt_frame: Dict,
                                  optimization_focus: Optional[str] = None) -> OptimizationResult:
        """Optimiert Prompt mit Claude A/B-Optimierung"""
        try:
            # Generiere Roh-Prompt
            raw_prompt = self._generate_raw_prompt(template)
            raw_prompt_hash = hashlib.md5(raw_prompt.encode()).hexdigest()[:16]
            
            # Erstelle Optimierungs-Instruktion
            optimization_instruction = self._create_optimization_instruction(
                prompt_frame, optimization_focus
            )
            
            # Sende an Claude zur Optimierung
            optimization_request = f"""
OPTIMIERE DIESEN PROMPT:

{raw_prompt}

OPTIMIERUNGS-INSTRUKTION:
{optimization_instruction}

WICHTIG:
- Markiere alle Änderungen mit [ÄNDERUNG: ...]
- Erkläre die Begründung für jede Änderung
- Behalte die grundlegende Struktur bei
- Fokussiere auf {optimization_focus or 'allgemeine Verbesserung'}

OPTIMIERTER PROMPT:
"""
            
            optimized_response = self.claude_client.generate_text(optimization_request)
            
            # Extrahiere optimierten Prompt
            optimized_prompt = self._extract_optimized_prompt(optimized_response)
            optimized_prompt_hash = hashlib.md5(optimized_prompt.encode()).hexdigest()[:16]
            
            # Generiere Prompt-Diff
            prompt_diff = self._generate_prompt_diff(raw_prompt, optimized_prompt)
            
            # Teste beide Prompts
            raw_result = self._test_prompt(raw_prompt, prompt_frame)
            optimized_result = self._test_prompt(optimized_prompt, prompt_frame)
            
            # Berechne Quality Score Delta
            quality_score_delta = optimized_result.get("quality_score", 0) - raw_result.get("quality_score", 0)
            
            # Erstelle Optimierungs-Ergebnis
            optimization_result = OptimizationResult(
                original_prompt_hash=raw_prompt_hash,
                optimized_prompt_hash=optimized_prompt_hash,
                quality_score_delta=quality_score_delta,
                prompt_diff=prompt_diff,
                optimization_focus=optimization_focus or "general",
                success=quality_score_delta > 0,
                metadata={
                    "raw_result": raw_result,
                    "optimized_result": optimized_result,
                    "optimization_timestamp": datetime.now().isoformat(),
                    "claude_response": optimized_response
                }
            )
            
            # Speichere in Historie
            self.optimization_history.append(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Fehler bei Claude-Optimierung: {e}")
            return OptimizationResult(
                original_prompt_hash="",
                optimized_prompt_hash="",
                quality_score_delta=0.0,
                prompt_diff={},
                optimization_focus=optimization_focus or "general",
                success=False,
                metadata={"error": str(e)}
            )
    
    def _generate_raw_prompt(self, template: PromptTemplate) -> str:
        """Generiert Roh-Prompt aus Template"""
        prompt_parts = []
        
        for layer in template.layers:
            prompt_parts.append(f"=== {layer.layer_type.value.upper()} ===")
            prompt_parts.append(layer.content)
            prompt_parts.append("---")
        
        return "\n".join(prompt_parts)
    
    def _create_optimization_instruction(self, prompt_frame: Dict, optimization_focus: Optional[str]) -> str:
        """Erstellt Optimierungs-Instruktion"""
        age_group = prompt_frame.get("age_group", "")
        genre = prompt_frame.get("genre", "")
        emotion = prompt_frame.get("emotion", "")
        
        base_instruction = f"""
Zielgruppe: {age_group}
Genre: {genre}
Emotion: {emotion}

OPTIMIERUNGS-ZIELE:
- Erhöhe emotionale Tiefe und Authentizität
- Verbessere Genre-Compliance und Konventionen
- Optimiere Lesbarkeit für die Zielgruppe
- Stärke bildhafte Sprache und Engagement
- Balanciere Komplexität und Zugänglichkeit
"""
        
        if optimization_focus:
            base_instruction += f"\nSPEZIFISCHER FOKUS: {optimization_focus}"
        
        return base_instruction
    
    def _extract_optimized_prompt(self, claude_response: str) -> str:
        """Extrahiert optimierten Prompt aus Claude-Antwort"""
        # Suche nach dem optimierten Prompt nach "OPTIMIERTER PROMPT:"
        if "OPTIMIERTER PROMPT:" in claude_response:
            parts = claude_response.split("OPTIMIERTER PROMPT:")
            if len(parts) > 1:
                return parts[1].strip()
        
        # Fallback: Verwende gesamte Antwort
        return claude_response.strip()
    
    def _generate_prompt_diff(self, raw_prompt: str, optimized_prompt: str) -> Dict[str, Any]:
        """Generiert detaillierten Prompt-Diff"""
        # Zeilenweise Diff
        raw_lines = raw_prompt.splitlines()
        optimized_lines = optimized_prompt.splitlines()
        
        diff_lines = list(difflib.unified_diff(
            raw_lines, optimized_lines,
            fromfile="Raw Prompt",
            tofile="Optimized Prompt",
            lineterm=""
        ))
        
        # Wortweise Änderungen
        word_changes = self._analyze_word_changes(raw_prompt, optimized_prompt)
        
        # Strukturelle Änderungen
        structural_changes = self._analyze_structural_changes(raw_prompt, optimized_prompt)
        
        return {
            "diff_lines": diff_lines,
            "word_changes": word_changes,
            "structural_changes": structural_changes,
            "similarity": difflib.SequenceMatcher(None, raw_prompt, optimized_prompt).ratio(),
            "change_percentage": self._calculate_change_percentage(raw_prompt, optimized_prompt)
        }
    
    def _analyze_word_changes(self, raw_prompt: str, optimized_prompt: str) -> Dict[str, Any]:
        """Analysiert wortweise Änderungen"""
        raw_words = set(re.findall(r'\b\w+\b', raw_prompt.lower()))
        optimized_words = set(re.findall(r'\b\w+\b', optimized_prompt.lower()))
        
        added_words = optimized_words - raw_words
        removed_words = raw_words - optimized_words
        common_words = raw_words & optimized_words
        
        return {
            "added_words": list(added_words)[:20],  # Limitiere auf 20
            "removed_words": list(removed_words)[:20],
            "common_words_count": len(common_words),
            "vocabulary_expansion": len(added_words)
        }
    
    def _analyze_structural_changes(self, raw_prompt: str, optimized_prompt: str) -> Dict[str, Any]:
        """Analysiert strukturelle Änderungen"""
        raw_sections = len(re.findall(r'===', raw_prompt))
        optimized_sections = len(re.findall(r'===', optimized_prompt))
        
        raw_length = len(raw_prompt)
        optimized_length = len(optimized_prompt)
        
        return {
            "section_count_change": optimized_sections - raw_sections,
            "length_change": optimized_length - raw_length,
            "length_change_percentage": ((optimized_length - raw_length) / max(raw_length, 1)) * 100
        }
    
    def _calculate_change_percentage(self, raw_prompt: str, optimized_prompt: str) -> float:
        """Berechnet Änderungs-Prozentsatz"""
        matcher = difflib.SequenceMatcher(None, raw_prompt, optimized_prompt)
        return (1 - matcher.ratio()) * 100
    
    def _test_prompt(self, prompt: str, prompt_frame: Dict) -> Dict[str, Any]:
        """Testet Prompt mit einfacher Evaluation"""
        try:
            # Generiere Test-Text
            response = self.openai_client.generate_text(prompt)
            
            # Einfache Evaluation
            word_count = len(response.split())
            target_words = prompt_frame.get("target_words", 800)
            word_count_score = min(word_count / max(target_words, 1), 1.0)
            
            # Einfache Qualitäts-Metriken
            has_dialogue = '"' in response or '"' in response
            has_emotion = any(word in response.lower() for word in ["freude", "mut", "wunder", "freundschaft"])
            has_structure = len(response.split('\n\n')) >= 3
            
            quality_score = (word_count_score + has_dialogue + has_emotion + has_structure) / 4
            
            return {
                "quality_score": quality_score,
                "word_count": word_count,
                "word_count_score": word_count_score,
                "has_dialogue": has_dialogue,
                "has_emotion": has_emotion,
                "has_structure": has_structure,
                "response_preview": response[:200] + "..." if len(response) > 200 else response
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Prompt-Test: {e}")
            return {
                "quality_score": 0.0,
                "error": str(e)
            }
    
    def create_prompt_ensemble(self, 
                             base_template: PromptTemplate,
                             variations: int = 3,
                             variation_focus: List[str] = None) -> List[PromptTemplate]:
        """Erstellt Prompt-Ensemble mit Variationen"""
        if variation_focus is None:
            variation_focus = ["emotional_depth", "genre_compliance", "readability"]
        
        ensemble = [base_template]
        
        for i, focus in enumerate(variation_focus[:variations-1]):
            # Erstelle Variation basierend auf Fokus
            variation_template = self._create_template_variation(base_template, focus, i+1)
            ensemble.append(variation_template)
        
        return ensemble
    
    def _create_template_variation(self, 
                                 base_template: PromptTemplate, 
                                 focus: str, 
                                 variation_id: int) -> PromptTemplate:
        """Erstellt Template-Variation"""
        # Kopiere Template
        variation_layers = []
        for layer in base_template.layers:
            # Anpasse Layer basierend auf Fokus
            adjusted_content = self._adjust_layer_for_focus(layer, focus)
            
            variation_layers.append(type(layer)(
                layer_type=layer.layer_type,
                content=adjusted_content,
                weight=layer.weight,
                version=layer.version,
                metadata=layer.metadata
            ))
        
        return PromptTemplate(
            template_id=f"{base_template.template_id}_variation_{variation_id}",
            name=f"{base_template.name} - {focus.title()}",
            description=f"Variation von {base_template.name} mit Fokus auf {focus}",
            layers=variation_layers,
            version=f"{base_template.version}.{variation_id}",
            metadata={
                "base_template": base_template.template_id,
                "variation_focus": focus,
                "variation_id": variation_id
            }
        )
    
    def _adjust_layer_for_focus(self, layer, focus: str) -> str:
        """Passt Layer-Inhalt für spezifischen Fokus an"""
        content = layer.content
        
        if focus == "emotional_depth":
            # Verstärke emotionale Elemente
            content += "\n\nEMOTIONALE VERSTÄRKUNG:\n- Verwende mehr emotionale Schlüsselwörter\n- Baue emotionale Spannungsbögen auf\n- Schaffe tiefere Charakterverbindungen"
        
        elif focus == "genre_compliance":
            # Verstärke Genre-Elemente
            content += "\n\nGENRE-VERSTÄRKUNG:\n- Verwende mehr Genre-typische Tropes\n- Betone Genre-Konventionen\n- Stärke Genre-spezifische Stilrichtlinien"
        
        elif focus == "readability":
            # Verbessere Lesbarkeit
            content += "\n\nLESBARKEITS-VERBESSERUNG:\n- Verwende kürzere, klarere Sätze\n- Erhöhe Dialog-Anteil\n- Verbessere Struktur und Fluss"
        
        return content
    
    def rank_prompt_ensemble(self, 
                           ensemble: List[PromptTemplate],
                           prompt_frame: Dict) -> List[Tuple[PromptTemplate, float]]:
        """Ranked Prompt-Ensemble basierend auf Performance"""
        rankings = []
        
        for template in ensemble:
            # Teste Template
            prompt = self._generate_raw_prompt(template)
            test_result = self._test_prompt(prompt, prompt_frame)
            
            rankings.append((template, test_result.get("quality_score", 0)))
        
        # Sortiere nach Score (höchste zuerst)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
    
    def create_hybrid_prompt(self, 
                           top_templates: List[Tuple[PromptTemplate, float]],
                           max_templates: int = 2) -> PromptTemplate:
        """Erstellt hybriden Prompt aus Top-Templates"""
        if not top_templates:
            raise ValueError("Keine Templates für Hybrid-Erstellung")
        
        # Wähle Top-Templates
        selected_templates = top_templates[:max_templates]
        templates = [t[0] for t in selected_templates]
        scores = [t[1] for t in selected_templates]
        
        # Normalisiere Scores als Gewichte
        total_score = sum(scores)
        weights = [score / total_score for score in scores]
        
        # Erstelle hybriden Template
        hybrid_layers = []
        layer_types = set()
        
        for template, weight in zip(templates, weights):
            for layer in template.layers:
                if layer.layer_type not in layer_types:
                    # Erste Instanz dieses Layer-Typs
                    hybrid_layers.append(type(layer)(
                        layer_type=layer.layer_type,
                        content=layer.content,
                        weight=layer.weight * weight,
                        version=layer.version,
                        metadata=layer.metadata
                    ))
                    layer_types.add(layer.layer_type)
                else:
                    # Layer-Typ bereits vorhanden, gewichte kombinieren
                    existing_layer = next(l for l in hybrid_layers if l.layer_type == layer.layer_type)
                    existing_layer.content += f"\n\n--- HYBRID GEWICHTET {weight:.2f} ---\n{layer.content}"
                    existing_layer.weight = (existing_layer.weight + layer.weight * weight) / 2
        
        return PromptTemplate(
            template_id=f"hybrid_{hashlib.md5(str(templates).encode()).hexdigest()[:8]}",
            name=f"Hybrid Template ({len(templates)} Templates)",
            description=f"Hybride Kombination der besten {len(templates)} Templates",
            layers=hybrid_layers,
            version="2.0.0",
            metadata={
                "hybrid_templates": [t.template_id for t in templates],
                "weights": weights,
                "hybrid_timestamp": datetime.now().isoformat()
            }
        )
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Gibt Optimierungs-Historie zurück"""
        return self.optimization_history
    
    def get_best_optimizations(self, min_improvement: float = 0.1) -> List[OptimizationResult]:
        """Gibt beste Optimierungen zurück"""
        return [
            opt for opt in self.optimization_history 
            if opt.quality_score_delta >= min_improvement and opt.success
        ]

# Registrierte Version des Prompt-Optimizers
class PromptOptimizerComponent(PromptOptimizer):
    """Registrierte Version des Prompt-Optimizers"""
    def __init__(self):
        super().__init__() 