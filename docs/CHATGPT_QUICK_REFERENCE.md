# One Click Book Writer - Quick Reference für ChatGPT

## 🚀 **Schnellstart-Befehle**

### **Pipeline ausführen:**
```bash
python prompt_router.py data/generate_chapter_full_extended.json --chapter 1
```

### **GUI starten:**
```bash
bookwriter-gui
```

### **Tests ausführen:**
```bash
python tests/smoke_test.py
```

### **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

## 📋 **Wichtige Dateien**

| Datei | Zweck |
|-------|-------|
| `prompt_router.py` | Haupt-Pipeline |
| `simple_gui.py` | GUI-Anwendung |
| `compiler/prompt_compiler.py` | JSON → Prompt |
| `engine/openai_adapter.py` | OpenAI Integration |
| `engine/claude_adapter.py` | Claude Integration |
| `utils/quality_evaluator.py` | Qualitätsbewertung |
| `schema/prompt_frame.schema.json` | JSON-Validierung |

## 🔧 **Kern-Klassen**

### **PromptRouter** (Haupt-Controller)
```python
from prompt_router import PromptRouter

router = PromptRouter()
result = router.run_full_pipeline(
    prompt_frame_path="data/input.json",
    optimize_with_claude=True,
    chapter_number=1
)
```

### **QualityEvaluator** (Qualitätsbewertung)
```python
from utils.quality_evaluator import QualityEvaluator

evaluator = QualityEvaluator()
score = evaluator.calculate_overall_quality_score(
    text=chapter_text,
    target_words=800,
    target_emotion="wonder",
    target_audience="children",
    language="de"
)
```

### **PromptVersioning** (Versions-Tracking)
```python
from utils.prompt_versioning import PromptVersioning

versioning = PromptVersioning()
hash = versioning.add_version(
    prompt_frame=json_data,
    raw_prompt=prompt_text,
    optimized_prompt=optimized_text,
    chapter_number=1
)
```

## 📊 **JSON-Schema (Minimal)**

```json
{
  "input": {
    "book": {
      "title": "Buchtitel",
      "genre": "Kinderbuch",
      "target_audience": "Kinder 6-10",
      "titles": {
        "de": "Deutscher Titel",
        "en": "English Title"
      }
    },
    "chapter": {
      "number": 1,
      "title": "Kapiteltitel",
      "length_words": 800
    },
    "characters": {
      "main_character": {
        "name": "Charaktername",
        "language_variants": {
          "de": "Deutscher Name",
          "en": "English Name"
        }
      }
    },
    "language": {
      "bilingual_output": true,
      "target_languages": ["de", "en"]
    }
  }
}
```

## 🎯 **Pipeline-Schritte**

1. **Validierung** → JSON-Schema + Struktur-Check
2. **Prompt-Kompilierung** → JSON → KI-Prompt
3. **Claude-Optimierung** → Optional, mit Fallback
4. **GPT-Generierung** → Kapitel-Text erstellen
5. **Bilinguales Parsing** → DE/EN trennen
6. **Qualitätsbewertung** → Automatische Scoring
7. **Datei-Speicherung** → Alle Versionen + Metadaten

## 📈 **Qualitäts-Score (0.0-1.0)**

- **Wortlimit-Compliance** (25%)
- **Kernemotion-Präsenz** (20%)
- **Wiederholungs-Penalty** (15%)
- **Lesbarkeit** (20%)
- **Struktur-Qualität** (20%)

## 🐛 **Häufige Probleme & Lösungen**

### **Import-Fehler:**
```bash
# Problem: ModuleNotFoundError
pip install -r requirements.txt
source .venv/bin/activate
```

### **API-Key-Fehler:**
```bash
# Problem: proxies argument
# Lösung: Adapter bereits aktualisiert
```

### **Schema-Fehler:**
```bash
# Problem: Required fields missing
# Lösung: Schema an neue Struktur angepasst
```

## 📁 **Output-Struktur**

```
output/
├── chapter_1_de.txt          # Deutsche Version
├── chapter_1_en.txt          # Englische Version
├── chapter_1_bilingual.txt   # Kombiniert
├── chapter_1_meta.json       # Metadaten
├── prompt_history.json       # Prompt-Versionen
└── token_usage.json          # API-Nutzung
```

## 🎨 **GUI-Tabs**

1. **Kapitel-Generierung** - JSON-Input, Prompt-Preview, Generation
2. **Story-Entwicklung** - Claude-gestützte Plot-Entwicklung  
3. **Charakter-Entwicklung** - KI-gestützte Charakter-Erstellung

## 🔄 **Entwicklungsworkflow**

1. **JSON-Template erstellen** → `data/`
2. **Pipeline testen** → `python prompt_router.py`
3. **GUI testen** → `bookwriter-gui`
4. **Tests ausführen** → `python tests/smoke_test.py`
5. **Commits** → Pre-commit Hook läuft automatisch

## 📊 **Erfolgreiche Pipeline-Beispiel**

```
INFO: Pipeline erfolgreich für Kapitel 1
📁 Ausgabedateien: {
  'german': 'output/chapter_1_de.txt',
  'english': 'output/chapter_1_en.txt', 
  'bilingual': 'output/chapter_1_bilingual.txt',
  'metadata': 'output/chapter_1_meta.json'
}
🎯 Qualitäts-Score: 0.645
```

---

**Diese Quick-Reference gibt ChatGPT alle wichtigen Informationen für die tägliche Arbeit am Projekt!** ⚡ 