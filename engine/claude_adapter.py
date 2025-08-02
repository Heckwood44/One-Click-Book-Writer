import os
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeAdapter:
    """
    Adapter für die Anthropic Claude API zur Kapitelgenerierung.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den Claude Adapter.
        
        Args:
            api_key: Anthropic API Key (optional, wird aus Umgebungsvariablen geladen)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY ist erforderlich")
            
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"
        
    def generate_chapter(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generiert ein Kapitel mit Claude basierend auf dem kompilierten Prompt.
        
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
                "max_tokens": kwargs.get("max_tokens", 8000),
                "temperature": kwargs.get("temperature", 0.4),
                "system": "Du bist ein erfahrener Autor und Schriftsteller. Schreibe kreative, fesselnde Kapitel.",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Optionale Stop-Sequenzen
            if "stop_sequences" in kwargs:
                params["stop_sequences"] = kwargs["stop_sequences"]
            
            logger.info(f"Sende Anfrage an Claude (Model: {self.model})")
            
            # API-Aufruf
            response = self.client.messages.create(**params)
            
            # Extrahiere den generierten Text
            generated_text = response.content[0].text if response.content else ""
            
            # Erstelle Ergebnis-Dictionary
            result = {
                "text": generated_text,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "finish_reason": response.stop_reason,
                "metadata": {
                    "temperature": params["temperature"],
                    "max_tokens": params["max_tokens"]
                }
            }
            
            logger.info(f"Kapitel erfolgreich generiert. Tokens: {result['usage']['total_tokens']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Claude API-Anfrage: {e}")
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
            if usage.get("total_tokens", 0) > 32000:  # Claude-3-Opus Limit
                logger.warning("Token-Limit überschritten")
                return False
            
            # Prüfe Finish Reason
            if response.get("finish_reason") == "max_tokens":
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
            "provider": "anthropic",
            "max_tokens": 32000,
            "supports_system_prompts": True,
            "supports_stop_sequences": True
        } 