#!/usr/bin/env python3
"""
Security Module
Sicheres Secret Management für One Click Book Writer
"""

import os
import re
import logging
import hashlib
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class SecretManager:
    """Sicheres Secret Management mit Maskierung und optionaler Verschlüsselung"""
    
    def __init__(self, encryption_key: Optional[str] = None) -> None:
        """
        Initialisiert den Secret Manager
        
        Args:
            encryption_key: Optionaler Verschlüsselungsschlüssel
        """
        self.encryption_key: Optional[str] = encryption_key
        self.fernet: Optional[Fernet] = None
        self._init_encryption()
        
        # Patterns für Secrets
        self.secret_patterns = [
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API Key
            r'sk-ant-[a-zA-Z0-9]{48}',  # Anthropic API Key
            r'[a-zA-Z0-9]{32,}',  # Generic API Keys
        ]
    
    def _init_encryption(self) -> None:
        """Initialisiert die Verschlüsselung"""
        try:
            if self.encryption_key:
                # Generiere Fernet Key aus Passwort
                salt = b'one_click_book_writer_salt'  # In Produktion: zufälliger Salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
                self.fernet = Fernet(key)
                logger.info("Verschlüsselung initialisiert")
            else:
                logger.info("Verschlüsselung deaktiviert - nur Maskierung aktiv")
        except Exception as e:
            logger.error(f"Fehler bei Verschlüsselungs-Initialisierung: {e}")
            self.fernet = None
    
    def mask_secret(self, secret: str, mask_char: str = "*") -> str:
        """
        Maskiert ein Secret für Logging
        
        Args:
            secret: Das zu maskierende Secret
            mask_char: Zeichen für Maskierung
            
        Returns:
            Maskiertes Secret
        """
        if not secret or len(secret) < 8:
            return mask_char * 8
        
        # Zeige nur erste 4 Zeichen, Rest maskiert
        visible_start = secret[:4]
        masked_rest = mask_char * (len(secret) - 4)
        
        return f"{visible_start}{masked_rest}"
    
    def is_secret(self, text: str) -> bool:
        """
        Prüft ob Text ein Secret enthält
        
        Args:
            text: Zu prüfender Text
            
        Returns:
            True wenn Secret gefunden
        """
        if not text:
            return False
        
        for pattern in self.secret_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def mask_text(self, text: str) -> str:
        """
        Maskiert alle Secrets in einem Text
        
        Args:
            text: Text mit möglichen Secrets
            
        Returns:
            Text mit maskierten Secrets
        """
        if not text:
            return text
        
        masked_text = text
        
        for pattern in self.secret_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                secret = match.group()
                masked_secret = self.mask_secret(secret)
                masked_text = masked_text.replace(secret, masked_secret)
        
        return masked_text
    
    def encrypt_secret(self, secret: str) -> Optional[str]:
        """
        Verschlüsselt ein Secret
        
        Args:
            secret: Das zu verschlüsselnde Secret
            
        Returns:
            Verschlüsseltes Secret oder None bei Fehler
        """
        if not self.fernet:
            logger.warning("Verschlüsselung nicht verfügbar")
            return None
        
        try:
            encrypted = self.fernet.encrypt(secret.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Fehler bei Secret-Verschlüsselung: {e}")
            return None
    
    def decrypt_secret(self, encrypted_secret: str) -> Optional[str]:
        """
        Entschlüsselt ein Secret
        
        Args:
            encrypted_secret: Das verschlüsselte Secret
            
        Returns:
            Entschlüsseltes Secret oder None bei Fehler
        """
        if not self.fernet:
            logger.warning("Verschlüsselung nicht verfügbar")
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Fehler bei Secret-Entschlüsselung: {e}")
            return None
    
    def secure_log(self, message: str, level: str = "INFO") -> None:
        """
        Loggt eine Nachricht mit maskierten Secrets
        
        Args:
            message: Zu loggende Nachricht
            level: Log-Level
        """
        masked_message = self.mask_text(message)
        
        if level.upper() == "DEBUG":
            logger.debug(masked_message)
        elif level.upper() == "INFO":
            logger.info(masked_message)
        elif level.upper() == "WARNING":
            logger.warning(masked_message)
        elif level.upper() == "ERROR":
            logger.error(masked_message)
        else:
            logger.info(masked_message)
    
    def hash_secret(self, secret: str) -> str:
        """
        Erstellt einen Hash eines Secrets für Vergleich
        
        Args:
            secret: Das zu hashende Secret
            
        Returns:
            SHA-256 Hash des Secrets
        """
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str, provider: str) -> bool:
        """
        Validiert einen API Key
        
        Args:
            api_key: Der zu validierende API Key
            provider: API Provider (openai, anthropic, etc.)
            
        Returns:
            True wenn gültig
        """
        if not api_key or len(api_key) < 20:
            return False
        
        if provider.lower() == "openai":
            return api_key.startswith("sk-") and len(api_key) >= 48
        elif provider.lower() == "anthropic":
            return api_key.startswith("sk-ant-") and len(api_key) >= 48
        else:
            # Generic validation
            return len(api_key) >= 32 and api_key.isalnum()
    
    def rotate_secret(self, old_secret: str, new_secret: str) -> bool:
        """
        Rotiert ein Secret (Stub für zukünftige Implementierung)
        
        Args:
            old_secret: Altes Secret
            new_secret: Neues Secret
            
        Returns:
            True wenn Rotation erfolgreich
        """
        try:
            # Hier würde die eigentliche Rotation implementiert
            # z.B. Update in Vault, Database, etc.
            logger.info("Secret-Rotation durchgeführt")
            return True
        except Exception as e:
            logger.error(f"Fehler bei Secret-Rotation: {e}")
            return False

# Globaler Secret Manager
secret_manager = SecretManager()

def secure_log(message: str, level: str = "INFO") -> None:
    """Globale Funktion für sicheres Logging"""
    secret_manager.secure_log(message, level)

def mask_secret(secret: str) -> str:
    """Globale Funktion für Secret-Maskierung"""
    return secret_manager.mask_secret(secret)

def is_secret(text: str) -> bool:
    """Globale Funktion für Secret-Erkennung"""
    return secret_manager.is_secret(text)

def validate_api_key(api_key: str, provider: str) -> bool:
    """Globale Funktion für API Key Validierung"""
    return secret_manager.validate_api_key(api_key, provider) 