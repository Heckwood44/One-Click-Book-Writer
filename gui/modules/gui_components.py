#!/usr/bin/env python3
"""
GUI Components Module
Modulare GUI-Komponenten für One Click Book Writer
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, Any, Optional, Callable
import logging
import json
from core.validation import validate_prompt_frame, validate_feedback, validate_api_request, sanitize_input
from core.security import secure_log

logger = logging.getLogger(__name__)

class ChapterTab:
    """Kapitel-Generierung Tab"""
    
    def __init__(self, parent: ttk.Notebook, api_client: Any) -> None:
        """
        Initialisiert den Chapter Tab
        
        Args:
            parent: Parent Notebook
            api_client: API Client für Generierung
        """
        self.parent = parent
        self.api_client = api_client
        self.tab = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # JSON Input
        input_frame = ttk.LabelFrame(main_frame, text="JSON Input", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.json_text = scrolledtext.ScrolledText(input_frame, height=15, width=80)
        self.json_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Beispiel laden", command=self.load_example).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="JSON validieren", command=self.validate_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Prompt aktualisieren", command=self.update_prompt).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Kapitel generieren", command=self.generate_chapter).pack(side=tk.LEFT, padx=(0, 5))
        
        # Output
        output_frame = ttk.LabelFrame(main_frame, text="Generiertes Kapitel", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def load_example(self) -> None:
        """Lädt Beispiel-JSON"""
        try:
            example_data = self._get_example_data()
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(1.0, example_data)
            secure_log("Beispiel-JSON geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden des Beispiels: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden des Beispiels: {e}")
    
    def validate_json(self) -> None:
        """Validiert JSON-Input"""
        try:
            json_str = self.json_text.get(1.0, tk.END).strip()
            if not json_str:
                messagebox.showwarning("Warnung", "Bitte gib JSON-Daten ein")
                return
            
            # Parse JSON
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON Parse-Fehler: {e}")
                messagebox.showerror("Fehler", f"JSON Parse-Fehler: {e}")
                return
            
            # Validiere mit Pydantic
            validation_result = validate_prompt_frame(data)
            
            if validation_result.valid:
                messagebox.showinfo("Erfolg", "JSON ist gültig!")
                if validation_result.warnings:
                    warning_msg = "Warnungen:\n" + "\n".join(validation_result.warnings)
                    messagebox.showwarning("Warnungen", warning_msg)
                secure_log("JSON erfolgreich validiert")
            else:
                error_msg = "Validierungsfehler:\n" + "\n".join(validation_result.errors)
                logger.error(f"JSON Validierungsfehler: {validation_result.errors}")
                messagebox.showerror("Fehler", error_msg)
                
        except Exception as e:
            logger.exception(f"Unerwarteter Fehler bei JSON-Validierung: {e}")
            messagebox.showerror("Fehler", f"Unerwarteter Fehler: {e}")
    
    def update_prompt(self) -> None:
        """Aktualisiert den Prompt"""
        try:
            # Validiere zuerst JSON
            json_str = self.json_text.get(1.0, tk.END).strip()
            if not json_str:
                messagebox.showwarning("Warnung", "Bitte gib JSON-Daten ein")
                return
            
            data = json.loads(json_str)
            validation_result = validate_prompt_frame(data)
            
            if not validation_result.valid:
                error_msg = "Validierungsfehler:\n" + "\n".join(validation_result.errors)
                messagebox.showerror("Fehler", error_msg)
                return
            
            # Hier würde die Prompt-Aktualisierung implementiert
            secure_log("Prompt aktualisiert")
            messagebox.showinfo("Info", "Prompt aktualisiert")
        except Exception as e:
            logger.exception(f"Fehler bei Prompt-Aktualisierung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Prompt-Aktualisierung: {e}")
    
    def generate_chapter(self) -> None:
        """Generiert ein Kapitel"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            json_str = self.json_text.get(1.0, tk.END).strip()
            if not json_str:
                messagebox.showwarning("Warnung", "Bitte gib JSON-Daten ein")
                return
            
            # Validiere JSON
            data = json.loads(json_str)
            validation_result = validate_prompt_frame(data)
            
            if not validation_result.valid:
                error_msg = "Validierungsfehler:\n" + "\n".join(validation_result.errors)
                messagebox.showerror("Fehler", error_msg)
                return
            
            # Validiere API Request
            api_request_data = {
                "prompt_frame": {"input": data},
                "engine": "claude",
                "temperature": 0.4,
                "max_tokens": 8000
            }
            
            api_validation = validate_api_request(api_request_data)
            if not api_validation.valid:
                error_msg = "API Request Validierungsfehler:\n" + "\n".join(api_validation.errors)
                messagebox.showerror("Fehler", error_msg)
                return
            
            # Hier würde die Kapitel-Generierung implementiert
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, "Generiertes Kapitel würde hier erscheinen...")
            secure_log("Kapitel-Generierung gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei Kapitel-Generierung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Kapitel-Generierung: {e}")
    
    def _get_example_data(self) -> str:
        """Gibt Beispiel-JSON zurück"""
        return '''{
  "input": {
    "book": {
      "title": "Die magische Reise",
      "genre": "fantasy",
      "target_audience": "early_reader",
      "theme": "Mut und Selbstvertrauen",
      "setting": "Ein verzauberter Wald",
      "language_variants": ["de", "en"],
      "bilingual_sequence": ["de", "en"]
    },
    "chapter": {
      "number": 1,
      "title": "Der Anfang der Reise",
      "narrative_purpose": "Einführung der Hauptfigur",
      "position_in_arc": "setup",
      "length_words": 800,
      "language_variants": ["de", "en"],
      "bilingual_sequence": ["de", "en"]
    }
  }
}'''

