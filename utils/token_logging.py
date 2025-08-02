#!/usr/bin/env python3
"""
One Click Book Writer - Token Logging
Version: 2.0.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TokenLogger:
    """Verwaltet Token-Logging und Kostenverfolgung"""
    
    def __init__(self, log_file: str = "output/token_usage.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.usage_data = self._load_usage_data()
        
        # Token-Preise (USD pro 1K Tokens)
        self.token_prices = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
            },
            "anthropic": {
                "claude-3-opus": {"input": 0.015, "output": 0.075},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
            }
        }
    
    def _load_usage_data(self) -> Dict:
        """Lädt die Nutzungsdaten"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Nutzungsdaten: {e}")
                return {"api_calls": [], "summary": {}}
        return {"api_calls": [], "summary": {}}
    
    def _save_usage_data(self):
        """Speichert die Nutzungsdaten"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Nutzungsdaten: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Einfache Token-Zählung (Näherung)"""
        # Näherung: 1 Token ≈ 4 Zeichen für Englisch, 3 Zeichen für Deutsch
        return len(text) // 4
    
    def log_api_call(self, 
                    provider: str, 
                    model: str, 
                    tokens: int, 
                    call_type: str,
                    input_tokens: Optional[int] = None,
                    output_tokens: Optional[int] = None) -> Dict:
        """Loggt einen API-Call"""
        
        # Token-Aufteilung schätzen falls nicht angegeben
        if input_tokens is None and output_tokens is None:
            if call_type == "chapter_generation":
                input_tokens = int(tokens * 0.3)  # 30% Input
                output_tokens = int(tokens * 0.7)  # 70% Output
            else:
                input_tokens = int(tokens * 0.5)  # 50/50
                output_tokens = int(tokens * 0.5)
        
        # Kosten berechnen
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        
        # Call loggen
        call_data = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "call_type": call_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost
        }
        
        self.usage_data["api_calls"].append(call_data)
        self._save_usage_data()
        
        logger.info(f"API-Call geloggt: {provider}/{model} - {input_tokens + output_tokens} Tokens - ${cost:.4f}")
        
        return call_data
    
    def calculate_cost(self, 
                      provider: str, 
                      model: str, 
                      input_tokens: int, 
                      output_tokens: int) -> float:
        """Berechnet die Kosten für einen API-Call"""
        
        if provider not in self.token_prices or model not in self.token_prices[provider]:
            logger.warning(f"Unbekannte Provider/Model Kombination: {provider}/{model}")
            return 0.0
        
        prices = self.token_prices[provider][model]
        
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        
        return input_cost + output_cost
    
    def get_usage_summary(self) -> Dict:
        """Gibt eine Zusammenfassung der API-Nutzung zurück"""
        calls = self.usage_data.get("api_calls", [])
        
        if not calls:
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "by_provider": {},
                "by_model": {}
            }
        
        # Gesamtstatistiken
        total_calls = len(calls)
        total_tokens = sum(call.get("total_tokens", 0) for call in calls)
        total_cost = sum(call.get("cost_usd", 0) for call in calls)
        
        # Nach Provider gruppieren
        by_provider = {}
        for call in calls:
            provider = call.get("provider", "unknown")
            if provider not in by_provider:
                by_provider[provider] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
            by_provider[provider]["calls"] += 1
            by_provider[provider]["tokens"] += call.get("total_tokens", 0)
            by_provider[provider]["cost"] += call.get("cost_usd", 0)
        
        # Nach Model gruppieren
        by_model = {}
        for call in calls:
            model = call.get("model", "unknown")
            if model not in by_model:
                by_model[model] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
            by_model[model]["calls"] += 1
            by_model[model]["tokens"] += call.get("total_tokens", 0)
            by_model[model]["cost"] += call.get("cost_usd", 0)
        
        return {
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "by_provider": by_provider,
            "by_model": by_model
        }
    
    def get_cost_estimate(self, 
                         provider: str, 
                         model: str, 
                         estimated_tokens: int,
                         call_type: str = "chapter_generation") -> Dict:
        """Schätzt die Kosten für einen geplanten API-Call"""
        
        # Token-Aufteilung schätzen
        if call_type == "chapter_generation":
            input_tokens = int(estimated_tokens * 0.3)
            output_tokens = int(estimated_tokens * 0.7)
        else:
            input_tokens = int(estimated_tokens * 0.5)
            output_tokens = int(estimated_tokens * 0.5)
        
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        
        return {
            "provider": provider,
            "model": model,
            "estimated_tokens": estimated_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 4),
            "call_type": call_type
        }
    
    def get_budget_alerts(self, budget_limit_usd: float = 10.0) -> List[str]:
        """Gibt Budget-Warnungen zurück"""
        summary = self.get_usage_summary()
        total_cost = summary["total_cost_usd"]
        
        alerts = []
        
        if total_cost >= budget_limit_usd:
            alerts.append(f"⚠️ Budget-Limit erreicht: ${total_cost:.2f} von ${budget_limit_usd:.2f}")
        elif total_cost >= budget_limit_usd * 0.8:
            alerts.append(f"⚠️ Budget-Warnung: ${total_cost:.2f} von ${budget_limit_usd:.2f} (80%)")
        
        # Tägliche Nutzung prüfen
        today = datetime.now().date()
        today_calls = [
            call for call in self.usage_data.get("api_calls", [])
            if datetime.fromisoformat(call["timestamp"]).date() == today
        ]
        
        if len(today_calls) > 50:
            alerts.append(f"⚠️ Hohe tägliche Nutzung: {len(today_calls)} API-Calls heute")
        
        return alerts 