#!/usr/bin/env python3
"""
Validation Module
Pydantic-basierte Input-Validation für One Click Book Writer
"""

import re
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ValidationError
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Enums
class AgeGroup(str, Enum):
    """Altersgruppen"""
    EARLY_READER = "early_reader"
    MIDDLE_READER = "middle_reader"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    SENIOR = "senior"

class Genre(str, Enum):
    """Genres"""
    FANTASY = "fantasy"
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    SCIENCE_FICTION = "science_fiction"
    ROMANCE = "romance"
    HISTORICAL = "historical"
    CONTEMPORARY = "contemporary"

class Emotion(str, Enum):
    """Emotionen"""
    JOY = "joy"
    SADNESS = "sadness"
    FEAR = "fear"
    ANGER = "anger"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"

class Language(str, Enum):
    """Sprachen"""
    GERMAN = "de"
    ENGLISH = "en"
    BILINGUAL = "bilingual"

# Info Models
class BookInfo(BaseModel):
    """Buch-Informationen"""
    title: str = Field(..., min_length=1, max_length=200, description="Buchtitel")
    genre: Genre = Field(..., description="Genre")
    target_audience: AgeGroup = Field(..., description="Zielgruppe")
    language_variants: List[Language] = Field(default=[Language.GERMAN], description="Sprachvarianten")
    bilingual_sequence: Optional[str] = Field(None, description="Bilinguale Sequenz")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Titel darf nicht leer sein")
        return v.strip()
    
    @field_validator('language_variants')
    @classmethod
    def validate_language_variants(cls, v):
        if not v:
            raise ValueError("Mindestens eine Sprachvariante erforderlich")
        return v
    
    @field_validator('bilingual_sequence')
    @classmethod
    def validate_bilingual_sequence(cls, v):
        if v and v not in ['de_en', 'en_de']:
            raise ValueError("Bilinguale Sequenz muss 'de_en' oder 'en_de' sein")
        return v

class ChapterInfo(BaseModel):
    """Kapitel-Informationen"""
    number: int = Field(..., ge=1, description="Kapitelnummer")
    title: str = Field(..., min_length=1, max_length=100, description="Kapiteltitel")
    narrative_purpose: str = Field(..., min_length=1, max_length=500, description="Narrative Funktion")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Titel darf nicht leer sein")
        return v.strip()
    
    @field_validator('narrative_purpose')
    @classmethod
    def validate_narrative_purpose(cls, v):
        if not v or not v.strip():
            raise ValueError("Narrative Funktion darf nicht leer sein")
        return v.strip()

class CharacterInfo(BaseModel):
    """Charakter-Informationen"""
    name: str = Field(..., min_length=1, max_length=50, description="Charaktername")
    role: str = Field(..., min_length=1, max_length=100, description="Charakterrolle")
    description: str = Field(..., min_length=1, max_length=500, description="Charakterbeschreibung")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name darf nicht leer sein")
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Beschreibung darf nicht leer sein")
        return v.strip()

class SceneInfo(BaseModel):
    """Szenen-Informationen"""
    setting: str = Field(..., min_length=1, max_length=200, description="Schauplatz")
    time_period: str = Field(..., min_length=1, max_length=100, description="Zeitperiode")
    atmosphere: str = Field(..., min_length=1, max_length=200, description="Atmosphäre")
    
    @field_validator('setting')
    @classmethod
    def validate_setting(cls, v):
        if not v or not v.strip():
            raise ValueError("Schauplatz darf nicht leer sein")
        return v.strip()

class PlotInfo(BaseModel):
    """Plot-Informationen"""
    main_event: str = Field(..., min_length=1, max_length=300, description="Hauptereignis")
    conflict: str = Field(..., min_length=1, max_length=300, description="Konflikt")
    resolution: str = Field(..., min_length=1, max_length=300, description="Auflösung")
    
    @field_validator('main_event')
    @classmethod
    def validate_main_event(cls, v):
        if not v or not v.strip():
            raise ValueError("Hauptereignis darf nicht leer sein")
        return v.strip()

# Main Models
class PromptFrame(BaseModel):
    """PromptFrame für Kapitel-Generierung"""
    input: Dict[str, Any] = Field(..., description="Input-Daten")
    
    @field_validator('input')
    @classmethod
    def validate_input(cls, v):
        required_keys = ['book', 'chapter']
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Erforderlicher Input-Schlüssel fehlt: {key}")
        return v

class FeedbackEntry(BaseModel):
    """Feedback-Eintrag"""
    comment: str = Field(..., min_length=1, max_length=1000, description="Feedback-Kommentar")
    rating: float = Field(..., ge=0.0, le=1.0, description="Bewertung (0.0-1.0)")
    category: str = Field(..., min_length=1, max_length=50, description="Feedback-Kategorie")
    
    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v):
        if not v or not v.strip():
            raise ValueError("Kommentar darf nicht leer sein")
        return v.strip()

