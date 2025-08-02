#!/usr/bin/env python3
"""
One Click Book Writer - GUI Application
Moderne Benutzeroberfläche mit CustomTkinter
"""

import customtkinter as ctk
import json
import os
import sys
import threading
from pathlib import Path
from tkinter import messagebox, filedialog
from typing import Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from compiler.prompt_compiler import compile_prompt, compile_prompt_for_chatgpt, get_prompt_metadata
from schema.validate_input import validate_json_schema, validate_prompt_frame_structure


class OneClickBookWriterGUI:
    """Hauptfenster der One Click Book Writer Anwendung."""
    
    def __init__(self):
        """Initialisiert die GUI-Anwendung."""
        # CustomTkinter Setup
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Hauptfenster
        self.root = ctk.CTk()
        self.root.title("One Click Book Writer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Variablen
        self.current_prompt_frame = None
        self.available_engines = ["claude", "chatgpt"]
        self.selected_engine = ctk.StringVar(value="claude")
        self.temperature = ctk.DoubleVar(value=0.4)
        self.max_tokens = ctk.IntVar(value=8000)
        
        # GUI erstellen
        self.create_widgets()
        self.load_example_data()
        
    def create_widgets(self):
        """Erstellt alle GUI-Widgets."""
        # Hauptcontainer
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🚀 One Click Book Writer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Notebook für Tabs
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Eingabe
        self.create_input_tab()
        
        # Tab 2: Prompt-Vorschau
        self.create_preview_tab()
        
        # Tab 3: Generierung
        self.create_generation_tab()
        
        # Tab 4: Ergebnisse
        self.create_results_tab()
        
        # Status Bar
        self.status_label = ctk.CTkLabel(main_frame, text="Bereit")
        self.status_label.pack(pady=5)
        
    def create_input_tab(self):
        """Erstellt den Eingabe-Tab."""
        input_tab = self.notebook.add("📝 Eingabe")
        
        # Linke Seite - JSON Editor
        left_frame = ctk.CTkFrame(input_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(left_frame, text="JSON PromptFrame", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # JSON Text Area
        self.json_text = ctk.CTkTextbox(left_frame, font=ctk.CTkFont(family="monospace", size=12))
        self.json_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # JSON Buttons
        json_buttons_frame = ctk.CTkFrame(left_frame)
        json_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(json_buttons_frame, text="📁 Laden", command=self.load_json_file).pack(side="left", padx=5)
        ctk.CTkButton(json_buttons_frame, text="💾 Speichern", command=self.save_json_file).pack(side="left", padx=5)
        ctk.CTkButton(json_buttons_frame, text="✅ Validieren", command=self.validate_json).pack(side="left", padx=5)
        
        # Rechte Seite - Formular
        right_frame = ctk.CTkFrame(input_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(right_frame, text="Schnelleingabe", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Scrollable Frame für Formular
        form_frame = ctk.CTkScrollableFrame(right_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Kapitel-Informationen
        ctk.CTkLabel(form_frame, text="Kapitel", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        chapter_frame = ctk.CTkFrame(form_frame)
        chapter_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(chapter_frame, text="Nummer:").pack(anchor="w", padx=10, pady=2)
        self.chapter_number = ctk.CTkEntry(chapter_frame, placeholder_text="1")
        self.chapter_number.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(chapter_frame, text="Titel:").pack(anchor="w", padx=10, pady=2)
        self.chapter_title = ctk.CTkEntry(chapter_frame, placeholder_text="Der erste Flug")
        self.chapter_title.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(chapter_frame, text="Zweck:").pack(anchor="w", padx=10, pady=2)
        self.chapter_purpose = ctk.CTkEntry(chapter_frame, placeholder_text="Einführung der Hauptfigur")
        self.chapter_purpose.pack(fill="x", padx=10, pady=2)
        
        # Buch-Informationen
        ctk.CTkLabel(form_frame, text="Buch", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        book_frame = ctk.CTkFrame(form_frame)
        book_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(book_frame, text="Titel:").pack(anchor="w", padx=10, pady=2)
        self.book_title = ctk.CTkEntry(book_frame, placeholder_text="Die Abenteuer des kleinen Drachen")
        self.book_title.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(book_frame, text="Genre:").pack(anchor="w", padx=10, pady=2)
        self.book_genre = ctk.CTkEntry(book_frame, placeholder_text="Kinderbuch")
        self.book_genre.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(book_frame, text="Zielgruppe:").pack(anchor="w", padx=10, pady=2)
        self.target_audience = ctk.CTkEntry(book_frame, placeholder_text="Kinder im Alter von 6-10 Jahren")
        self.target_audience.pack(fill="x", padx=10, pady=2)
        
        # Story-Kontext
        ctk.CTkLabel(form_frame, text="Story-Kontext", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        context_frame = ctk.CTkFrame(form_frame)
        context_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(context_frame, text="Aktuelle Szene:").pack(anchor="w", padx=10, pady=2)
        self.current_scene = ctk.CTkTextbox(context_frame, height=60)
        self.current_scene.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(context_frame, text="Vorherige Zusammenfassung:").pack(anchor="w", padx=10, pady=2)
        self.previous_summary = ctk.CTkTextbox(context_frame, height=60)
        self.previous_summary.pack(fill="x", padx=10, pady=2)
        
        # Formular zu JSON Button
        ctk.CTkButton(form_frame, text="🔄 Formular zu JSON", command=self.form_to_json).pack(pady=10)
        
    def create_preview_tab(self):
        """Erstellt den Prompt-Vorschau-Tab."""
        preview_tab = self.notebook.add("👁️ Prompt-Vorschau")
        
        # Engine-Auswahl
        engine_frame = ctk.CTkFrame(preview_tab)
        engine_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(engine_frame, text="AI-Engine:").pack(side="left", padx=10)
        
        for engine in self.available_engines:
            ctk.CTkRadioButton(
                engine_frame, 
                text=engine.title(), 
                variable=self.selected_engine, 
                value=engine,
                command=self.update_preview
            ).pack(side="left", padx=10)
        
        # Prompt-Vorschau
        preview_frame = ctk.CTkFrame(preview_tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(preview_frame, text="Kompilierter Prompt", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.preview_text = ctk.CTkTextbox(preview_frame, font=ctk.CTkFont(family="monospace", size=11))
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Metadaten
        metadata_frame = ctk.CTkFrame(preview_tab)
        metadata_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(metadata_frame, text="Metadaten", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.metadata_text = ctk.CTkTextbox(metadata_frame, height=100, font=ctk.CTkFont(family="monospace", size=10))
        self.metadata_text.pack(fill="x", padx=10, pady=10)
        
    def create_generation_tab(self):
        """Erstellt den Generierungs-Tab."""
        generation_tab = self.notebook.add("⚡ Generierung")
        
        # Parameter
        params_frame = ctk.CTkFrame(generation_tab)
        params_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(params_frame, text="Generierungsparameter", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Temperature
        temp_frame = ctk.CTkFrame(params_frame)
        temp_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(temp_frame, text="Temperature:").pack(side="left", padx=10)
        temp_slider = ctk.CTkSlider(temp_frame, from_=0.0, to=1.0, variable=self.temperature, number_of_steps=20)
        temp_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.temp_label = ctk.CTkLabel(temp_frame, text="0.4")
        self.temp_label.pack(side="right", padx=10)
        temp_slider.configure(command=self.update_temp_label)
        
        # Max Tokens
        tokens_frame = ctk.CTkFrame(params_frame)
        tokens_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(tokens_frame, text="Max Tokens:").pack(side="left", padx=10)
        tokens_slider = ctk.CTkSlider(tokens_frame, from_=1000, to=8000, variable=self.max_tokens, number_of_steps=70)
        tokens_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.tokens_label = ctk.CTkLabel(tokens_frame, text="8000")
        self.tokens_label.pack(side="right", padx=10)
        tokens_slider.configure(command=self.update_tokens_label)
        
        # Generierungs-Buttons
        buttons_frame = ctk.CTkFrame(generation_tab)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        self.generate_button = ctk.CTkButton(
            buttons_frame, 
            text="🚀 Kapitel generieren", 
            command=self.generate_chapter,
            height=40
        )
        self.generate_button.pack(side="left", padx=5)
        
        self.batch_button = ctk.CTkButton(
            buttons_frame, 
            text="📚 Batch-Generierung", 
            command=self.open_batch_window,
            height=40
        )
        self.batch_button.pack(side="left", padx=5)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(generation_tab)
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)
        
        # Status
        self.generation_status = ctk.CTkLabel(generation_tab, text="Bereit zur Generierung")
        self.generation_status.pack(pady=5)
        
    def create_results_tab(self):
        """Erstellt den Ergebnisse-Tab."""
        results_tab = self.notebook.add("📖 Ergebnisse")
        
        # Ergebnis-Text
        result_frame = ctk.CTkFrame(results_tab)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(result_frame, text="Generierter Text", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.result_text = ctk.CTkTextbox(result_frame, font=ctk.CTkFont(size=12))
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Ergebnis-Buttons
        result_buttons_frame = ctk.CTkFrame(results_tab)
        result_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(result_buttons_frame, text="💾 Speichern", command=self.save_result).pack(side="left", padx=5)
        ctk.CTkButton(result_buttons_frame, text="📁 Ordner öffnen", command=self.open_output_folder).pack(side="left", padx=5)
        ctk.CTkButton(result_buttons_frame, text="🗑️ Löschen", command=self.clear_result).pack(side="left", padx=5)
        
    def load_example_data(self):
        """Lädt Beispieldaten."""
        try:
            with open("data/generate_chapter_full_extended.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.json_text.delete("1.0", "end")
                self.json_text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
                self.current_prompt_frame = data
                self.update_preview()
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Beispieldaten: {e}")
    
    def load_json_file(self):
        """Lädt eine JSON-Datei."""
        file_path = filedialog.askopenfilename(
            title="JSON-Datei auswählen",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.json_text.delete("1.0", "end")
                    self.json_text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
                    self.current_prompt_frame = data
                    self.update_preview()
                    self.status_label.configure(text=f"Datei geladen: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")
    
    def save_json_file(self):
        """Speichert die JSON-Daten."""
        file_path = filedialog.asksaveasfilename(
            title="JSON-Datei speichern",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                data = json.loads(self.json_text.get("1.0", "end"))
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.status_label.configure(text=f"Datei gespeichert: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def validate_json(self):
        """Validiert die JSON-Daten."""
        try:
            data = json.loads(self.json_text.get("1.0", "end"))
            
            # Strukturvalidierung
            if not validate_prompt_frame_structure(data):
                messagebox.showerror("Validierungsfehler", "Strukturvalidierung fehlgeschlagen")
                return
            
            # Schema-Validierung
            if not validate_json_schema(data, "schema/prompt_frame.schema.json"):
                messagebox.showerror("Validierungsfehler", "Schema-Validierung fehlgeschlagen")
                return
            
            self.current_prompt_frame = data
            self.update_preview()
            messagebox.showinfo("Erfolg", "JSON-Daten sind gültig!")
            self.status_label.configure(text="JSON validiert")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON-Fehler", f"Ungültige JSON-Syntax: {e}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Validierungsfehler: {e}")
    
    def form_to_json(self):
        """Konvertiert das Formular zu JSON."""
        try:
            data = {
                "input": {
                    "chapter": {
                        "number": int(self.chapter_number.get() or "1"),
                        "title": self.chapter_title.get() or "Unbekanntes Kapitel",
                        "narrative_purpose": self.chapter_purpose.get() or "Kapitel-Zweck",
                        "position_in_arc": "setup",
                        "length_words": 800
                    },
                    "book": {
                        "title": self.book_title.get() or "Unbekanntes Buch",
                        "genre": self.book_genre.get() or "Allgemein",
                        "target_audience": self.target_audience.get() or "Allgemein"
                    },
                    "style": {
                        "writing_style": "descriptive",
                        "tone": "warm",
                        "tense": "past",
                        "perspective": "third_limited",
                        "sentence_complexity": "simple"
                    },
                    "story_context": {
                        "current_scene": self.current_scene.get("1.0", "end").strip(),
                        "previous_summary": self.previous_summary.get("1.0", "end").strip()
                    },
                    "constraints": {
                        "structure": "linear",
                        "format": "prose",
                        "stylistic_dos": ["Verwende einfache Sätze"],
                        "forbidden_elements": ["Gewalt"]
                    }
                }
            }
            
            self.json_text.delete("1.0", "end")
            self.json_text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
            self.current_prompt_frame = data
            self.update_preview()
            self.status_label.configure(text="Formular zu JSON konvertiert")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Konvertierung: {e}")
    
    def update_preview(self):
        """Aktualisiert die Prompt-Vorschau."""
        if not self.current_prompt_frame:
            return
        
        try:
            # Prompt kompilieren
            engine = self.selected_engine.get()
            if engine == "chatgpt":
                prompt = compile_prompt_for_chatgpt(self.current_prompt_frame)
            else:
                prompt = compile_prompt(self.current_prompt_frame)
            
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", prompt)
            
            # Metadaten anzeigen
            metadata = get_prompt_metadata(self.current_prompt_frame)
            self.metadata_text.delete("1.0", "end")
            self.metadata_text.insert("1.0", json.dumps(metadata, indent=2, ensure_ascii=False))
            
        except Exception as e:
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", f"Fehler beim Kompilieren: {e}")
    
    def update_temp_label(self, value):
        """Aktualisiert das Temperature-Label."""
        self.temp_label.configure(text=f"{value:.1f}")
    
    def update_tokens_label(self, value):
        """Aktualisiert das Tokens-Label."""
        self.tokens_label.configure(text=str(int(value)))
    
    def generate_chapter(self):
        """Generiert ein Kapitel."""
        if not self.current_prompt_frame:
            messagebox.showerror("Fehler", "Keine gültigen Daten zum Generieren")
            return
        
        # In separatem Thread ausführen
        thread = threading.Thread(target=self._generate_chapter_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_chapter_thread(self):
        """Generiert ein Kapitel in einem separaten Thread."""
        try:
            self.generate_button.configure(state="disabled")
            self.generation_status.configure(text="Generiere Kapitel...")
            self.progress_bar.set(0.2)
            
            # Simulierte Generierung (ohne API-Keys)
            engine = self.selected_engine.get()
            
            # Prompt kompilieren
            if engine == "chatgpt":
                prompt = compile_prompt_for_chatgpt(self.current_prompt_frame)
            else:
                prompt = compile_prompt(self.current_prompt_frame)
            
            self.progress_bar.set(0.5)
            
            # Simulierte Antwort
            metadata = get_prompt_metadata(self.current_prompt_frame)
            simulated_text = f"""Kapitel {metadata['chapter_number']}: {metadata['chapter_title']}

Feuerherz stand am Rande der gemütlichen Drachenhöhle und schaute sehnsüchtig in die Ferne. Die warme Morgensonne kitzelte seine grünen Schuppen, während er die anderen Drachen beobachtete, die elegant durch die Lüfte tanzten. Seine kleinen Flügel zitterten vor Aufregung.

"Du schaffst das, mein Kleiner", flüsterte Mama Drache sanft und strich ihm mit ihrer warmen Schnauze über den Kopf. "Jeder Drache muss irgendwann seinen ersten Flug wagen."

Papa Drache nickte stolz. "Heute ist dein Tag, Feuerherz. Du bist bereit."

Feuerherz atmete tief ein. Angst und Aufregung kämpften in seinem kleinen Drachenherzen. Er spürte, wie sein Mut wuchs, während er sich langsam zum Abgrund bewegte.

"Du bist ein Drache", sagte er sich selbst. "Du kannst fliegen."

Mit einem letzten tiefen Atemzug sprang Feuerherz in die Luft. Für einen Moment fühlte er sich schwerelos, dann begannen seine Flügel zu schlagen. Zuerst unsicher, dann immer sicherer, bis er schließlich elegant durch die Lüfte glitt.

"Du fliegst!", rief Mama Drache begeistert.

Feuerherz jubelte innerlich. Er war endlich ein echter Drache!"""
            
            self.progress_bar.set(0.8)
            
            # Ergebnis anzeigen
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", simulated_text)
            
            # Ergebnis speichern
            self.save_generated_result(simulated_text, metadata, engine)
            
            self.progress_bar.set(1.0)
            self.generation_status.configure(text="Kapitel erfolgreich generiert!")
            self.status_label.configure(text=f"Kapitel mit {engine} generiert")
            
            # Zum Ergebnisse-Tab wechseln
            self.notebook.set("📖 Ergebnisse")
            
        except Exception as e:
            self.generation_status.configure(text=f"Fehler: {e}")
            messagebox.showerror("Generierungsfehler", str(e))
        finally:
            self.generate_button.configure(state="normal")
    
    def save_generated_result(self, text: str, metadata: Dict[str, Any], engine: str):
        """Speichert das generierte Ergebnis."""
        try:
            os.makedirs("output/chapters", exist_ok=True)
            
            # Text speichern
            output_filename = f"chapter_{metadata['chapter_number']}_{metadata['chapter_title'].replace(' ', '_').lower()}.txt"
            output_path = f"output/chapters/{output_filename}"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Metadaten speichern
            metadata_filename = output_filename.replace(".txt", "_metadata.json")
            metadata_path = f"output/chapters/{metadata_filename}"
            
            result_metadata = {
                "text_length": len(text),
                "model": f"{engine}-simulated",
                "engine": engine,
                "usage": {
                    "input_tokens": 450,
                    "output_tokens": 320,
                    "total_tokens": 770
                },
                "finish_reason": "stop",
                "metadata": {
                    "temperature": self.temperature.get(),
                    "max_tokens": self.max_tokens.get()
                },
                "prompt_metadata": metadata
            }
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(result_metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def open_batch_window(self):
        """Öffnet das Batch-Generierungs-Fenster."""
        BatchWindow(self.root, self.current_prompt_frame)
    
    def save_result(self):
        """Speichert das aktuelle Ergebnis."""
        text = self.result_text.get("1.0", "end")
        if not text.strip():
            messagebox.showwarning("Warnung", "Kein Text zum Speichern vorhanden")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Ergebnis speichern",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.status_label.configure(text=f"Ergebnis gespeichert: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def open_output_folder(self):
        """Öffnet den Ausgabe-Ordner."""
        import subprocess
        try:
            subprocess.run(["open", "output/chapters"])
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Ordners: {e}")
    
    def clear_result(self):
        """Löscht das aktuelle Ergebnis."""
        if messagebox.askyesno("Bestätigung", "Möchten Sie das aktuelle Ergebnis löschen?"):
            self.result_text.delete("1.0", "end")
            self.status_label.configure(text="Ergebnis gelöscht")
    
    def run(self):
        """Startet die GUI-Anwendung."""
        self.root.mainloop()


class BatchWindow:
    """Fenster für Batch-Generierung."""
    
    def __init__(self, parent, base_prompt_frame):
        """Initialisiert das Batch-Fenster."""
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Batch-Generierung")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.base_prompt_frame = base_prompt_frame
        
        self.create_widgets()
    
    def create_widgets(self):
        """Erstellt die Widgets für das Batch-Fenster."""
        # Hauptframe
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text="📚 Batch-Generierung", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Einstellungen
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(settings_frame, text="Einstellungen", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Anzahl Kapitel
        chapters_frame = ctk.CTkFrame(settings_frame)
        chapters_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(chapters_frame, text="Anzahl Kapitel:").pack(side="left", padx=10)
        self.chapters_count = ctk.CTkEntry(chapters_frame, placeholder_text="5")
        self.chapters_count.pack(side="left", padx=10)
        
        # Start-Kapitel
        start_frame = ctk.CTkFrame(settings_frame)
        start_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(start_frame, text="Start-Kapitel:").pack(side="left", padx=10)
        self.start_chapter = ctk.CTkEntry(start_frame, placeholder_text="1")
        self.start_chapter.pack(side="left", padx=10)
        
        # Engine
        engine_frame = ctk.CTkFrame(settings_frame)
        engine_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(engine_frame, text="Engine:").pack(side="left", padx=10)
        self.batch_engine = ctk.StringVar(value="claude")
        
        for engine in ["claude", "chatgpt"]:
            ctk.CTkRadioButton(
                engine_frame, 
                text=engine.title(), 
                variable=self.batch_engine, 
                value=engine
            ).pack(side="left", padx=10)
        
        # Start-Button
        ctk.CTkButton(
            main_frame, 
            text="🚀 Batch starten", 
            command=self.start_batch,
            height=40
        ).pack(pady=20)
        
        # Progress
        self.batch_progress = ctk.CTkProgressBar(main_frame)
        self.batch_progress.pack(fill="x", padx=10, pady=10)
        self.batch_progress.set(0)
        
        # Status
        self.batch_status = ctk.CTkLabel(main_frame, text="Bereit für Batch-Generierung")
        self.batch_status.pack(pady=5)
    
    def start_batch(self):
        """Startet die Batch-Generierung."""
        try:
            count = int(self.chapters_count.get() or "1")
            start = int(self.start_chapter.get() or "1")
            engine = self.batch_engine.get()
            
            if count < 1 or count > 20:
                messagebox.showerror("Fehler", "Anzahl Kapitel muss zwischen 1 und 20 liegen")
                return
            
            # Batch in separatem Thread starten
            thread = threading.Thread(target=self._batch_thread, args=(count, start, engine))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Zahlen für Kapitel-Anzahl oder Start-Kapitel")
    
    def _batch_thread(self, count: int, start: int, engine: str):
        """Führt die Batch-Generierung in einem separaten Thread aus."""
        try:
            self.batch_status.configure(text="Batch-Generierung läuft...")
            
            for i in range(count):
                chapter_num = start + i
                
                # PromptFrame für aktuelles Kapitel erstellen
                prompt_frame = self._create_chapter_prompt_frame(chapter_num)
                
                # Kapitel generieren (simuliert)
                metadata = get_prompt_metadata(prompt_frame)
                simulated_text = f"""Kapitel {metadata['chapter_number']}: {metadata['chapter_title']}

Dies ist ein simuliertes Kapitel {chapter_num} für die Batch-Generierung mit {engine}.

Feuerherz setzte seine Abenteuer fort und lernte neue Dinge über das Fliegen und die Welt um ihn herum. Jedes Kapitel brachte neue Herausforderungen und Erkenntnisse.

"Du wirst immer besser", sagte Mama Drache stolz.

Feuerherz nickte und fühlte sich stärker als je zuvor."""
                
                # Ergebnis speichern
                self._save_batch_result(simulated_text, metadata, engine, i+1)
                
                # Progress aktualisieren
                progress = (i + 1) / count
                self.batch_progress.set(progress)
                self.batch_status.configure(text=f"Kapitel {i+1}/{count} generiert")
            
            self.batch_status.configure(text="Batch-Generierung abgeschlossen!")
            messagebox.showinfo("Erfolg", f"{count} Kapitel erfolgreich generiert!")
            
        except Exception as e:
            self.batch_status.configure(text=f"Fehler: {e}")
            messagebox.showerror("Batch-Fehler", str(e))
    
    def _create_chapter_prompt_frame(self, chapter_num: int) -> Dict[str, Any]:
        """Erstellt ein PromptFrame für ein spezifisches Kapitel."""
        if not self.base_prompt_frame:
            raise ValueError("Kein Basis-PromptFrame verfügbar")
        
        # Basis-PromptFrame kopieren
        prompt_frame = json.loads(json.dumps(self.base_prompt_frame))
        
        # Kapitel-Nummer anpassen
        prompt_frame["input"]["chapter"]["number"] = chapter_num
        prompt_frame["input"]["chapter"]["title"] = f"Kapitel {chapter_num}"
        
        return prompt_frame
    
    def _save_batch_result(self, text: str, metadata: Dict[str, Any], engine: str, batch_num: int):
        """Speichert ein Batch-Ergebnis."""
        try:
            os.makedirs("output/chapters", exist_ok=True)
            
            # Text speichern
            output_filename = f"batch_{batch_num}_chapter_{metadata['chapter_number']}.txt"
            output_path = f"output/chapters/{output_filename}"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Metadaten speichern
            metadata_filename = output_filename.replace(".txt", "_metadata.json")
            metadata_path = f"output/chapters/{metadata_filename}"
            
            result_metadata = {
                "text_length": len(text),
                "model": f"{engine}-simulated",
                "engine": engine,
                "batch_number": batch_num,
                "usage": {
                    "input_tokens": 450,
                    "output_tokens": 320,
                    "total_tokens": 770
                },
                "finish_reason": "stop",
                "prompt_metadata": metadata
            }
            
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(result_metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Fehler beim Speichern des Batch-Ergebnisses: {e}")


def main():
    """Hauptfunktion für die GUI-Anwendung."""
    app = OneClickBookWriterGUI()
    app.run()


if __name__ == "__main__":
    main() 