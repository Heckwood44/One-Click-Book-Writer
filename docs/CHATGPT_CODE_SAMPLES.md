# One Click Book Writer - Code Samples für ChatGPT

## 🚀 **Grundlegende Verwendung**

### **1. Pipeline ausführen**
```python
from prompt_router import PromptRouter

# Router initialisieren
router = PromptRouter()

# Pipeline ausführen
result = router.run_full_pipeline(
    prompt_frame_path="data/generate_chapter_full_extended.json",
    optimize_with_claude=True,
    chapter_number=1
)

# Ergebnis prüfen
if result["success"]:
    print(f"✅ Pipeline erfolgreich für Kapitel {result['chapter_number']}")
    print(f"📁 Ausgabedateien: {result['output_files']}")
    print(f"🎯 Qualitäts-Score: {result['quality_evaluation']['overall_bilingual_score']}")
else:
    print(f"❌ Pipeline fehlgeschlagen: {result['errors']}")
```

### **2. JSON-Template erstellen**
```python
import json

# Neues Kapitel-Template
chapter_template = {
    "input": {
        "book": {
            "title": "Die magische Bibliothek",
            "genre": "Fantasy",
            "target_audience": "Jugendliche 12-16",
            "titles": {
                "de": "Die magische Bibliothek",
                "en": "The Magical Library"
            }
        },
        "chapter": {
            "number": 2,
            "title": "Das verborgene Buch",
            "length_words": 1200
        },
        "characters": {
            "main_character": {
                "name": "Luna",
                "language_variants": {
                    "de": "Luna",
                    "en": "Luna"
                },
                "description": "Ein 14-jähriges Mädchen mit magischen Fähigkeiten",
                "personality": "Neugierig, mutig, aber manchmal unsicher"
            }
        },
        "scene": {
            "setting": "Eine alte Bibliothek mit hohen Regalen",
            "time": "Später Nachmittag",
            "atmosphere": "Mystisch und geheimnisvoll"
        },
        "plot": {
            "main_event": "Luna entdeckt ein verstecktes Buch",
            "conflict": "Das Buch ist magisch und reagiert auf ihre Berührung"
        },
        "style": {
            "dialogue_style": "Natürlich und jugendlich",
            "pacing": "Spannungsvoll mit ruhigen Momenten"
        },
        "emotions": {
            "primary_emotion": "wonder",
            "secondary_emotions": ["excitement", "curiosity"]
        },
        "language": {
            "bilingual_output": True,
            "target_languages": ["de", "en"],
            "bilingual_sequence": "de_first"
        }
    }
}

# Template speichern
with open("data/new_chapter.json", "w", encoding="utf-8") as f:
    json.dump(chapter_template, f, indent=2, ensure_ascii=False)
```

## 🔧 **Erweiterte Features**

### **3. Qualitätsbewertung manuell**
```python
from utils.quality_evaluator import QualityEvaluator

# Evaluator initialisieren
evaluator = QualityEvaluator()

# Text bewerten
chapter_text = """
Luna stand vor dem hohen Bücherregal und spürte, wie ihr Herz vor Aufregung klopfte. 
Die alte Bibliothek war voller Geheimnisse, und sie wusste, dass heute etwas Besonderes 
passieren würde. Vorsichtig streckte sie ihre Hand aus und berührte ein Buch, das 
anders aussah als alle anderen.
"""

# Qualitäts-Score berechnen
score = evaluator.calculate_overall_quality_score(
    text=chapter_text,
    target_words=800,
    target_emotion="wonder",
    target_audience="children",
    language="de"
)

print(f"Gesamt-Score: {score['overall_score']}")
print(f"Qualitätsstufe: {score['quality_level']}")
print(f"Verbesserungsvorschläge: {score['improvement_suggestions']}")
```