class APIRequest(BaseModel):
    """API-Request"""
    prompt_frame: PromptFrame = Field(..., description="PromptFrame")
    engine: str = Field(..., pattern="^(claude|chatgpt)$", description="AI Engine")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Max Tokens")

class ValidationResult(BaseModel):
    """Validierungsergebnis"""
    valid: bool = Field(..., description="Gültig oder nicht")
    errors: List[str] = Field(default_factory=list, description="Validierungsfehler")
    warnings: List[str] = Field(default_factory=list, description="Warnungen")
    data: Optional[Dict[str, Any]] = Field(None, description="Validierte Daten")

# Validation Functions
def validate_prompt_frame(data: Dict[str, Any]) -> ValidationResult:
    """
    Validiert einen PromptFrame
    
    Args:
        data: Zu validierende Daten
        
    Returns:
        ValidationResult mit Ergebnis
    """
    try:
        warnings = []
        errors = []
        
        # Prüfe ob data die erwartete Struktur hat
        if not isinstance(data, dict):
            return ValidationResult(
                valid=False,
                errors=["Daten müssen ein Dictionary sein"],
                data=data
            )
        
        # Extrahiere input-Daten
        input_data = data.get('input', data)
        
        # Validiere Buch-Informationen
        if 'book' in input_data:
            try:
                BookInfo(**input_data['book'])
            except ValidationError as e:
                errors.append(f"Buch-Validierung: {e}")
        
        # Validiere Kapitel-Informationen
        if 'chapter' in input_data:
            try:
                ChapterInfo(**input_data['chapter'])
            except ValidationError as e:
                errors.append(f"Kapitel-Validierung: {e}")
        
        # Prüfe ob mindestens 'book' oder 'chapter' vorhanden ist
        if 'book' not in input_data and 'chapter' not in input_data:
            errors.append("Mindestens 'book' oder 'chapter' muss vorhanden sein")
        
        # Wenn es Fehler gibt, ist das Ergebnis ungültig
        if errors:
            return ValidationResult(
                valid=False,
                errors=errors,
                data=data
            )
        
        return ValidationResult(
            valid=True,
            warnings=warnings,
            data=data
        )
        
    except Exception as e:
        return ValidationResult(
            valid=False,
            errors=[f"Unerwarteter Validierungsfehler: {e}"],
            data=data
        )

def validate_feedback(data: Dict[str, Any]) -> ValidationResult:
    """
    Validiert Feedback-Daten
    
    Args:
        data: Zu validierende Feedback-Daten
        
    Returns:
        ValidationResult mit Ergebnis
    """
    try:
        feedback = FeedbackEntry(**data)
        return ValidationResult(
            valid=True,
            data=data
        )
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'unknown'
            message = error['msg']
            errors.append(f"{field}: {message}")
        
        return ValidationResult(
            valid=False,
            errors=errors,
            data=data
        )

def validate_api_request(data: Dict[str, Any]) -> ValidationResult:
    """
    Validiert API-Request
    
    Args:
        data: Zu validierende API-Request-Daten
        
    Returns:
        ValidationResult mit Ergebnis
    """
    try:
        api_request = APIRequest(**data)
        return ValidationResult(
            valid=True,
            data=data
        )
    except ValidationError as e:
        errors = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'unknown'
            message = error['msg']
            errors.append(f"{field}: {message}")
        
        return ValidationResult(
            valid=False,
            errors=errors,
            data=data
        )

def sanitize_input(text: str) -> str:
    """
    Sanitisiert Input-Text
    
    Args:
        text: Zu sanitierender Text
        
    Returns:
        Sanitisierter Text
    """
    if not text:
        return ""
    
    # Entferne gefährliche HTML-Tags und deren Inhalt
    dangerous_tags = ['script', 'img', 'input', 'iframe', 'object', 'embed']
    for tag in dangerous_tags:
        text = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(rf'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
    
    # Entferne alle anderen HTML-Tags, aber behalte den Inhalt
    text = re.sub(r'<[^>]+>', '', text)
    
    # Entferne gefährliche Zeichen und Sequenzen
    text = re.sub(r'[<>"\']', '', text)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Entferne mehrfache Whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def validate_and_sanitize_input(data: Dict[str, Any]) -> ValidationResult:
    """
    Validiert und sanitisiert Input-Daten
    
    Args:
        data: Zu validierende und sanitierende Daten
        
    Returns:
        ValidationResult mit Ergebnis
    """
    try:
        sanitized_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = sanitize_input(value)
            elif isinstance(value, dict):
                sanitized_data[key] = validate_and_sanitize_input(value).data
            else:
                sanitized_data[key] = value
        
        return ValidationResult(
            valid=True,
            data=sanitized_data
        )
    except Exception as e:
        return ValidationResult(
            valid=False,
            errors=[f"Fehler bei Input-Sanitization: {e}"],
            data=data
        ) 