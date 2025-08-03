#!/usr/bin/env python3
"""
Modular Prompt Template System
Strukturierte, versionierte Prompt-Layer mit Gewichten und adaptiver Optimierung
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptLayer:
    """Einzelner Prompt-Layer mit Versionierung und Gewichtung"""
    
    def __init__(self, 
                 layer_type: str,
                 content: str,
                 version: str = "1.0.0",
                 weight: float = 1.0,
                 metadata: Optional[Dict] = None):
        self.layer_type = layer_type
        self.content = content
        self.version = version
        self.weight = weight
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.layer_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generiert Hash für Layer-Versionierung"""
        content_str = f"{self.layer_type}:{self.content}:{self.version}:{self.weight}"
        return hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        """Konvertiert Layer zu Dictionary"""
        return {
            "layer_type": self.layer_type,
            "content": self.content,
            "version": self.version,
            "weight": self.weight,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "layer_hash": self.layer_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PromptLayer':
        """Erstellt Layer aus Dictionary"""
        return cls(
            layer_type=data["layer_type"],
            content=data["content"],
            version=data.get("version", "1.0.0"),
            weight=data.get("weight", 1.0),
            metadata=data.get("metadata", {})
        )

class ModularPromptTemplate:
    """Modulares Prompt-Template mit mehreren Layern"""
    
    def __init__(self, template_id: str, name: str = ""):
        self.template_id = template_id
        self.name = name or template_id
        self.layers: Dict[str, PromptLayer] = {}
        self.version = "1.0.0"
        self.created_at = datetime.now().isoformat()
        self.template_hash = ""
        self.performance_metrics = {}
    
    def add_layer(self, layer: PromptLayer) -> None:
        """Fügt Layer zum Template hinzu"""
        self.layers[layer.layer_type] = layer
        self._update_template_hash()
    
    def get_layer(self, layer_type: str) -> Optional[PromptLayer]:
        """Holt Layer nach Typ"""
        return self.layers.get(layer_type)
    
    def update_layer(self, layer_type: str, content: str, weight: float = 1.0) -> None:
        """Aktualisiert bestehenden Layer"""
        if layer_type in self.layers:
            old_layer = self.layers[layer_type]
            new_version = self._increment_version(old_layer.version)
            new_layer = PromptLayer(
                layer_type=layer_type,
                content=content,
                version=new_version,
                weight=weight,
                metadata=old_layer.metadata
            )
            self.layers[layer_type] = new_layer
            self._update_template_hash()
    
    def _increment_version(self, version: str) -> str:
        """Erhöht Versionsnummer"""
        parts = version.split('.')
        if len(parts) >= 3:
            parts[2] = str(int(parts[2]) + 1)
        return '.'.join(parts)
    
    def _update_template_hash(self) -> None:
        """Aktualisiert Template-Hash"""
        layer_data = []
        for layer_type in sorted(self.layers.keys()):
            layer = self.layers[layer_type]
            layer_data.append(f"{layer_type}:{layer.layer_hash}:{layer.weight}")
        
        content_str = f"{self.template_id}:{self.version}:" + "|".join(layer_data)
        self.template_hash = hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    def compile_prompt(self, language: str = "de") -> str:
        """Kompiliert vollständigen Prompt aus Layern"""
        prompt_parts = []
        
        # System Note Layer (immer zuerst)
        if "system_note" in self.layers:
            system_layer = self.layers["system_note"]
            prompt_parts.append(f"SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR")
            prompt_parts.append(system_layer.content)
            prompt_parts.append("---")
        
        # Context Layer
        if "context" in self.layers:
            context_layer = self.layers["context"]
            prompt_parts.append(f"CONTEXT ({language.upper()}):")
            prompt_parts.append(context_layer.content)
            prompt_parts.append("---")
        
        # Style Layer
        if "style" in self.layers:
            style_layer = self.layers["style"]
            prompt_parts.append(f"STYLE GUIDELINES ({language.upper()}):")
            prompt_parts.append(style_layer.content)
            prompt_parts.append("---")
        
        # Emotion Layer
        if "emotion" in self.layers:
            emotion_layer = self.layers["emotion"]
            prompt_parts.append(f"EMOTIONAL LAYER ({language.upper()}):")
            prompt_parts.append(emotion_layer.content)
            prompt_parts.append("---")
        
        # Instructions Layer
        if "instructions" in self.layers:
            instructions_layer = self.layers["instructions"]
            prompt_parts.append(f"SPECIFIC INSTRUCTIONS ({language.upper()}):")
            prompt_parts.append(instructions_layer.content)
            prompt_parts.append("---")
        
        # Constraints Layer
        if "constraints" in self.layers:
            constraints_layer = self.layers["constraints"]
            prompt_parts.append(f"CONSTRAINTS ({language.upper()}):")
            prompt_parts.append(constraints_layer.content)
            prompt_parts.append("---")
        
        return "\n".join(prompt_parts)
    
    def get_layer_weights(self) -> Dict[str, float]:
        """Gibt Layer-Gewichte zurück"""
        return {layer_type: layer.weight for layer_type, layer in self.layers.items()}
    
    def adjust_layer_weight(self, layer_type: str, new_weight: float) -> None:
        """Passt Layer-Gewicht an"""
        if layer_type in self.layers:
            self.layers[layer_type].weight = new_weight
            self._update_template_hash()
    
    def to_dict(self) -> Dict:
        """Konvertiert Template zu Dictionary"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at,
            "template_hash": self.template_hash,
            "layers": {layer_type: layer.to_dict() for layer_type, layer in self.layers.items()},
            "performance_metrics": self.performance_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModularPromptTemplate':
        """Erstellt Template aus Dictionary"""
        template = cls(data["template_id"], data.get("name", ""))
        template.version = data.get("version", "1.0.0")
        template.created_at = data.get("created_at", datetime.now().isoformat())
        template.template_hash = data.get("template_hash", "")
        template.performance_metrics = data.get("performance_metrics", {})
        
        for layer_type, layer_data in data.get("layers", {}).items():
            template.layers[layer_type] = PromptLayer.from_dict(layer_data)
        
        return template

class PromptTemplateManager:
    """Manager für modulare Prompt-Templates"""
    
    def __init__(self, templates_file: str = "prompt_templates.json"):
        self.templates_file = Path(templates_file)
        self.templates: Dict[str, ModularPromptTemplate] = {}
        self.load_templates()
    
    def load_templates(self) -> None:
        """Lädt Templates aus Datei"""
        if self.templates_file.exists():
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for template_id, template_data in data.items():
                        self.templates[template_id] = ModularPromptTemplate.from_dict(template_data)
                logger.info(f"Templates geladen: {len(self.templates)} Templates")
            except Exception as e:
                logger.error(f"Fehler beim Laden der Templates: {e}")
    
    def save_templates(self) -> None:
        """Speichert Templates in Datei"""
        try:
            data = {template_id: template.to_dict() for template_id, template in self.templates.items()}
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Templates gespeichert: {len(self.templates)} Templates")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Templates: {e}")
    
    def create_template(self, template_id: str, name: str = "") -> ModularPromptTemplate:
        """Erstellt neues Template"""
        template = ModularPromptTemplate(template_id, name)
        self.templates[template_id] = template
        return template
    
    def get_template(self, template_id: str) -> Optional[ModularPromptTemplate]:
        """Holt Template nach ID"""
        return self.templates.get(template_id)
    
    def update_template_performance(self, template_id: str, metrics: Dict) -> None:
        """Aktualisiert Performance-Metriken für Template"""
        if template_id in self.templates:
            self.templates[template_id].performance_metrics.update(metrics)
    
    def get_best_performing_template(self, metric: str = "quality_score") -> Optional[ModularPromptTemplate]:
        """Holt bestes Template basierend auf Metrik"""
        best_template = None
        best_score = -1
        
        for template in self.templates.values():
            score = template.performance_metrics.get(metric, 0)
            if score > best_score:
                best_score = score
                best_template = template
        
        return best_template
    
    def create_default_children_book_template(self) -> ModularPromptTemplate:
        """Erstellt Standard-Template für Kinderbücher"""
        template = self.create_template("children_book_v1", "Kinderbuch Standard Template")
        
        # System Note Layer
        system_layer = PromptLayer(
            layer_type="system_note",
            content="Du bist ein weltklasse Kinderbuchautor, der magische Geschichten für 6-jährige Kinder schreibt.",
            version="1.0.0",
            weight=1.0
        )
        template.add_layer(system_layer)
        
        # Context Layer
        context_layer = PromptLayer(
            layer_type="context",
            content="Geschichte für Kinder im Alter von 6 Jahren mit magischen Elementen und positiven Botschaften.",
            version="1.0.0",
            weight=1.0
        )
        template.add_layer(context_layer)
        
        # Style Layer
        style_layer = PromptLayer(
            layer_type="style",
            content="Warme, bildhafte Sprache. Kurze, klare Sätze. Dialoge zwischen Charakteren. Positive, ermutigende Töne.",
            version="1.0.0",
            weight=1.2
        )
        template.add_layer(style_layer)
        
        # Emotion Layer
        emotion_layer = PromptLayer(
            layer_type="emotion",
            content="Emotionale Tiefe: Wunder, Freude, Mut, Freundschaft. Emotionale Entwicklung der Charaktere zeigen.",
            version="1.0.0",
            weight=1.3
        )
        template.add_layer(emotion_layer)
        
        # Instructions Layer
        instructions_layer = PromptLayer(
            layer_type="instructions",
            content="Schreibe eine vollständige Geschichte mit Anfang, Mitte und Ende. Mindestens 800 Wörter. Bilinguale Ausgabe.",
            version="1.0.0",
            weight=1.0
        )
        template.add_layer(instructions_layer)
        
        # Constraints Layer
        constraints_layer = PromptLayer(
            layer_type="constraints",
            content="Keine Gewalt, keine beängstigenden Elemente. Altersgerechte Sprache. Positive Lösungen für Konflikte.",
            version="1.0.0",
            weight=1.1
        )
        template.add_layer(constraints_layer)
        
        return template

def main():
    """Beispiel für modulares Template-System"""
    manager = PromptTemplateManager()
    
    # Erstelle Standard-Template
    template = manager.create_default_children_book_template()
    
    # Kompiliere Prompt
    prompt = template.compile_prompt("de")
    
    print("\n" + "="*60)
    print("MODULARES PROMPT-TEMPLATE SYSTEM")
    print("="*60)
    print(f"Template ID: {template.template_id}")
    print(f"Template Hash: {template.template_hash}")
    print(f"Layer Count: {len(template.layers)}")
    print(f"Layer Weights: {template.get_layer_weights()}")
    
    print("\nKOMPILIERTER PROMPT:")
    print("-" * 40)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    
    # Speichere Template
    manager.save_templates()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main() 