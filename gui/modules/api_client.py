#!/usr/bin/env python3
"""
API Client Module
Zentrale API-Client-Verwaltung für One Click Book Writer
"""

import os
import logging
from typing import Dict, Any, Optional, Union
import openai
import anthropic
from dotenv import load_dotenv
from core.security import secure_log, mask_secret, validate_api_key

# Setup Logging
logger = logging.getLogger(__name__)

class APIClient:
    """Zentrale API-Client-Verwaltung"""
    
    def __init__(self) -> None:
        """Initialisiert die API-Clients"""
        # Lade Umgebungsvariablen
        load_dotenv()
        
        # API Keys prüfen
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
        
        # API Clients initialisieren
        self._init_openai_client()
        self._init_claude_client()
    
    def _init_openai_client(self) -> None:
        """Initialisiert OpenAI Client"""
        if self.openai_api_key:
            # Validiere API Key
            if not validate_api_key(self.openai_api_key, "openai"):
                logger.error("Ungültiger OpenAI API Key")
                self.openai_api_key = None
                return
            
            openai.api_key = self.openai_api_key
            # SICHER: Verwende maskierten Key für Logging
            masked_key = mask_secret(self.openai_api_key)
            secure_log(f"OpenAI Client initialisiert mit Key: {masked_key}")
        else:
            logger.warning("OPENAI_API_KEY nicht gefunden")
    
    def _init_claude_client(self) -> None:
        """Initialisiert Claude Client"""
        self.claude_client: Optional[anthropic.Anthropic] = None
        if self.anthropic_api_key and len(self.anthropic_api_key.strip()) > 0:
            # Validiere API Key
            if not validate_api_key(self.anthropic_api_key, "anthropic"):
                logger.error("Ungültiger Anthropic API Key")
                self.anthropic_api_key = None
                return
            
            try:
                self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                # SICHER: Verwende maskierten Key für Logging
                masked_key = mask_secret(self.anthropic_api_key)
                secure_log(f"Claude Client erfolgreich initialisiert mit Key: {masked_key}")
            except Exception as e:
                secure_log(f"Claude Client Initialisierung fehlgeschlagen: {e}", "ERROR")
                # Fallback: Versuche es ohne zusätzliche Parameter
                try:
                    self.claude_client = anthropic.Anthropic()
                    self.claude_client.api_key = self.anthropic_api_key
                    # SICHER: Verwende maskierten Key für Logging
                    masked_key = mask_secret(self.anthropic_api_key)
                    secure_log(f"Claude Client erfolgreich initialisiert (Fallback) mit Key: {masked_key}")
                except Exception as e2:
                    secure_log(f"Claude Client Fallback fehlgeschlagen: {e2}", "ERROR")
                    self.claude_client = None
    
    def get_openai_client(self) -> Optional[Any]:
        """Gibt OpenAI Client zurück"""
        return openai if self.openai_api_key else None
    
    def get_claude_client(self) -> Optional[anthropic.Anthropic]:
        """Gibt Claude Client zurück"""
        return self.claude_client
    
    def is_openai_available(self) -> bool:
        """Prüft ob OpenAI verfügbar ist"""
        return bool(self.openai_api_key)
    
    def is_claude_available(self) -> bool:
        """Prüft ob Claude verfügbar ist"""
        return bool(self.claude_client)
    
    def get_status(self) -> Dict[str, bool]:
        """Gibt Status der API-Clients zurück"""
        return {
            'openai_available': self.is_openai_available(),
            'claude_available': self.is_claude_available(),
            'openai_key_present': bool(self.openai_api_key),
            'claude_key_present': bool(self.anthropic_api_key)
        } 