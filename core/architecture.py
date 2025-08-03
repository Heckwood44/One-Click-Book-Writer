#!/usr/bin/env python3
"""
Core Architecture
Konsolidierte Architektur-Definition für das One Click Book Writer Framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import hashlib
from datetime import datetime

class ComponentType(Enum):
    """Komponenten-Typen"""
    PROMPT_FRAME = "prompt_frame"
    COMPILER = "compiler"
    ROUTER = "router"
    OPTIMIZER = "optimizer"
    GENERATOR = "generator"
    EVALUATOR = "evaluator"
    OUTPUT_HANDLER = "output_handler"
    FEEDBACK = "feedback"
    CI = "ci"

class LayerType(Enum):
    """Layer-Typen für Prompt-Compiler"""
    SYSTEM_NOTE = "system_note"
    TARGET_AUDIENCE = "target_audience"
    GENRE = "genre"
    EMOTION_DRAMA = "emotion_drama"
    STYLE = "style"
    CONTEXT = "context"
    CONSTRAINTS = "constraints"
    LANGUAGE = "language"
    CUSTOM = "custom"

@dataclass
class Layer:
    """Einzelner Layer für Prompt-Kompilierung"""
    layer_type: LayerType
    content: str
    weight: float = 1.0
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_hash(self) -> str:
        """Generiert Hash für Layer"""
        content_str = f"{self.layer_type.value}:{self.content}:{self.weight}:{self.version}"
        return hashlib.md5(content_str.encode()).hexdigest()[:16]

@dataclass
class PromptTemplate:
    """Prompt-Template mit Layern"""
    template_id: str
    name: str
    description: str
    layers: List[Layer]
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_hash(self) -> str:
        """Generiert Hash für Template"""
        layer_hashes = [layer.get_hash() for layer in self.layers]
        content_str = f"{self.template_id}:{self.version}:{':'.join(layer_hashes)}"
        return hashlib.md5(content_str.encode()).hexdigest()[:16]

@dataclass
class PromptFrame:
    """Strukturierte Eingabe für Prompt-Generierung"""
    age_group: str
    genre: str
    emotion: str
    language: str = "de"
    target_audience: str = "general"
    custom_context: Optional[Dict[str, Any]] = None
    template_overrides: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationRequest:
    """Generierungs-Anfrage"""
    prompt_frame: PromptFrame
    template: PromptTemplate
    optimization_enabled: bool = True
    ab_testing_enabled: bool = False
    feedback_collection: bool = True
    retry_on_failure: bool = True
    max_retries: int = 3

@dataclass
class GenerationResult:
    """Ergebnis der Text-Generierung"""
    success: bool
    german_text: str = ""
    english_text: str = ""
    prompt_hash: str = ""
    template_hash: str = ""
    generation_time: float = 0.0
    word_count: int = 0
    retry_count: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationResult:
    """Evaluations-Ergebnis"""
    overall_score: float
    readability_score: float
    age_appropriateness: float
    genre_compliance: float
    emotional_depth: float
    engagement_score: float
    flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evaluation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeedbackEntry:
    """Nutzer-Feedback-Eintrag"""
    chapter_number: int
    prompt_hash: str
    quality_score: float
    user_rating: int
    comment: str
    language: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class OptimizationResult:
    """Optimierungs-Ergebnis"""
    original_prompt_hash: str
    optimized_prompt_hash: str
    quality_score_delta: float
    prompt_diff: Dict[str, Any]
    optimization_focus: str
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ABTestResult:
    """A/B-Test-Ergebnis"""
    test_id: str
    segment: str
    original_result: GenerationResult
    optimized_result: GenerationResult
    comparison: Dict[str, Any]
    significant_improvement: bool
    recommendation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineResult:
    """Gesamtes Pipeline-Ergebnis"""
    run_id: str
    prompt_frame: PromptFrame
    generation_result: GenerationResult
    evaluation_result: EvaluationResult
    optimization_result: Optional[OptimizationResult] = None
    ab_test_result: Optional[ABTestResult] = None
    feedback_entries: List[FeedbackEntry] = field(default_factory=list)
    compliance_status: str = "pending"
    total_cost: float = 0.0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class ComponentInterface:
    """Basis-Interface für alle Komponenten"""
    
    def __init__(self, component_type: ComponentType, version: str = "1.0.0"):
        self.component_type = component_type
        self.version = version
        self.metadata = {}
    
    def get_component_info(self) -> Dict[str, Any]:
        """Gibt Komponenten-Informationen zurück"""
        return {
            "type": self.component_type.value,
            "version": self.version,
            "metadata": self.metadata
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """Validiert Eingabe (zu überschreiben)"""
        return True
    
    def process(self, input_data: Any) -> Any:
        """Verarbeitet Eingabe (zu überschreiben)"""
        raise NotImplementedError

class ArchitectureRegistry:
    """Registry für alle Komponenten"""
    
    def __init__(self):
        self.components: Dict[ComponentType, ComponentInterface] = {}
        self.templates: Dict[str, PromptTemplate] = {}
        self.pipelines: Dict[str, List[ComponentType]] = {}
    
    def register_component(self, component: ComponentInterface):
        """Registriert eine Komponente"""
        self.components[component.component_type] = component
    
    def get_component(self, component_type: ComponentType) -> Optional[ComponentInterface]:
        """Holt eine Komponente"""
        return self.components.get(component_type)
    
    def register_template(self, template: PromptTemplate):
        """Registriert ein Template"""
        self.templates[template.template_id] = template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Holt ein Template"""
        return self.templates.get(template_id)
    
    def define_pipeline(self, pipeline_id: str, components: List[ComponentType]):
        """Definiert eine Pipeline"""
        self.pipelines[pipeline_id] = components
    
    def get_pipeline(self, pipeline_id: str) -> List[ComponentType]:
        """Holt eine Pipeline"""
        return self.pipelines.get(pipeline_id, [])

# Globale Registry-Instanz
ARCHITECTURE_REGISTRY = ArchitectureRegistry()

def register_component(component: ComponentInterface):
    """Decorator für Komponenten-Registrierung"""
    ARCHITECTURE_REGISTRY.register_component(component)
    return component

def get_component(component_type: ComponentType) -> Optional[ComponentInterface]:
    """Holt eine Komponente aus der Registry"""
    return ARCHITECTURE_REGISTRY.get_component(component_type)

def get_template(template_id: str) -> Optional[PromptTemplate]:
    """Holt ein Template aus der Registry"""
    return ARCHITECTURE_REGISTRY.get_template(template_id) 