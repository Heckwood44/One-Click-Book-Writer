#!/usr/bin/env python3
"""
One Click Book Writer - Test Application
Funktioniert ohne API-Keys für Demo-Zwecke
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestBookWriterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "One Click Book Writer - Test App (Keine API-Keys erforderlich)"
        )
        self.root.geometry("1200x800")

        # Beispiel-Template
        self.example_template = {
            "input": {
                "book": {
                    "title": "Die magische Reise",
                    "genre": "Fantasy",
                    "target_audience": "children",
                    "theme": "Mut und Selbstvertrauen",
                    "setting": "Ein verzauberter Wald",
                },
                "chapter": {
                    "number": 1,
                    "title": "Der Anfang der Reise",
                    "narrative_purpose": "Einführung der Hauptfigur",
                    "position_in_arc": "setup",
                    "length_words": 800,
                },
                "characters": {
                    "main_character": {
                        "name": "Luna",
                        "age": 10,
                        "personality": "mutig und neugierig",
                        "goal": "den verzauberten Wald erkunden",
                    }
                },
                "style": {
                    "writing_style": "descriptive",
                    "tone": "warm",
                    "tense": "past",
                    "perspective": "third_limited",
                },
            }
        }

        self.setup_ui()
        self.load_example()

    def setup_ui(self):
        """Baut die Benutzeroberfläche auf"""
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titel
        title_label = ttk.Label(
            main_frame,
            text="One Click Book Writer - Test Application",
            font=("Arial", 16, "bold"),
        )
        title_label.pack(pady=(0, 10))

        # Info-Text
        info_text = ttk.Label(
            main_frame,
            text="Diese Test-Anwendung demonstriert das Framework ohne API-Keys.\n"
            "Sie können Templates bearbeiten und die Struktur testen.",
            font=("Arial", 10),
        )
        info_text.pack(pady=(0, 20))

        # Notebook für Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Template-Tab
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="Template Editor")

        # Template-Editor
        template_label = ttk.Label(
            template_frame, text="JSON Template:", font=("Arial", 12, "bold")
        )
        template_label.pack(anchor=tk.W, pady=(10, 5))

        self.template_text = scrolledtext.ScrolledText(
            template_frame, height=20, font=("Consolas", 10)
        )
        self.template_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(template_frame)
        button_frame.pack(fill=tk.X, padx=10)

        ttk.Button(button_frame, text="Beispiel laden", command=self.load_example).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(
            button_frame, text="Validieren", command=self.validate_template
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            button_frame, text="Demo-Generierung", command=self.demo_generation
        ).pack(side=tk.LEFT)

        # Demo-Tab
        demo_frame = ttk.Frame(notebook)
        notebook.add(demo_frame, text="Demo-Output")

        # Demo-Output
        demo_label = ttk.Label(
            demo_frame, text="Demo-Generierung:", font=("Arial", 12, "bold")
        )
        demo_label.pack(anchor=tk.W, pady=(10, 5))

        self.demo_text = scrolledtext.ScrolledText(
            demo_frame, height=20, font=("Consolas", 10)
        )
        self.demo_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit - Test-Anwendung läuft")
        status_label = ttk.Label(
            main_frame, textvariable=self.status_var, font=("Arial", 10)
        )
        status_label.pack(pady=(10, 0))

    def load_example(self):
        """Lädt das Beispiel-Template"""
        try:
            json_str = json.dumps(self.example_template, indent=2, ensure_ascii=False)
            self.template_text.delete(1.0, tk.END)
            self.template_text.insert(1.0, json_str)
            self.status_var.set("Beispiel-Template geladen")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Beispiels: {e}")

    def validate_template(self):
        """Validiert das JSON-Template"""
        try:
            json_str = self.template_text.get(1.0, tk.END)
            template = json.loads(json_str)

            # Einfache Validierung
            required_fields = ["input", "book", "chapter", "characters", "style"]
            missing_fields = []

            for field in required_fields:
                if field not in template.get("input", {}):
                    missing_fields.append(field)

            if missing_fields:
                messagebox.showwarning(
                    "Validierung", f"Fehlende Felder: {', '.join(missing_fields)}"
                )
                self.status_var.set("Template-Validierung: Fehlende Felder")
            else:
                messagebox.showinfo("Validierung", "✅ Template ist gültig!")
                self.status_var.set("Template-Validierung: Erfolgreich")

        except json.JSONDecodeError as e:
            messagebox.showerror("JSON-Fehler", f"Ungültige JSON-Syntax: {e}")
            self.status_var.set("Template-Validierung: JSON-Syntax-Fehler")
        except Exception as e:
            messagebox.showerror("Fehler", f"Validierungsfehler: {e}")
            self.status_var.set("Template-Validierung: Fehler")

    def demo_generation(self):
        """Simuliert eine Kapitel-Generierung"""
        try:
            json_str = self.template_text.get(1.0, tk.END)
            template = json.loads(json_str)

            # Demo-Kapitel generieren
            book_title = template["input"]["book"]["title"]
            chapter_title = template["input"]["chapter"]["title"]
            character_name = template["input"]["characters"]["main_character"]["name"]

            demo_chapter = f"""# {chapter_title}

Es war ein wunderschöner Morgen im verzauberten Wald. Die Sonne schien durch die alten Bäume und warf goldene Lichtflecken auf den moosbedeckten Boden. {character_name} stand am Rande des Waldes und blickte neugierig in die geheimnisvolle Welt vor sich.

"Was für ein Abenteuer wartet dort auf mich?", dachte {character_name} und trat mutig in den Wald hinein. Die Luft war erfüllt vom Duft wilder Blumen und dem sanften Rauschen der Blätter.

Plötzlich hörte {character_name} ein leises Zwitschern. Ein kleiner Vogel mit glitzernden Federn saß auf einem Ast und schaute sie freundlich an. Es war, als würde er sie willkommen heißen.

"Hallöchen!", rief {character_name} dem Vogel zu. "Kannst du mir den Weg zeigen?"

Der Vogel zwitscherte fröhlich und flog ein Stück voraus. {character_name} folgte ihm durch den Wald und entdeckte dabei wunderschöne Dinge: leuchtende Pilze, die wie kleine Laternen aussahen, und einen kleinen Bach, der glitzernd über Steine plätscherte.

---

**Demo-Generierung abgeschlossen**
- Buch: {book_title}
- Kapitel: {chapter_title}
- Hauptfigur: {character_name}
- Wörter: ~150 (Demo-Version)

*Hinweis: Dies ist eine Demo-Generierung. Die echte KI-Generierung würde ein vollständiges Kapitel mit 800+ Wörtern erstellen.*
"""

            self.demo_text.delete(1.0, tk.END)
            self.demo_text.insert(1.0, demo_chapter)

            self.status_var.set(f"Demo-Kapitel generiert: {chapter_title}")
            messagebox.showinfo("Demo-Erfolg", "Demo-Kapitel erfolgreich generiert!")

        except json.JSONDecodeError as e:
            messagebox.showerror("JSON-Fehler", f"Ungültige JSON-Syntax: {e}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Demo-Generierungsfehler: {e}")


def main():
    root = tk.Tk()

    # Fenster-Management
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()

    # Zentriere das Fenster
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Nach dem Laden wieder normal
    root.after(1000, lambda: root.attributes("-topmost", False))

    app = TestBookWriterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
