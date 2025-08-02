#!/usr/bin/env python3
"""
One Click Book Writer - Enhanced GUI
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
import threading
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from prompt_router import PromptRouter
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

class EnhancedBookWriterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("One Click Book Writer - Enhanced GUI v2.0")
        self.root.geometry("1600x1000")
        
        # Router initialisieren
        self.router = PromptRouter()
        
        # API Keys prüfen
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Status-Variablen
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit - Lade Template...")
        
        # UI aufbauen
        self.setup_ui()
        
        # Beispiel-Template laden
        self.load_template()
        
    def setup_ui(self):
        """Baut die Benutzeroberfläche auf"""
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid-Konfiguration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Titel
        title_label = ttk.Label(main_frame, text="One Click Book Writer - Enhanced GUI", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Linke Spalte - Eingabe
        input_frame = ttk.LabelFrame(main_frame, text="JSON Template", padding="5")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        # Template-Auswahl
        template_frame = ttk.Frame(input_frame)
        template_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(template_frame, text="Template:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar(value="Fantasy")
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, 
                                     values=["Fantasy", "Abenteuer", "Krimi", "Science Fiction"],
                                     state="readonly", width=15)
        template_combo.pack(side=tk.LEFT, padx=(5, 0))
        template_combo.bind("<<ComboboxSelected>>", self.on_template_change)
        
        # JSON-Editor
        self.json_text = scrolledtext.ScrolledText(input_frame, width=50, height=30, 
                                                  font=("Consolas", 10))
        self.json_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons für JSON
        json_buttons_frame = ttk.Frame(input_frame)
        json_buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(json_buttons_frame, text="Laden", command=self.load_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_buttons_frame, text="Speichern", command=self.save_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_buttons_frame, text="Validieren", command=self.validate_json).pack(side=tk.LEFT)
        
        # Mittlere Spalte - Steuerung
        control_frame = ttk.LabelFrame(main_frame, text="Pipeline-Steuerung", padding="5")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        control_frame.columnconfigure(0, weight=1)
        
        # Kapitel-Nummer
        chapter_frame = ttk.Frame(control_frame)
        chapter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(chapter_frame, text="Kapitel:").pack(side=tk.LEFT)
        self.chapter_var = tk.IntVar(value=1)
        chapter_spin = ttk.Spinbox(chapter_frame, from_=1, to=50, textvariable=self.chapter_var, width=10)
        chapter_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Claude-Optimierung
        self.claude_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Claude-Optimierung", variable=self.claude_var).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Generierungs-Button
        self.generate_button = ttk.Button(control_frame, text="Kapitel Generieren", 
                                         command=self.generate_chapter, style="Accent.TButton")
        self.generate_button.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Batch-Generierung
        ttk.Button(control_frame, text="Batch-Generierung (3 Kapitel)", 
                  command=self.batch_generation).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # API-Keys konfigurieren
        ttk.Button(control_frame, text="API-Keys konfigurieren", 
                  command=self.configure_api_keys).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status
        status_frame = ttk.LabelFrame(control_frame, text="Status", padding="5")
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        self.status_display = scrolledtext.ScrolledText(status_frame, width=30, height=10, 
                                                       font=("Consolas", 9))
        self.status_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Rechte Spalte - Ergebnisse
        results_frame = ttk.LabelFrame(main_frame, text="Generierte Kapitel", padding="5")
        results_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Ergebnis-Tabs
        self.result_notebook = ttk.Notebook(results_frame)
        self.result_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Deutsche Version
        self.de_text = scrolledtext.ScrolledText(self.result_notebook, width=50, height=25, 
                                                font=("Arial", 11))
        self.result_notebook.add(self.de_text, text="Deutsch")
        
        # Englische Version
        self.en_text = scrolledtext.ScrolledText(self.result_notebook, width=50, height=25, 
                                                font=("Arial", 11))
        self.result_notebook.add(self.en_text, text="English")
        
        # Metadaten
        self.meta_text = scrolledtext.ScrolledText(self.result_notebook, width=50, height=25, 
                                                  font=("Consolas", 9))
        self.result_notebook.add(self.meta_text, text="Metadaten")
        
        # Buttons für Ergebnisse
        result_buttons_frame = ttk.Frame(results_frame)
        result_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(result_buttons_frame, text="Alle speichern", 
                  command=self.save_all_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(result_buttons_frame, text="Metadaten anzeigen", 
                  command=self.show_metadata).pack(side=tk.LEFT)
        
        # Status-Bar
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def load_template(self):
        """Lädt ein Template basierend auf der Auswahl"""
        template = self.template_var.get()
        template_file = f"templates/{template.lower()}_kinderbuch.json"
        
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                self.json_text.delete(1.0, tk.END)
                self.json_text.insert(1.0, json.dumps(template_data, indent=2, ensure_ascii=False))
                self.status_var.set(f"Template geladen: {template}")
            except Exception as e:
                self.status_var.set(f"Fehler beim Laden des Templates: {e}")
        else:
            # Fallback auf Standard-Template
            self.load_default_template()
    
    def load_default_template(self):
        """Lädt das Standard-Template"""
        try:
            with open("data/generate_chapter_full_extended.json", 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(1.0, json.dumps(template_data, indent=2, ensure_ascii=False))
            self.status_var.set("Standard-Template geladen")
        except Exception as e:
            self.status_var.set(f"Fehler beim Laden des Standard-Templates: {e}")
    
    def on_template_change(self, event):
        """Wird aufgerufen, wenn sich das Template ändert"""
        self.load_template()
    
    def validate_json(self):
        """Validiert die JSON-Eingabe"""
        try:
            json_str = self.json_text.get(1.0, tk.END)
            json_data = json.loads(json_str)
            
            # Validiere mit dem Router
            success, data, message = self.router.load_and_validate_prompt_frame_from_data(json_data)
            
            if success:
                messagebox.showinfo("Validierung", "✅ JSON ist gültig!")
                self.status_var.set("JSON validiert")
            else:
                messagebox.showerror("Validierung", f"❌ JSON-Fehler: {message}")
                self.status_var.set("JSON-Validierung fehlgeschlagen")
                
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON-Fehler", f"Ungültige JSON-Syntax: {e}")
            self.status_var.set("JSON-Syntax-Fehler")
        except Exception as e:
            messagebox.showerror("Fehler", f"Validierungsfehler: {e}")
            self.status_var.set("Validierungsfehler")
    
    def generate_chapter(self):
        """Generiert ein Kapitel in einem separaten Thread"""
        if not self.openai_api_key:
            messagebox.showerror("API-Fehler", "OpenAI API Key nicht gefunden!")
            return
        
        # Button deaktivieren
        self.generate_button.config(state="disabled")
        self.status_var.set("Generierung läuft...")
        
        # Thread für Generierung
        thread = threading.Thread(target=self._generate_chapter_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_chapter_thread(self):
        """Thread für die Kapitelgenerierung"""
        try:
            # JSON laden
            json_str = self.json_text.get(1.0, tk.END)
            json_data = json.loads(json_str)
            
            # Temporäre JSON-Datei erstellen
            temp_file = "temp_template.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Pipeline ausführen
            chapter_number = self.chapter_var.get()
            optimize_with_claude = self.claude_var.get()
            
            self.log_status(f"Starte Pipeline für Kapitel {chapter_number}...")
            
            result = self.router.run_full_pipeline(
                prompt_frame_path=temp_file,
                optimize_with_claude=optimize_with_claude,
                chapter_number=chapter_number
            )
            
            # Ergebnisse anzeigen
            self.root.after(0, lambda: self._show_results(result))
            
            # Temporäre Datei löschen
            os.remove(temp_file)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Generierungsfehler: {e}"))
    
    def _show_results(self, result):
        """Zeigt die Generierungsergebnisse an"""
        try:
            if result["success"]:
                # Deutsche Version
                de_file = result["output_files"]["german"]
                if os.path.exists(de_file):
                    with open(de_file, 'r', encoding='utf-8') as f:
                        de_content = f.read()
                    self.de_text.delete(1.0, tk.END)
                    self.de_text.insert(1.0, de_content)
                
                # Englische Version
                en_file = result["output_files"]["english"]
                if os.path.exists(en_file):
                    with open(en_file, 'r', encoding='utf-8') as f:
                        en_content = f.read()
                    self.en_text.delete(1.0, tk.END)
                    self.en_text.insert(1.0, en_content)
                
                # Metadaten
                meta_file = result["output_files"]["metadata"]
                if os.path.exists(meta_file):
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta_content = f.read()
                    self.meta_text.delete(1.0, tk.END)
                    self.meta_text.insert(1.0, meta_content)
                
                # Status aktualisieren
                quality_score = result.get("quality_evaluation", {}).get("overall_bilingual_score", "N/A")
                self.status_var.set(f"✅ Kapitel generiert! Qualitäts-Score: {quality_score}")
                
                # Erfolgsmeldung
                messagebox.showinfo("Erfolg", f"Kapitel erfolgreich generiert!\n\nQualitäts-Score: {quality_score}")
                
            else:
                error_msg = "\n".join(result.get("errors", ["Unbekannter Fehler"]))
                messagebox.showerror("Fehler", f"Generierung fehlgeschlagen:\n{error_msg}")
                self.status_var.set("Generierung fehlgeschlagen")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Ergebnisse: {e}")
            self.status_var.set("Fehler beim Anzeigen der Ergebnisse")
        
        finally:
            # Button wieder aktivieren
            self.generate_button.config(state="normal")
    
    def _show_error(self, error_msg):
        """Zeigt einen Fehler an"""
        messagebox.showerror("Fehler", error_msg)
        self.status_var.set("Fehler aufgetreten")
        self.generate_button.config(state="normal")
    
    def log_status(self, message):
        """Loggt eine Nachricht in den Status-Bereich"""
        self.root.after(0, lambda: self._log_status_thread_safe(message))
    
    def _log_status_thread_safe(self, message):
        """Thread-sichere Status-Logging"""
        self.status_display.insert(tk.END, f"{message}\n")
        self.status_display.see(tk.END)
    
    def batch_generation(self):
        """Batch-Generierung für mehrere Kapitel"""
        if not self.openai_api_key:
            messagebox.showerror("API-Fehler", "OpenAI API Key nicht gefunden!")
            return
        
        # Thread für Batch-Generierung
        thread = threading.Thread(target=self._batch_generation_thread)
        thread.daemon = True
        thread.start()
    
    def _batch_generation_thread(self):
        """Thread für Batch-Generierung"""
        try:
            # JSON laden
            json_str = self.json_text.get(1.0, tk.END)
            json_data = json.loads(json_str)
            
            # Temporäre JSON-Datei erstellen
            temp_file = "temp_template.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Batch-Generierung
            optimize_with_claude = self.claude_var.get()
            
            self.log_status("Starte Batch-Generierung (3 Kapitel)...")
            
            results = []
            for chapter_num in range(1, 4):
                self.log_status(f"Generiere Kapitel {chapter_num}...")
                
                result = self.router.run_full_pipeline(
                    prompt_frame_path=temp_file,
                    optimize_with_claude=optimize_with_claude,
                    chapter_number=chapter_num
                )
                
                results.append(result)
                
                if result["success"]:
                    quality_score = result.get("quality_evaluation", {}).get("overall_bilingual_score", "N/A")
                    self.log_status(f"Kapitel {chapter_num} erfolgreich (Score: {quality_score})")
                else:
                    self.log_status(f"Kapitel {chapter_num} fehlgeschlagen")
            
            # Temporäre Datei löschen
            os.remove(temp_file)
            
            # Ergebnisse zusammenfassen
            successful = sum(1 for r in results if r["success"])
            self.root.after(0, lambda: messagebox.showinfo("Batch-Generierung", 
                f"Batch-Generierung abgeschlossen!\n\nErfolgreich: {successful}/3 Kapitel"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"Batch-Generierungsfehler: {e}"))
    
    def configure_api_keys(self):
        """Konfiguriert API-Keys"""
        dialog = tk.Toplevel(self.root)
        dialog.title("API-Keys konfigurieren")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Zentriere Dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (200)
        y = (dialog.winfo_screenheight() // 2) - (100)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Frame
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # OpenAI Key
        ttk.Label(frame, text="OpenAI API Key:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        openai_entry = ttk.Entry(frame, width=50, show="*")
        openai_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        openai_entry.insert(0, self.openai_api_key or "")
        
        # Claude Key
        ttk.Label(frame, text="Anthropic API Key:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        claude_entry = ttk.Entry(frame, width=50, show="*")
        claude_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        claude_entry.insert(0, self.anthropic_api_key or "")
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        def save_keys():
            openai_key = openai_entry.get().strip()
            claude_key = claude_entry.get().strip()
            
            # .env Datei aktualisieren
            env_content = f"OPENAI_API_KEY={openai_key}\nANTHROPIC_API_KEY={claude_key}\n"
            
            try:
                with open(".env", 'w', encoding='utf-8') as f:
                    f.write(env_content)
                
                # Variablen aktualisieren
                self.openai_api_key = openai_key
                self.anthropic_api_key = claude_key
                
                messagebox.showinfo("Erfolg", "API-Keys gespeichert!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
        
        ttk.Button(button_frame, text="Speichern", command=save_keys).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def load_json(self):
        """Lädt eine JSON-Datei"""
        filename = filedialog.askopenfilename(
            title="JSON-Datei laden",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    json_str = f.read()
                
                self.json_text.delete(1.0, tk.END)
                self.json_text.insert(1.0, json_str)
                self.status_var.set(f"JSON geladen: {filename}")
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden: {e}")
    
    def save_json(self):
        """Speichert die JSON-Eingabe"""
        filename = filedialog.asksaveasfilename(
            title="JSON-Datei speichern",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                json_str = self.json_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                self.status_var.set(f"JSON gespeichert: {filename}")
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def save_all_results(self):
        """Speichert alle Ergebnisse"""
        try:
            # Ordner für Ergebnisse
            results_dir = "gui_results"
            os.makedirs(results_dir, exist_ok=True)
            
            # Deutsche Version
            de_content = self.de_text.get(1.0, tk.END)
            if de_content.strip():
                with open(f"{results_dir}/chapter_de.txt", 'w', encoding='utf-8') as f:
                    f.write(de_content)
            
            # Englische Version
            en_content = self.en_text.get(1.0, tk.END)
            if en_content.strip():
                with open(f"{results_dir}/chapter_en.txt", 'w', encoding='utf-8') as f:
                    f.write(en_content)
            
            # Metadaten
            meta_content = self.meta_text.get(1.0, tk.END)
            if meta_content.strip():
                with open(f"{results_dir}/chapter_meta.json", 'w', encoding='utf-8') as f:
                    f.write(meta_content)
            
            messagebox.showinfo("Erfolg", f"Alle Ergebnisse gespeichert in: {results_dir}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def show_metadata(self):
        """Zeigt Metadaten in einem separaten Fenster"""
        meta_content = self.meta_text.get(1.0, tk.END)
        if meta_content.strip():
            dialog = tk.Toplevel(self.root)
            dialog.title("Metadaten")
            dialog.geometry("600x400")
            dialog.transient(self.root)
            
            # Zentriere Dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300)
            y = (dialog.winfo_screenheight() // 2) - (200)
            dialog.geometry(f"600x400+{x}+{y}")
            
            # Text-Widget
            text_widget = scrolledtext.ScrolledText(dialog, font=("Consolas", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(1.0, meta_content)
            text_widget.config(state=tk.DISABLED)
            
            # Schließen-Button
            ttk.Button(dialog, text="Schließen", command=dialog.destroy).pack(pady=10)

def main():
    root = tk.Tk()
    
    # Fenster-Management
    root.lift()
    root.attributes('-topmost', True)
    root.focus_force()
    
    # Zentriere das Fenster
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Nach dem Laden wieder normal
    root.after(1000, lambda: root.attributes('-topmost', False))
    
    app = EnhancedBookWriterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 