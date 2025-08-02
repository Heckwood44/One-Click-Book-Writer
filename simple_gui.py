import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import os
import sys
import openai
import anthropic
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compiler.prompt_compiler import compile_prompt, compile_prompt_for_chatgpt
from schema.validate_input import validate_json_schema

class SimpleBookWriterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("One Click Book Writer - AI-Powered Story Development")
        self.root.geometry("1400x900")
        
        # API Keys prüfen
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.openai_api_key:
            messagebox.showwarning("API Key fehlt", 
                "OPENAI_API_KEY nicht gefunden in .env Datei.\n"
                "Bitte füge deinen OpenAI API Key zur .env Datei hinzu:\n"
                "OPENAI_API_KEY=dein-api-key-hier")
        
        if not self.anthropic_api_key:
            messagebox.showwarning("Claude API Key fehlt", 
                "ANTHROPIC_API_KEY nicht gefunden in .env Datei.\n"
                "Claude-Features für Story-Entwicklung sind nicht verfügbar.\n"
                "ANTHROPIC_API_KEY=dein-claude-api-key-hier")
        
        # API Clients initialisieren
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Claude Client nur initialisieren wenn API Key vorhanden und nicht der Platzhalter ist
        self.claude_client = None
        if self.anthropic_api_key and len(self.anthropic_api_key.strip()) > 0:
            try:
                # Verwende nur die notwendigen Parameter für die neueste Anthropic Version
                self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                print("Claude Client erfolgreich initialisiert")
            except Exception as e:
                print(f"Claude Client Initialisierung fehlgeschlagen: {e}")
                # Fallback: Versuche es ohne zusätzliche Parameter
                try:
                    self.claude_client = anthropic.Anthropic()
                    self.claude_client.api_key = self.anthropic_api_key
                    print("Claude Client erfolgreich initialisiert (Fallback)")
                except Exception as e2:
                    print(f"Claude Client Fallback fehlgeschlagen: {e2}")
                    self.claude_client = None
        
        # Beispiel-JSON laden (kompatibel mit neuer bilingualer Struktur)
        self.example_data = {
            "input": {
                "book": {
                    "title": "Die magische Reise",
                    "genre": "Fantasy",
                    "target_audience": "children",
                    "theme": "Mut und Selbstvertrauen",
                    "setting": "Ein verzauberter Wald",
                    "language_variants": ["de", "en"],
                    "bilingual_sequence": ["de", "en"],
                    "titles": {
                        "de": "Die magische Reise",
                        "en": "The Magical Journey"
                    }
                },
                "chapter": {
                    "number": 1,
                    "title": "Der Anfang der Reise",
                    "narrative_purpose": "Einführung der Hauptfigur und Aufbau der Spannung",
                    "position_in_arc": "setup",
                    "length_words": 800,
                    "language_variants": ["de", "en"],
                    "bilingual_sequence": ["de", "en"],
                    "titles": {
                        "de": "Der Anfang der Reise",
                        "en": "The Beginning of the Journey"
                    }
                },
                "characters": {
                    "main_character": {
                        "name": "Luna",
                        "description": "Ein mutiges Mädchen mit magischen Fähigkeiten",
                        "personality": "Neugierig, mutig und freundlich",
                        "goals": "Die Geheimnisse des Waldes entdecken",
                        "language_variants": {
                            "de": {
                                "name": "Luna",
                                "description": "Ein mutiges Mädchen mit magischen Fähigkeiten"
                            },
                            "en": {
                                "name": "Luna",
                                "description": "A brave girl with magical abilities"
                            }
                        }
                    },
                    "supporting_characters": [
                        {
                            "name": "Waldgeist",
                            "role": "Magischer Begleiter",
                            "language_variants": {
                                "de": {
                                    "name": "Waldgeist",
                                    "role": "Magischer Begleiter"
                                },
                                "en": {
                                    "name": "Forest Spirit",
                                    "role": "Magical companion"
                                }
                            }
                        }
                    ]
                },
                "scene": {
                    "setting": "Ein verzauberter Wald",
                    "time": "Goldener Nachmittag",
                    "atmosphere": "Magisch und aufregend",
                    "language_variants": {
                        "de": {
                            "setting": "Ein verzauberter Wald",
                            "time": "Goldener Nachmittag",
                            "atmosphere": "Magisch und aufregend"
                        },
                        "en": {
                            "setting": "An enchanted forest",
                            "time": "Golden afternoon",
                            "atmosphere": "Magical and exciting"
                        }
                    }
                },
                "plot": {
                    "main_event": "Luna entdeckt den verzauberten Wald",
                    "conflict": "Angst vor dem Unbekannten vs. Neugier",
                    "resolution": "Freundschaft mit dem Waldgeist",
                    "language_variants": {
                        "de": {
                            "main_event": "Luna entdeckt den verzauberten Wald",
                            "conflict": "Angst vor dem Unbekannten vs. Neugier",
                            "resolution": "Freundschaft mit dem Waldgeist"
                        },
                        "en": {
                            "main_event": "Luna discovers the enchanted forest",
                            "conflict": "Fear of the unknown vs. curiosity",
                            "resolution": "Friendship with the forest spirit"
                        }
                    }
                },
                "style": {
                    "dialogue_style": "natural_and_engaging",
                    "pacing": "moderate",
                    "tone": "Warm und ermutigend"
                },
                "emotions": {
                    "primary_emotion": "wonder",
                    "emotional_arc": "growth",
                    "mood": "hopeful",
                    "language_variants": {
                        "de": {
                            "primary_emotion": "wonder",
                            "emotional_arc": "growth",
                            "mood": "hopeful"
                        },
                        "en": {
                            "primary_emotion": "wonder",
                            "emotional_arc": "growth",
                            "mood": "hopeful"
                        }
                    }
                },
                "language": {
                    "bilingual_output": True,
                    "target_languages": ["de", "en"],
                    "separate_files": False,
                    "cultural_adaptation": True
                }
            }
        }
        
        self.setup_ui()
        self.load_example_data()
        
    def setup_ui(self):
        # Hauptframe mit Notebook für Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Kapitel Generierung
        self.chapter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chapter_tab, text="📝 Kapitel Generierung")
        self.setup_chapter_tab()
        
        # Tab 2: Story-Entwicklung (Claude)
        self.story_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.story_tab, text="🎭 Story-Entwicklung")
        self.setup_story_tab()
        
        # Tab 3: Charakter-Entwicklung (Claude)
        self.character_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.character_tab, text="👤 Charakter-Entwicklung")
        self.setup_character_tab()
        
    def setup_chapter_tab(self):
        # Hauptframe
        main_frame = ttk.Frame(self.chapter_tab, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguriere Grid-Gewichtung
        self.chapter_tab.columnconfigure(0, weight=1)
        self.chapter_tab.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Titel
        title_label = ttk.Label(main_frame, text="One Click Book Writer - Kapitel Generierung", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # API Status und Konfiguration
        api_frame = ttk.Frame(main_frame)
        api_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        
        openai_status = "✅ API Key verfügbar" if self.openai_api_key else "❌ API Key fehlt"
        claude_status = "✅ API Key verfügbar" if self.claude_client else "❌ API Key fehlt"
        status_text = f"OpenAI: {openai_status} | Claude: {claude_status}"
        status_label = ttk.Label(api_frame, text=status_text, font=("Arial", 10))
        status_label.pack(side="left", padx=(0, 10))
        
        # API Keys konfigurieren Button
        config_button = ttk.Button(api_frame, text="🔑 API Keys konfigurieren", command=self.configure_api_keys)
        config_button.pack(side="right")
        
        # Linke Seite - JSON Editor
        left_frame = ttk.LabelFrame(main_frame, text="JSON Eingabe", padding="10")
        left_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # JSON Editor
        self.json_text = scrolledtext.ScrolledText(left_frame, width=50, height=30)
        self.json_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons für JSON
        json_buttons_frame = ttk.Frame(left_frame)
        json_buttons_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(json_buttons_frame, text="Beispiel laden", command=self.load_example_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_buttons_frame, text="Validieren", command=self.validate_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_buttons_frame, text="Speichern", command=self.save_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_buttons_frame, text="Laden", command=self.load_json).pack(side=tk.LEFT)
        
        # Rechte Seite - Prompt Vorschau und Generierung
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Engine Auswahl
        engine_frame = ttk.LabelFrame(right_frame, text="AI Engine", padding="10")
        engine_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.engine_var = tk.StringVar(value="chatgpt")
        ttk.Radiobutton(engine_frame, text="Claude (Prompt Design)", variable=self.engine_var, value="claude").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(engine_frame, text="ChatGPT (Text Generierung)", variable=self.engine_var, value="chatgpt").pack(side=tk.LEFT)
        
        # Prompt Vorschau
        prompt_frame = ttk.LabelFrame(right_frame, text="Prompt Vorschau", padding="10")
        prompt_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(0, weight=1)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, width=60, height=15)
        self.prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Generierung Buttons
        gen_frame = ttk.Frame(right_frame)
        gen_frame.grid(row=2, column=0, pady=(0, 10))
        
        ttk.Button(gen_frame, text="Prompt aktualisieren", command=self.update_prompt).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(gen_frame, text="Kapitel mit ChatGPT generieren", command=self.generate_chapter_with_chatgpt).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(gen_frame, text="Batch Generierung", command=self.batch_generation_demo).pack(side=tk.LEFT)
        
        # Ergebnisse
        results_frame = ttk.LabelFrame(right_frame, text="Generiertes Kapitel", padding="10")
        results_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, width=60, height=10)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status Bar
        self.status_var = tk.StringVar(value="Bereit")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_story_tab(self):
        # Hauptframe
        main_frame = ttk.Frame(self.story_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="🎭 Story-Struktur & Emotionale Tiefe", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Claude Status
        if not self.claude_client:
            status_label = ttk.Label(main_frame, text="❌ Claude API Key fehlt - Story-Entwicklung nicht verfügbar", font=("Arial", 12, "bold"), foreground="red")
            status_label.pack(pady=(0, 20))
            return
        
        # Story-Kontext Eingabe
        context_frame = ttk.LabelFrame(main_frame, text="Story-Kontext", padding="10")
        context_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(context_frame, text="Beschreibe deine Story-Idee:").pack(anchor=tk.W)
        self.story_context_text = scrolledtext.ScrolledText(context_frame, height=6)
        self.story_context_text.pack(fill=tk.X, pady=(0, 10))
        
        # Beratungs-Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="📖 Story-Struktur Vorschläge", command=self.get_story_structure_suggestions).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="💝 Emotionale Tiefe Optimierung", command=self.optimize_emotional_depth).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🎯 Plot-Entwicklung", command=self.develop_plot).pack(side=tk.LEFT)
        
        # Ergebnisse
        results_frame = ttk.LabelFrame(main_frame, text="Claude's Beratung", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.story_results_text = scrolledtext.ScrolledText(results_frame)
        self.story_results_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_character_tab(self):
        # Hauptframe
        main_frame = ttk.Frame(self.character_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="👤 Charakter-Entwicklung", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Claude Status
        if not self.claude_client:
            status_label = ttk.Label(main_frame, text="❌ Claude API Key fehlt - Charakter-Entwicklung nicht verfügbar", font=("Arial", 12, "bold"), foreground="red")
            status_label.pack(pady=(0, 20))
            return
        
        # Charakter-Eingabe
        character_frame = ttk.LabelFrame(main_frame, text="Charakter-Beschreibung", padding="10")
        character_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(character_frame, text="Beschreibe deinen Charakter:").pack(anchor=tk.W)
        self.character_text = scrolledtext.ScrolledText(character_frame, height=6)
        self.character_text.pack(fill=tk.X, pady=(0, 10))
        
        # Beratungs-Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🎭 Charakter-Entwicklung", command=self.develop_character).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="💬 Dialog-Optimierung", command=self.optimize_dialogue).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="🔄 Charakter-Arc", command=self.character_arc).pack(side=tk.LEFT)
        
        # Ergebnisse
        results_frame = ttk.LabelFrame(main_frame, text="Claude's Charakter-Beratung", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.character_results_text = scrolledtext.ScrolledText(results_frame)
        self.character_results_text.pack(fill=tk.BOTH, expand=True)
        
    def get_story_structure_suggestions(self):
        """Holt Story-Struktur Vorschläge von Claude"""
        if not self.claude_client:
            messagebox.showerror("Fehler", "Claude API Key fehlt")
            return
        
        try:
            context = self.story_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Story-Idee ein")
                return
            
            prompt = f"""Du bist ein erfahrener Story-Entwickler und Schriftsteller. Analysiere diese Story-Idee und gib detaillierte Vorschläge für die Story-Struktur:

Story-Idee: {context}

Bitte gib mir:
1. **Drei-Akt-Struktur** - Wie könnte die Story in drei Akte aufgeteilt werden?
2. **Plot-Punkte** - Welche wichtigen Wendepunkte sollte die Story haben?
3. **Spannungsbogen** - Wie kann die Spannung aufgebaut und gehalten werden?
4. **Themen & Motive** - Welche zentralen Themen könnten entwickelt werden?
5. **Genre-spezifische Elemente** - Welche Genre-Konventionen sollten beachtet werden?

Gib strukturierte, praktische Vorschläge, die sofort umsetzbar sind."""
            
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, "🤔 Claude analysiert deine Story-Struktur...\n\n")
            self.story_tab.update()
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Story-Analyse: {e}")
    
    def optimize_emotional_depth(self):
        """Optimiert die emotionale Tiefe der Story"""
        if not self.claude_client:
            messagebox.showerror("Fehler", "Claude API Key fehlt")
            return
        
        try:
            context = self.story_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Story-Idee ein")
                return
            
            prompt = f"""Du bist ein Experte für emotionale Story-Entwicklung. Analysiere diese Story-Idee und gib Vorschläge für emotionale Tiefe:

Story-Idee: {context}

Bitte gib mir:
1. **Emotionale Konflikte** - Welche inneren und äußeren Konflikte können die Charaktere haben?
2. **Emotionale Entwicklung** - Wie können sich die Charaktere emotional entwickeln?
3. **Empathie-Aufbau** - Wie kann der Leser mit den Charakteren mitfühlen?
4. **Emotionale Höhepunkte** - Wo sollten die emotional intensivsten Momente sein?
5. **Therapeutische Elemente** - Welche emotionalen Heilungsprozesse können eingebaut werden?

Konzentriere dich auf authentische, tiefgreifende Emotionen."""
            
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, "💝 Claude optimiert die emotionale Tiefe...\n\n")
            self.story_tab.update()
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der emotionalen Optimierung: {e}")
    
    def develop_plot(self):
        """Entwickelt den Plot weiter"""
        if not self.claude_client:
            messagebox.showerror("Fehler", "Claude API Key fehlt")
            return
        
        try:
            context = self.story_context_text.get(1.0, tk.END).strip()
            if not context:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Story-Idee ein")
                return
            
            prompt = f"""Du bist ein Plot-Entwickler. Erweitere diese Story-Idee zu einem vollständigen Plot:

Story-Idee: {context}

Bitte entwickle:
1. **Hauptplot** - Die zentrale Handlung mit Anfang, Mitte, Ende
2. **Subplots** - Welche Nebenhandlungen können die Hauptstory unterstützen?
3. **Konflikte** - Verschiedene Arten von Konflikten (Mensch vs. Mensch, Mensch vs. Natur, etc.)
4. **Auflösungen** - Wie können die verschiedenen Handlungsstränge aufgelöst werden?
5. **Überraschungen** - Welche unerwarteten Wendungen können eingebaut werden?

Mache den Plot spannend und logisch kohärent."""
            
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, "🎯 Claude entwickelt den Plot...\n\n")
            self.story_tab.update()
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            self.story_results_text.delete(1.0, tk.END)
            self.story_results_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Plot-Entwicklung: {e}")
    
    def develop_character(self):
        """Entwickelt Charaktere weiter"""
        if not self.claude_client:
            messagebox.showerror("Fehler", "Claude API Key fehlt")
            return
        
        try:
            character = self.character_text.get(1.0, tk.END).strip()
            if not character:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Charakter-Beschreibung ein")
                return
            
            prompt = f"""Du bist ein Charakter-Entwickler. Erweitere diese Charakter-Beschreibung:

Charakter: {character}

Bitte entwickle:
1. **Hintergrund** - Was ist die Geschichte des Charakters?
2. **Motivationen** - Was treibt den Charakter an?
3. **Stärken & Schwächen** - Welche Eigenschaften hat der Charakter?
4. **Entwicklung** - Wie kann sich der Charakter im Laufe der Story entwickeln?
5. **Beziehungen** - Welche Beziehungen könnte der Charakter haben?
6. **Konflikte** - Welche inneren und äußeren Konflikte hat der Charakter?

Mache den Charakter komplex, interessant und realistisch."""
            
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, "👤 Claude entwickelt den Charakter...\n\n")
            self.character_tab.update()
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Charakter-Entwicklung: {e}")
    
    def optimize_dialogue(self):
        """Optimiert Dialoge für den Charakter"""
        if not self.claude_client:
            messagebox.showerror("Fehler", "Claude API Key fehlt")
            return
        
        try:
            character = self.character_text.get(1.0, tk.END).strip()
            if not character:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Charakter-Beschreibung ein")
                return
            
            prompt = f"""Du bist ein Dialog-Experte. Entwickle authentische Dialoge für diesen Charakter:

Charakter: {character}

Bitte gib mir:
1. **Sprechweise** - Wie spricht dieser Charakter? (Wortwahl, Satzstruktur, Akzente)
2. **Beispiel-Dialoge** - 3-5 Beispiel-Dialoge in verschiedenen Situationen
3. **Emotionale Ausdrücke** - Wie drückt der Charakter verschiedene Emotionen aus?
4. **Charakteristische Phrasen** - Welche wiederkehrenden Ausdrücke könnte der Charakter haben?
5. **Dialog-Tipps** - Wie kann man die Stimme des Charakters konsistent halten?

Mache die Dialoge authentisch und charakteristisch."""
            
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, "💬 Claude optimiert die Dialoge...\n\n")
            self.character_tab.update()
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Dialog-Optimierung: {e}")
    
    def character_arc(self):
        """Entwickelt den Charakter-Arc"""
        if not self.claude_client:
            messagebox.showerror("Fehler", "Claude API Key fehlt")
            return
        
        try:
            character = self.character_text.get(1.0, tk.END).strip()
            if not character:
                messagebox.showwarning("Warnung", "Bitte gib zuerst eine Charakter-Beschreibung ein")
                return
            
            prompt = f"""Du bist ein Experte für Charakter-Entwicklung. Entwickle einen Charakter-Arc für:

Charakter: {character}

Bitte entwickle:
1. **Anfangs-Zustand** - Wie ist der Charakter am Anfang der Story?
2. **Entwicklungs-Trigger** - Was löst die Entwicklung aus?
3. **Entwicklungs-Phasen** - Welche Schritte durchläuft der Charakter?
4. **Widerstände** - Welche Hindernisse muss der Charakter überwinden?
5. **End-Zustand** - Wie hat sich der Charakter am Ende verändert?
6. **Thematische Bedeutung** - Was bedeutet diese Entwicklung für die Story?

Mache den Arc überzeugend und bedeutungsvoll."""
            
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, "🔄 Claude entwickelt den Charakter-Arc...\n\n")
            self.character_tab.update()
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            self.character_results_text.delete(1.0, tk.END)
            self.character_results_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Charakter-Arc-Entwicklung: {e}")
        
    def configure_api_keys(self):
        """Öffnet ein Dialog-Fenster zur API Key Konfiguration"""
        config_window = tk.Toplevel(self.root)
        config_window.title("API Keys konfigurieren")
        config_window.geometry("600x500")
        config_window.resizable(False, False)
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Zentriere das Fenster
        config_window.update_idletasks()
        x = (config_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (config_window.winfo_screenheight() // 2) - (500 // 2)
        config_window.geometry(f"600x500+{x}+{y}")
        
        # Hauptframe
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="🔑 API Keys konfigurieren", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # OpenAI API Key
        openai_frame = ttk.LabelFrame(main_frame, text="OpenAI API Key", padding="10")
        openai_frame.pack(fill="x", pady=(0, 10))
        
        openai_label = ttk.Label(openai_frame, text="OpenAI API Key (für ChatGPT):")
        openai_label.pack(anchor="w")
        
        openai_entry = ttk.Entry(openai_frame, width=50, show="*")
        openai_entry.pack(fill="x", pady=(5, 0))
        openai_entry.insert(0, self.openai_api_key or "")
        
        # Enter-Key Handler für OpenAI Entry
        def on_openai_enter(event):
            save_api_keys()
        openai_entry.bind('<Return>', on_openai_enter)
        
        # Claude API Key
        claude_frame = ttk.LabelFrame(main_frame, text="Anthropic API Key", padding="10")
        claude_frame.pack(fill="x", pady=(0, 20))
        
        claude_label = ttk.Label(claude_frame, text="Anthropic API Key (für Claude):")
        claude_label.pack(anchor="w")
        
        claude_entry = ttk.Entry(claude_frame, width=50, show="*")
        claude_entry.pack(fill="x", pady=(5, 0))
        claude_entry.insert(0, self.anthropic_api_key or "")
        
        # Enter-Key Handler für Claude Entry
        def on_claude_enter(event):
            save_api_keys()
        claude_entry.bind('<Return>', on_claude_enter)
        
        # Buttons - Größerer Frame für bessere Sichtbarkeit
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        def save_api_keys():
            openai_key = openai_entry.get().strip()
            claude_key = claude_entry.get().strip()
            
            # Speichere in .env Datei
            env_content = f"OPENAI_API_KEY={openai_key}\nANTHROPIC_API_KEY={claude_key}\n"
            
            try:
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(env_content)
                
                # Aktualisiere die Instanz-Variablen
                self.openai_api_key = openai_key if openai_key else None
                self.anthropic_api_key = claude_key if claude_key else None
                
                # Initialisiere Clients neu
                if self.openai_api_key:
                    openai.api_key = self.openai_api_key
                
                self.claude_client = None
                if self.anthropic_api_key and len(self.anthropic_api_key.strip()) > 0:
                    try:
                        self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                        print("Claude Client erfolgreich initialisiert")
                    except Exception as e:
                        print(f"Claude Client Initialisierung fehlgeschlagen: {e}")
                        self.claude_client = None
                
                messagebox.showinfo("Erfolg", "API Keys wurden erfolgreich gespeichert!")
                config_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern der API Keys: {e}")
        
        # Größere, auffälligere Buttons
        save_button = ttk.Button(button_frame, text="💾 SPEICHERN", command=save_api_keys)
        save_button.pack(side="right", padx=(10, 0), pady=10)
        
        cancel_button = ttk.Button(button_frame, text="❌ ABBRECHEN", command=config_window.destroy)
        cancel_button.pack(side="right", padx=(5, 0), pady=10)
        
        # Info Text - Kürzer und übersichtlicher
        info_text = ttk.Label(main_frame, text="💡 API Keys: OpenAI (platform.openai.com) | Anthropic (console.anthropic.com)", 
                             font=("Arial", 9), foreground="gray")
        info_text.pack(pady=(15, 0))

    def load_example_data(self):
        """Lädt Beispieldaten in den JSON Editor"""
        try:
            json_str = json.dumps(self.example_data, indent=2, ensure_ascii=False)
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(1.0, json_str)
            self.update_prompt()
            self.status_var.set("Beispieldaten geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Beispieldaten: {e}")
    
    def validate_json(self):
        """Validiert die JSON Eingabe"""
        try:
            json_str = self.json_text.get(1.0, tk.END)
            data = json.loads(json_str)
            
            # Schema-Validierung
            schema_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema", "prompt_frame.schema.json")
            is_valid, message = validate_json_schema(data, schema_file)
            
            if not is_valid:
                messagebox.showerror("Validierungsfehler", f"Schema-Fehler: {message}")
                self.status_var.set("Validierung fehlgeschlagen")
            else:
                # Zusätzliche Prompt-Struktur-Validierung
                from compiler.prompt_compiler import validate_prompt_structure
                if validate_prompt_structure(data):
                    messagebox.showinfo("Erfolg", "JSON ist gültig!")
                    self.status_var.set("JSON validiert")
                    self.update_prompt()
                else:
                    messagebox.showerror("Validierungsfehler", "Ungültige Prompt-Struktur")
                    self.status_var.set("Validierung fehlgeschlagen")
                
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Fehler", f"Ungültiges JSON: {e}")
            self.status_var.set("JSON Fehler")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Validierung: {e}")
    
    def update_prompt(self):
        """Aktualisiert die Prompt Vorschau"""
        try:
            json_str = self.json_text.get(1.0, tk.END)
            data = json.loads(json_str)
            
            if self.engine_var.get() == "claude":
                prompt = compile_prompt(data)
            else:
                prompt = compile_prompt_for_chatgpt(data)
            
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, prompt)
            self.status_var.set("Prompt aktualisiert")
            
        except Exception as e:
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(1.0, f"Fehler beim Kompilieren des Prompts: {e}")
            self.status_var.set("Prompt Fehler")
    
    def generate_chapter_with_chatgpt(self):
        """Generiert ein Kapitel mit der echten ChatGPT API"""
        if not self.openai_api_key:
            messagebox.showerror("API Key fehlt", 
                "Bitte füge deinen OpenAI API Key zur .env Datei hinzu:\n"
                "OPENAI_API_KEY=dein-api-key-hier")
            return
        
        try:
            # JSON validieren
            json_str = self.json_text.get(1.0, tk.END)
            data = json.loads(json_str)
            
            # Schema-Validierung
            errors = validate_json_schema(data)
            if errors:
                messagebox.showerror("Validierungsfehler", "Bitte korrigiere die JSON-Eingabe")
                return
            
            # Prompt kompilieren
            prompt = compile_prompt_for_chatgpt(data)
            
            # Status aktualisieren
            self.status_var.set("Generiere Kapitel mit ChatGPT...")
            self.root.update()
            
            # ChatGPT API aufrufen
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener Autor und Schriftsteller."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                top_p=0.9
            )
            
            # Antwort extrahieren
            generated_text = response.choices[0].message.content
            
            # Kapitel anzeigen
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, generated_text)
            
            # Status aktualisieren
            self.status_var.set(f"Kapitel generiert! Tokens: {response.usage.total_tokens}")
            
            # Erfolgsmeldung
            messagebox.showinfo("Erfolg", f"Kapitel erfolgreich generiert!\n\nTokens verwendet: {response.usage.total_tokens}\nKosten: ~${response.usage.total_tokens * 0.00003:.4f}")
            
        except openai.error.AuthenticationError:
            messagebox.showerror("API Fehler", "Ungültiger OpenAI API Key")
            self.status_var.set("API Authentifizierung fehlgeschlagen")
        except openai.error.RateLimitError:
            messagebox.showerror("API Fehler", "Rate Limit erreicht. Bitte warte einen Moment.")
            self.status_var.set("Rate Limit erreicht")
        except openai.error.APIError as e:
            messagebox.showerror("API Fehler", f"OpenAI API Fehler: {e}")
            self.status_var.set("API Fehler")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Generierung: {e}")
            self.status_var.set("Generierung fehlgeschlagen")
    
    def batch_generation_demo(self):
        """Demo für Batch-Generierung"""
        try:
            # Simuliere Batch-Generierung
            chapters = []
            for i in range(1, 4):
                chapter_text = f"# Kapitel {i} - Demo\n\nDies ist ein Demo-Kapitel {i} aus der Batch-Generierung.\n\nDie echte Batch-Generierung würde hier {i} vollständige Kapitel erstellen, die alle auf der JSON-Eingabe basieren.\n\n---\n"
                chapters.append(chapter_text)
            
            # Zeige alle Kapitel
            all_chapters = "\n".join(chapters)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, all_chapters)
            
            self.status_var.set("Batch-Demo: 3 Kapitel generiert")
            messagebox.showinfo("Batch-Generierung", "Demo: 3 Kapitel wurden generiert!")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Batch-Generierung: {e}")
    
    def save_json(self):
        """Speichert die JSON Eingabe"""
        filename = filedialog.asksaveasfilename(
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
    
    def load_json(self):
        """Lädt eine JSON Datei"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    json_str = f.read()
                self.json_text.delete(1.0, tk.END)
                self.json_text.insert(1.0, json_str)
                self.update_prompt()
                self.status_var.set(f"JSON geladen: {filename}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden: {e}")

def main():
    root = tk.Tk()
    
    # Fenster-Management für bessere Sichtbarkeit
    root.lift()  # Fenster in den Vordergrund bringen
    root.attributes('-topmost', True)  # Fenster immer oben halten
    root.focus_force()  # Fokus erzwingen
    
    # Zentriere das Fenster auf dem Bildschirm
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Nach dem Laden wieder normal
    root.after(1000, lambda: root.attributes('-topmost', False))
    
    app = SimpleBookWriterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 