class StoryTab:
    """Story-Entwicklung Tab"""
    
    def __init__(self, parent: ttk.Notebook, api_client: Any) -> None:
        """
        Initialisiert den Story Tab
        
        Args:
            parent: Parent Notebook
            api_client: API Client für Story-Entwicklung
        """
        self.parent = parent
        self.api_client = api_client
        self.tab = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Story-Idee", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.story_context_text = scrolledtext.ScrolledText(input_frame, height=8, width=80)
        self.story_context_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Story-Struktur", command=self.get_story_structure).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Emotionale Tiefe", command=self.optimize_emotional_depth).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Plot entwickeln", command=self.develop_plot).pack(side=tk.LEFT, padx=(0, 5))
        
        # Output Frame
        output_frame = ttk.LabelFrame(main_frame, text="Story-Entwicklung", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.story_results_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.story_results_text.pack(fill=tk.BOTH, expand=True)
    
    def get_story_structure(self) -> None:
        """Analysiert Story-Struktur"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            context = self.story_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Story-Idee ein")
                return
            
            # Bereinige Input
            sanitized_context = sanitize_input(context)
            if sanitized_context != context:
                logger.warning("Input wurde bereinigt")
            
            # Hier würde die Story-Struktur-Analyse implementiert
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, "Story-Struktur-Analyse würde hier erscheinen...")
            secure_log("Story-Struktur-Analyse gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei Story-Struktur-Analyse: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Story-Struktur-Analyse: {e}")
    
    def optimize_emotional_depth(self) -> None:
        """Optimiert emotionale Tiefe"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            context = self.story_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Story-Idee ein")
                return
            
            # Bereinige Input
            sanitized_context = sanitize_input(context)
            
            # Hier würde die emotionale Optimierung implementiert
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, "Emotionale Optimierung würde hier erscheinen...")
            secure_log("Emotionale Optimierung gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei emotionaler Optimierung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei emotionaler Optimierung: {e}")
    
    def develop_plot(self) -> None:
        """Entwickelt den Plot"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            context = self.story_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Story-Idee ein")
                return
            
            # Bereinige Input
            sanitized_context = sanitize_input(context)
            
            # Hier würde die Plot-Entwicklung implementiert
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, "Plot-Entwicklung würde hier erscheinen...")
            secure_log("Plot-Entwicklung gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei Plot-Entwicklung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Plot-Entwicklung: {e}")

class CharacterTab:
    """Charakter-Entwicklung Tab"""
    
    def __init__(self, parent: ttk.Notebook, api_client: Any) -> None:
        """
        Initialisiert den Character Tab
        
        Args:
            parent: Parent Notebook
            api_client: API Client für Charakter-Entwicklung
        """
        self.parent = parent
        self.api_client = api_client
        self.tab = ttk.Frame(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Erstellt die UI-Komponenten"""
        # Hauptframe
        main_frame = ttk.Frame(self.tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Charakter-Beschreibung", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.character_context_text = scrolledtext.ScrolledText(input_frame, height=8, width=80)
        self.character_context_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Charakter entwickeln", command=self.develop_character).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Dialog optimieren", command=self.optimize_dialogue).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Charakter-Entwicklung", command=self.character_arc).pack(side=tk.LEFT, padx=(0, 5))
        
        # Output Frame
        output_frame = ttk.LabelFrame(main_frame, text="Charakter-Entwicklung", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.character_results_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.character_results_text.pack(fill=tk.BOTH, expand=True)
    
    def develop_character(self) -> None:
        """Entwickelt Charaktere"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            context = self.character_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Charakter-Beschreibung ein")
                return
            
            # Bereinige Input
            sanitized_context = sanitize_input(context)
            
            # Hier würde die Charakter-Entwicklung implementiert
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, "Charakter-Entwicklung würde hier erscheinen...")
            secure_log("Charakter-Entwicklung gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei Charakter-Entwicklung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Charakter-Entwicklung: {e}")
    
    def optimize_dialogue(self) -> None:
        """Optimiert Dialoge"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            context = self.character_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Charakter-Beschreibung ein")
                return
            
            # Bereinige Input
            sanitized_context = sanitize_input(context)
            
            # Hier würde die Dialog-Optimierung implementiert
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, "Dialog-Optimierung würde hier erscheinen...")
            secure_log("Dialog-Optimierung gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei Dialog-Optimierung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Dialog-Optimierung: {e}")
    
    def character_arc(self) -> None:
        """Entwickelt Charakter-Entwicklung"""
        try:
            if not self.api_client.is_claude_available():
                messagebox.showerror("Fehler", "Claude API Key fehlt")
                return
            
            context = self.character_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Charakter-Beschreibung ein")
                return
            
            # Bereinige Input
            sanitized_context = sanitize_input(context)
            
            # Hier würde die Charakter-Entwicklung implementiert
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, "Charakter-Entwicklung würde hier erscheinen...")
            secure_log("Charakter-Entwicklung gestartet")
        except Exception as e:
            logger.exception(f"Fehler bei Charakter-Entwicklung: {e}")
            messagebox.showerror("Fehler", f"Fehler bei Charakter-Entwicklung: {e}") 