### **4. Prompt-Versionierung**
```python
from utils.prompt_versioning import PromptVersioning

# Versioning initialisieren
versioning = PromptVersioning()

# Neue Version hinzufügen
hash = versioning.add_version(
    prompt_frame=chapter_template,
    raw_prompt="Original prompt text...",
    optimized_prompt="Optimized prompt text...",
    chapter_number=2,
    language="de"
)

print(f"Neue Version hinzugefügt: {hash}")

# Statistiken abrufen
stats = versioning.get_statistics()
print(f"Gesamtversionen: {stats['total_versions']}")
print(f"Optimierte Versionen: {stats['optimized_versions']}")
print(f"Bilinguale Versionen: {stats['bilingual_versions']}")
```

### **5. Token-Logging**
```python
from utils.token_logging import TokenLogger

# Logger initialisieren
logger = TokenLogger()

# API-Call loggen
logger.log_api_call(
    provider="openai",
    model="gpt-4",
    tokens=1500,
    call_type="chapter_generation",
    input_tokens=500,
    output_tokens=1000
)

# Nutzungszusammenfassung
summary = logger.get_usage_summary()
print(f"Gesamtaufrufe: {summary['total_calls']}")
print(f"Gesamttokens: {summary['total_tokens']}")
print(f"Gesamtkosten: ${summary['total_cost_usd']}")

# Budget-Warnungen
alerts = logger.get_budget_alerts(budget_limit_usd=10.0)
for alert in alerts:
    print(f"⚠️ {alert}")
```

### **6. User Feedback**
```python
from utils.user_feedback import UserFeedback

# Feedback-System initialisieren
feedback = UserFeedback()

# Neues Feedback hinzufügen
feedback.add_feedback(
    chapter_number=1,
    rating=4,
    comment="Sehr schöne Geschichte, aber etwas zu kurz",
    language="de",
    quality_score=0.645
)

# Feedback-Zusammenfassung
summary = feedback.get_feedback_summary()
print(f"Durchschnittliches Rating: {summary['average_rating']}")
print(f"Gesamtfeedback: {summary['total_feedback']}")

# Verbesserungsvorschläge
suggestions = feedback.generate_improvement_suggestions()
for suggestion in suggestions:
    print(f"💡 {suggestion}")
```

## 🎨 **GUI-Integration**

### **7. GUI-Event-Handler**
```python
import tkinter as tk
from tkinter import ttk
import json

class ChapterGeneratorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("One Click Book Writer")
        self.setup_ui()
    
    def setup_ui(self):
        # JSON-Editor
        self.json_frame = ttk.LabelFrame(self.root, text="JSON Input")
        self.json_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.json_text = tk.Text(self.json_frame, height=15)
        self.json_text.pack(fill="both", expand=True)
        
        # Buttons
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(self.button_frame, text="Validieren", command=self.validate_json).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Generieren", command=self.generate_chapter).pack(side="left", padx=5)
        
        # Ergebnis-Anzeige
        self.result_frame = ttk.LabelFrame(self.root, text="Ergebnis")
        self.result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_text = tk.Text(self.result_frame, height=10)
        self.result_text.pack(fill="both", expand=True)
    
    def validate_json(self):
        try:
            json_data = json.loads(self.json_text.get("1.0", tk.END))
            # Validierung durchführen
            from schema.validate_input import validate_json_schema
            is_valid, message = validate_json_schema(json_data, "schema/prompt_frame.schema.json")
            
            if is_valid:
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", "✅ JSON ist gültig!")
            else:
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", f"❌ Validierungsfehler: {message}")
        except json.JSONDecodeError as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", f"❌ JSON-Syntax-Fehler: {e}")
    
    def generate_chapter(self):
        try:
            json_data = json.loads(self.json_text.get("1.0", tk.END))
            
            # Pipeline ausführen
            from prompt_router import PromptRouter
            router = PromptRouter()
            
            # Temporäre Datei speichern
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                temp_file = f.name
            
            result = router.run_full_pipeline(temp_file, chapter_number=1)
            
            if result["success"]:
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", f"✅ Kapitel generiert!\n")
                self.result_text.insert(tk.END, f"📁 Dateien: {result['output_files']}\n")
                self.result_text.insert(tk.END, f"🎯 Score: {result['quality_evaluation']['overall_bilingual_score']}")
            else:
                self.result_text.delete("1.0", tk.END)
                self.result_text.insert("1.0", f"❌ Fehler: {result['errors']}")
                
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", f"❌ Fehler: {e}")
    
    def run(self):
        self.root.mainloop()

# GUI starten
if __name__ == "__main__":
    app = ChapterGeneratorGUI()
    app.run()
```

