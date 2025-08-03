#!/usr/bin/env python3
"""
One Click Book Writer SDK
Python SDK für einfache Integration des selbstlernenden Prompt-Engineering-Frameworks
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PromptFrameBuilder:
    """Builder für PromptFrame-Objekte"""
    age_group: str
    genre: str
    emotion: str
    language: str = "de"
    target_audience: Optional[str] = None
    custom_context: Optional[Dict[str, Any]] = None
    
    def with_target_audience(self, audience: str) -> 'PromptFrameBuilder':
        """Setzt Zielgruppe"""
        self.target_audience = audience
        return self
    
    def with_custom_context(self, context: Dict[str, Any]) -> 'PromptFrameBuilder':
        """Setzt benutzerdefinierten Kontext"""
        self.custom_context = context
        return self
    
    def with_description(self, description: str) -> 'PromptFrameBuilder':
        """Fügt Beschreibung hinzu"""
        if not self.custom_context:
            self.custom_context = {}
        self.custom_context["description"] = description
        return self
    
    def with_instructions(self, instructions: str) -> 'PromptFrameBuilder':
        """Fügt Anweisungen hinzu"""
        if not self.custom_context:
            self.custom_context = {}
        self.custom_context["instructions"] = instructions
        return self
    
    def with_characters(self, characters: str) -> 'PromptFrameBuilder':
        """Fügt Charaktere hinzu"""
        if not self.custom_context:
            self.custom_context = {}
        self.custom_context["characters"] = characters
        return self
    
    def with_setting(self, setting: str) -> 'PromptFrameBuilder':
        """Fügt Setting hinzu"""
        if not self.custom_context:
            self.custom_context = {}
        self.custom_context["setting"] = setting
        return self
    
    def build(self) -> Dict[str, Any]:
        """Erstellt PromptFrame-Dictionary"""
        return {
            "age_group": self.age_group,
            "genre": self.genre,
            "emotion": self.emotion,
            "language": self.language,
            "target_audience": self.target_audience,
            "custom_context": self.custom_context or {}
        }

@dataclass
class GenerationResult:
    """Ergebnis der Kapitelgenerierung"""
    run_id: str
    chapter_text: str
    german_text: str
    english_text: str
    quality_score: float
    word_count: int
    execution_time: float
    total_cost: float
    compliance_status: str
    template_hash: str
    optimization_delta: Optional[float] = None
    ab_test_improvement: Optional[float] = None
    policy_decision: Optional[Dict[str, Any]] = None
    drift_alerts: Optional[List[Dict[str, Any]]] = None

@dataclass
class FeedbackResult:
    """Ergebnis der Feedback-Einreichung"""
    status: str
    feedback_id: str
    features_extracted: int
    suggestions_generated: int
    message: str

class BookWriterSDK:
    """Python SDK für One Click Book Writer"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def create_prompt_frame(self, age_group: str, genre: str, emotion: str, language: str = "de") -> PromptFrameBuilder:
        """Erstellt einen PromptFrame Builder"""
        return PromptFrameBuilder(age_group, genre, emotion, language)
    
    def generate_chapter(self, 
                        prompt_frame: Union[PromptFrameBuilder, Dict[str, Any]],
                        enable_optimization: bool = True,
                        enable_ab_testing: bool = False,
                        enable_feedback_collection: bool = True,
                        max_retries: int = 3) -> GenerationResult:
        """Generiert ein Kapitel (One-liner)"""
        try:
            # Konvertiere PromptFrame zu Dictionary
            if isinstance(prompt_frame, PromptFrameBuilder):
                request_data = prompt_frame.build()
            else:
                request_data = prompt_frame
            
            # Füge Optionen hinzu
            request_data.update({
                "enable_optimization": enable_optimization,
                "enable_ab_testing": enable_ab_testing,
                "enable_feedback_collection": enable_feedback_collection,
                "max_retries": max_retries
            })
            
            # API-Request
            response = self.session.post(f"{self.base_url}/generate", json=request_data)
            response.raise_for_status()
            
            result_data = response.json()
            
            return GenerationResult(
                run_id=result_data["run_id"],
                chapter_text=result_data["chapter_text"],
                german_text=result_data["german_text"],
                english_text=result_data["english_text"],
                quality_score=result_data["quality_score"],
                word_count=result_data["word_count"],
                execution_time=result_data["execution_time"],
                total_cost=result_data["total_cost"],
                compliance_status=result_data["compliance_status"],
                template_hash=result_data["template_hash"],
                optimization_delta=result_data.get("optimization_delta"),
                ab_test_improvement=result_data.get("ab_test_improvement"),
                policy_decision=result_data.get("policy_decision"),
                drift_alerts=result_data.get("drift_alerts")
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def submit_feedback(self, run_id: str, user_rating: int, comment: str, language: str = "de") -> FeedbackResult:
        """Reicht Feedback für ein generiertes Kapitel ein"""
        try:
            request_data = {
                "run_id": run_id,
                "user_rating": user_rating,
                "comment": comment,
                "language": language
            }
            
            response = self.session.post(f"{self.base_url}/feedback", json=request_data)
            response.raise_for_status()
            
            result_data = response.json()
            
            return FeedbackResult(
                status=result_data["status"],
                feedback_id=result_data["feedback_id"],
                features_extracted=result_data["features_extracted"],
                suggestions_generated=result_data["suggestions_generated"],
                message=result_data["message"]
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Feedback submission failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Feedback submission failed: {e}")
            raise
    
    def get_template_status(self, segment: str, include_history: bool = False) -> Dict[str, Any]:
        """Gibt Template-Status für ein Segment zurück"""
        try:
            params = {
                "segment": segment,
                "include_history": include_history
            }
            
            response = self.session.get(f"{self.base_url}/template-status", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Template status retrieval failed: {e}")
            raise
    
    def get_presets(self) -> List[Dict[str, Any]]:
        """Gibt verfügbare Presets zurück"""
        try:
            response = self.session.get(f"{self.base_url}/presets")
            response.raise_for_status()
            
            result_data = response.json()
            return result_data["presets"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Preset retrieval failed: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Gibt System-Metriken zurück"""
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Metrics retrieval failed: {e}")
            raise
    
    def get_diff(self, run_id: str) -> Dict[str, Any]:
        """Gibt Diff zwischen Original- und optimiertem Prompt zurück"""
        try:
            response = self.session.get(f"{self.base_url}/diff/{run_id}")
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Diff retrieval failed: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Führt Health Check durch"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            raise

# Convenience Functions
def quick_generate(age_group: str, genre: str, emotion: str, 
                  description: str = None, api_key: str = None, 
                  base_url: str = "http://localhost:8000") -> GenerationResult:
    """Schnelle Kapitelgenerierung mit minimalen Parametern"""
    if not api_key:
        api_key = os.getenv("BOOKWRITER_API_KEY")
        if not api_key:
            raise ValueError("API key required. Set BOOKWRITER_API_KEY environment variable or pass api_key parameter.")
    
    sdk = BookWriterSDK(api_key, base_url)
    
    builder = sdk.create_prompt_frame(age_group, genre, emotion)
    if description:
        builder.with_description(description)
    
    return sdk.generate_chapter(builder)

def quick_feedback(run_id: str, rating: int, comment: str, 
                  api_key: str = None, base_url: str = "http://localhost:8000") -> FeedbackResult:
    """Schnelle Feedback-Einreichung"""
    if not api_key:
        api_key = os.getenv("BOOKWRITER_API_KEY")
        if not api_key:
            raise ValueError("API key required. Set BOOKWRITER_API_KEY environment variable or pass api_key parameter.")
    
    sdk = BookWriterSDK(api_key, base_url)
    return sdk.submit_feedback(run_id, rating, comment)

# Preset Builders
class PresetBuilders:
    """Vordefinierte Preset-Builder für häufige Anwendungsfälle"""
    
    @staticmethod
    def early_reader_adventure() -> PromptFrameBuilder:
        """Early Reader Adventure Preset"""
        return PromptFrameBuilder("early_reader", "adventure", "courage")
    
    @staticmethod
    def middle_grade_fantasy() -> PromptFrameBuilder:
        """Middle Grade Fantasy Preset"""
        return PromptFrameBuilder("middle_grade", "fantasy", "wonder")
    
    @staticmethod
    def young_adult_self_discovery() -> PromptFrameBuilder:
        """Young Adult Self-Discovery Preset"""
        return PromptFrameBuilder("young_adult", "self_discovery", "growth")
    
    @staticmethod
    def preschool_friendship() -> PromptFrameBuilder:
        """Preschool Friendship Preset"""
        return PromptFrameBuilder("preschool", "friendship", "friendship")
    
    @staticmethod
    def adult_mystery() -> PromptFrameBuilder:
        """Adult Mystery Preset"""
        return PromptFrameBuilder("adult", "mystery", "mystery")

# Beispiel-Nutzung
if __name__ == "__main__":
    # Beispiel 1: Schnelle Generierung
    try:
        result = quick_generate(
            age_group="early_reader",
            genre="adventure", 
            emotion="courage",
            description="Eine mutige Entdeckungsreise im magischen Wald"
        )
        print(f"Kapitel generiert: {result.word_count} Wörter, Quality Score: {result.quality_score}")
        print(f"Deutscher Text: {result.german_text[:200]}...")
        
        # Feedback einreichen
        feedback = quick_feedback(
            run_id=result.run_id,
            rating=5,
            comment="Perfekte Adventure-Geschichte für 6-8 Jährige!"
        )
        print(f"Feedback eingereicht: {feedback.message}")
        
    except Exception as e:
        print(f"Fehler: {e}")
    
    # Beispiel 2: Vollständige SDK-Nutzung
    try:
        api_key = os.getenv("BOOKWRITER_API_KEY")
        if api_key:
            sdk = BookWriterSDK(api_key)
            
            # Erstelle PromptFrame mit Builder
            prompt_frame = (PresetBuilders.middle_grade_fantasy()
                          .with_description("Magische Fantasy-Welt mit sprechenden Tieren")
                          .with_instructions("Betone Wunder und Magie, verwende bildhafte Sprache")
                          .with_characters("Junge Protagonist, weise Eule, mutiger Wolf")
                          .with_setting("Verzauberter Wald mit glitzernden Bäumen"))
            
            # Generiere Kapitel
            result = sdk.generate_chapter(prompt_frame, enable_optimization=True)
            print(f"Fantasy-Kapitel generiert: {result.word_count} Wörter")
            
            # Template-Status abrufen
            status = sdk.get_template_status("middle_grade_fantasy")
            print(f"Template-Ranking: {len(status['template_ranking'])} Templates")
            
    except Exception as e:
        print(f"SDK-Fehler: {e}") 