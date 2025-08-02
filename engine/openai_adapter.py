import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIAdapter:
    """
    Adapter für die OpenAI ChatGPT API zur Kapitelgenerierung.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den OpenAI Adapter.
        
        Args:
            api_key: OpenAI API Key (optional, wird aus Umgebungsvariablen geladen)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY ist erforderlich")
            
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"
        
    def generate_chapter(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generiert ein Kapitel mit ChatGPT basierend auf dem kompilierten Prompt.
        
        Args:
            prompt: Kompilierter Prompt-Text
            **kwargs: Zusätzliche Parameter (temperature, max_tokens, etc.)
            
        Returns:
            Dictionary mit dem generierten Text und Metadaten
        """
        try:
            # Standard-Parameter
            params = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", 4000),
                "temperature": kwargs.get("temperature", 0.4),
                "messages": [
                    {
                        "role": "system",
                        "content": "Du bist ein erfahrener Autor und Schriftsteller. Schreibe kreative, fesselnde Kapitel."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Optionale Parameter
            if "top_p" in kwargs:
                params["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                params["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                params["presence_penalty"] = kwargs["presence_penalty"]
            
            logger.info(f"Sende Anfrage an ChatGPT (Model: {self.model})")
            
            # API-Aufruf
            response = self.client.chat.completions.create(**params)
            
            # Extrahiere den generierten Text
            generated_text = response.choices[0].message.content if response.choices else ""
            
            # Erstelle Ergebnis-Dictionary
            result = {
                "text": generated_text,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason,
                "metadata": {
                    "temperature": params["temperature"],
                    "max_tokens": params["max_tokens"]
                }
            }
            
            logger.info(f"Kapitel erfolgreich generiert. Tokens: {result['usage']['total_tokens']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der OpenAI API-Anfrage: {e}")
            raise
    
    def generate_chapter_with_retry(self, prompt: str, max_retries: int = 3, **kwargs) -> Dict[str, Any]:
        """
        Generiert ein Kapitel mit Wiederholungsversuchen bei Fehlern.
        
        Args:
            prompt: Kompilierter Prompt-Text
            max_retries: Maximale Anzahl von Wiederholungsversuchen
            **kwargs: Zusätzliche Parameter
            
        Returns:
            Dictionary mit dem generierten Text und Metadaten
        """
        for attempt in range(max_retries):
            try:
                return self.generate_chapter(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Versuch {attempt + 1} fehlgeschlagen: {e}")
                if attempt == max_retries - 1:
                    raise
                # Kurze Pause vor dem nächsten Versuch
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validiert die API-Antwort auf Vollständigkeit und Qualität.
        
        Args:
            response: API-Antwort Dictionary
            
        Returns:
            True wenn die Antwort gültig ist
        """
        try:
            # Prüfe ob Text vorhanden ist
            if not response.get("text") or len(response["text"].strip()) < 50:
                logger.warning("Generierter Text ist zu kurz oder leer")
                return False
            
            # Prüfe Token-Limits
            usage = response.get("usage", {})
            if usage.get("total_tokens", 0) > 128000:  # GPT-4-Turbo Limit
                logger.warning("Token-Limit überschritten")
                return False
            
            # Prüfe Finish Reason
            if response.get("finish_reason") == "length":
                logger.warning("Max Tokens erreicht - Text möglicherweise unvollständig")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Antwortvalidierung: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Gibt Informationen über das verwendete Modell zurück.
        
        Returns:
            Dictionary mit Modell-Informationen
        """
        return {
            "model": self.model,
            "provider": "openai",
            "max_tokens": 128000,
            "supports_system_prompts": True,
            "supports_stop_sequences": True
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Gibt verfügbare OpenAI Modelle zurück.
        
        Returns:
            Dictionary mit verfügbaren Modellen
        """
        try:
            models = self.client.models.list()
            available_models = {}
            
            for model in models.data:
                if "gpt" in model.id.lower():
                    available_models[model.id] = {
                        "id": model.id,
                        "created": model.created,
                        "owned_by": model.owned_by
                    }
            
            return available_models
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der verfügbaren Modelle: {e}")
            return {} 