## 🧪 **Testing**

### **8. Custom Test erstellen**
```python
import unittest
from prompt_router import PromptRouter
from utils.quality_evaluator import QualityEvaluator

class TestChapterGeneration(unittest.TestCase):
    def setUp(self):
        self.router = PromptRouter()
        self.evaluator = QualityEvaluator()
    
    def test_pipeline_execution(self):
        """Testet die komplette Pipeline"""
        result = self.router.run_full_pipeline(
            "data/generate_chapter_full_extended.json",
            chapter_number=1
        )
        
        self.assertTrue(result["success"])
        self.assertIn("output_files", result)
        self.assertIn("quality_evaluation", result)
    
    def test_quality_evaluation(self):
        """Testet die Qualitätsbewertung"""
        test_text = "Ein Testtext mit ausreichender Länge für die Qualitätsbewertung."
        
        score = self.evaluator.calculate_overall_quality_score(
            text=test_text,
            target_words=50,
            target_emotion="wonder",
            target_audience="children",
            language="de"
        )
        
        self.assertIsInstance(score["overall_score"], float)
        self.assertGreaterEqual(score["overall_score"], 0.0)
        self.assertLessEqual(score["overall_score"], 1.0)

if __name__ == "__main__":
    unittest.main()
```

### **9. Batch-Verarbeitung**
```python
import concurrent.futures
from pathlib import Path
import json

def process_chapter(chapter_data, chapter_number):
    """Verarbeitet ein einzelnes Kapitel"""
    from prompt_router import PromptRouter
    
    router = PromptRouter()
    
    # Temporäre Datei erstellen
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(chapter_data, f, indent=2, ensure_ascii=False)
        temp_file = f.name
    
    try:
        result = router.run_full_pipeline(temp_file, chapter_number=chapter_number)
        return {
            "chapter_number": chapter_number,
            "success": result["success"],
            "quality_score": result.get("quality_evaluation", {}).get("overall_bilingual_score", 0.0),
            "errors": result.get("errors", [])
        }
    finally:
        # Temporäre Datei löschen
        Path(temp_file).unlink()

def batch_generate_chapters(chapters_data):
    """Verarbeitet mehrere Kapitel parallel"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Kapitel parallel verarbeiten
        future_to_chapter = {
            executor.submit(process_chapter, chapter_data, i+1): i+1
            for i, chapter_data in enumerate(chapters_data)
        }
        
        for future in concurrent.futures.as_completed(future_to_chapter):
            chapter_number = future_to_chapter[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Kapitel {chapter_number}: {'✅' if result['success'] else '❌'} (Score: {result['quality_score']:.3f})")
            except Exception as e:
                print(f"Kapitel {chapter_number}: ❌ Fehler - {e}")
                results.append({
                    "chapter_number": chapter_number,
                    "success": False,
                    "quality_score": 0.0,
                    "errors": [str(e)]
                })
    
    return results

# Beispiel für Batch-Verarbeitung
chapters = [
    {
        "input": {
            "book": {"title": "Test Buch 1", "genre": "Kinderbuch"},
            "chapter": {"number": 1, "title": "Kapitel 1", "length_words": 800},
            "language": {"bilingual_output": True, "target_languages": ["de", "en"]}
        }
    },
    {
        "input": {
            "book": {"title": "Test Buch 2", "genre": "Kinderbuch"},
            "chapter": {"number": 2, "title": "Kapitel 2", "length_words": 800},
            "language": {"bilingual_output": True, "target_languages": ["de", "en"]}
        }
    }
]

results = batch_generate_chapters(chapters)
print(f"\nBatch abgeschlossen: {sum(1 for r in results if r['success'])}/{len(results)} erfolgreich")
```

---

**Diese Code-Samples zeigen ChatGPT, wie man praktisch mit dem One Click Book Writer Projekt arbeitet!** 🚀 