import json
import logging
from typing import Dict, Any
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


def validate_json_schema(data: Dict[str, Any], schema_path: str) -> (bool, str):
    """
    Validiert JSON-Daten gegen ein Schema.
    Returns:
        (True, "OK") wenn gültig, (False, Fehlertext) sonst
    """
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        validate(instance=data, schema=schema)
        logger.info("JSON-Schema-Validierung erfolgreich")
        return True, "OK"
    except FileNotFoundError:
        logger.error(f"Schema-Datei nicht gefunden: {schema_path}")
        return False, f"Schema-Datei nicht gefunden: {schema_path}"
    except json.JSONDecodeError as e:
        logger.error(f"Ungültige Schema-Datei: {e}")
        return False, f"Ungültige Schema-Datei: {e}"
    except ValidationError as e:
        logger.error(f"Schema-Validierungsfehler: {e}")
        return False, f"Schema-Validierungsfehler: {e}"
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei der Schema-Validierung: {e}")
        return False, f"Unerwarteter Fehler: {e}"


def validate_prompt_frame_structure(data: Dict[str, Any]) -> bool:
    """
    Validiert die grundlegende Struktur eines PromptFrames.
    
    Args:
        data: Zu validierende Daten
        
    Returns:
        True wenn gültig, False sonst
    """
    try:
        # Prüfe ob "input" vorhanden ist
        if "input" not in data:
            logger.error("Fehlender 'input' Schlüssel")
            return False
        
        input_data = data["input"]
        required_keys = ["chapter", "book", "style", "story_context", "constraints"]
        
        for key in required_keys:
            if key not in input_data:
                logger.error(f"Fehlender Pflichtschlüssel: {key}")
                return False
        
        # Prüfe Kapitel-Struktur
        chapter = input_data["chapter"]
        chapter_keys = ["number", "title", "narrative_purpose", "position_in_arc", "length_words"]
        for key in chapter_keys:
            if key not in chapter:
                logger.error(f"Fehlender Kapitel-Schlüssel: {key}")
                return False
        
        # Prüfe Buch-Struktur
        book = input_data["book"]
        book_keys = ["title", "genre", "target_audience"]
        for key in book_keys:
            if key not in book:
                logger.error(f"Fehlender Buch-Schlüssel: {key}")
                return False
        
        # Prüfe Stil-Struktur
        style = input_data["style"]
        style_keys = ["writing_style", "tone", "tense", "perspective", "sentence_complexity"]
        for key in style_keys:
            if key not in style:
                logger.error(f"Fehlender Stil-Schlüssel: {key}")
                return False
        
        # Prüfe Story-Kontext
        story_context = input_data["story_context"]
        if "current_scene" not in story_context:
            logger.error("Fehlender 'current_scene' in story_context")
            return False
        
        # Prüfe Constraints
        constraints = input_data["constraints"]
        constraint_keys = ["structure", "format"]
        for key in constraint_keys:
            if key not in constraints:
                logger.error(f"Fehlender Constraint-Schlüssel: {key}")
                return False
        
        logger.info("PromptFrame-Struktur ist gültig")
        return True
        
    except Exception as e:
        logger.error(f"Fehler bei der Strukturvalidierung: {e}")
        return False


def get_validation_errors(data: Dict[str, Any], schema_path: str) -> list:
    """
    Gibt detaillierte Validierungsfehler zurück.
    
    Args:
        data: Zu validierende Daten
        schema_path: Pfad zur Schema-Datei
        
    Returns:
        Liste von Validierungsfehlern
    """
    errors = []
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        from jsonschema import Draft7Validator
        validator = Draft7Validator(schema)
        
        for error in validator.iter_errors(data):
            errors.append({
                "path": " -> ".join(str(p) for p in error.path),
                "message": error.message,
                "schema_path": " -> ".join(str(p) for p in error.schema_path)
            })
        
    except Exception as e:
        errors.append({
            "path": "schema",
            "message": f"Fehler beim Laden des Schemas: {e}",
            "schema_path": schema_path
        })
    
    return errors 