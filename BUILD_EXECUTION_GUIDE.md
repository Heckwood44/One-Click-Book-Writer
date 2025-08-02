# One Click Book Writer – Build & Execution Guide

## 🎯 Überblick

Dieses Projekt implementiert eine vollständige **KI-gestützte Buchgenerierung Pipeline** mit zweistufiger KI-Orchestrierung:

- **Claude (claude-3-opus)**: Prompt-Design, Struktur-, Emotions- und Stiloptimierung
- **ChatGPT (OpenAI GPT-4)**: Generierung des eigentlichen Kapiteltexts
- **Agent/Orchestrator**: Steuerung, Routing, Validierung, Fallbacks und Ausgabe

## 🚀 Schnellstart

### 1. Environment Setup
```bash
# Virtual Environment aktivieren
cd /Users/tonyhegewald/Entwicklung/Projects/one-click-book-writer
source venv/bin/activate

# API Keys prüfen
python key_check.py
```

### 2. Pipeline ausführen
```bash
# Standard-Pipeline (ohne Claude-Optimierung)
python build_and_execute.py

# Pipeline mit Claude-Prompt-Optimierung
python build_and_execute.py --optimize

# Mit benutzerdefinierten Dateien
python build_and_execute.py --json-file data/my_chapter.json --output output/my_result.txt
```

## 📋 Vollständige Pipeline

### Schritt 1: JSON-PromptFrame laden und validieren
```python
# Lädt data/generate_chapter_full_extended.json
# Validiert gegen schema/prompt_frame.schema.json
prompt_frame = pipeline.load_prompt_frame(json_file)
is_valid = pipeline.validate_prompt_frame(prompt_frame)
```

### Schritt 2: Prompt kompilieren
```python
# Basis-Prompt mit compiler/prompt_compiler.py
base_prompt = compile_prompt_for_chatgpt(prompt_frame)

# Optional: Claude-Optimierung
if optimize_with_claude:
    optimized_prompt = pipeline.optimize_prompt_with_claude(base_prompt, prompt_frame)
```

### Schritt 3: Kapiteltext mit ChatGPT generieren
```python
# Verwendet OpenAI GPT-4 für Textgenerierung
chapter_text = pipeline.generate_chapter(prompt)
```

### Schritt 4: Ausgabe speichern
```python
# Speichert in output/chapter_result.txt
# Metadaten in output/chapter_result.json
saved_file = pipeline.save_output(chapter_text, metadata)
```

## 🔧 API Key Management

### key_check.py Modul
```python
from key_check import APIKeyChecker

checker = APIKeyChecker()

# Status prüfen
status = checker.get_status()
# {'openai_available': True, 'claude_available': True}

# Funktionalität prüfen
can_generate = checker.can_generate_chapters()  # OpenAI
can_optimize = checker.can_optimize_prompts()   # Claude

# Detaillierter Bericht
report = checker.get_validation_report()
```

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 📁 Projektstruktur

```
one-click-book-writer/
├── build_and_execute.py          # Haupt-Pipeline
├── key_check.py                  # API Key Validierung
├── simple_gui.py                 # GUI-Anwendung
├── data/
│   └── generate_chapter_full_extended.json  # Standard-PromptFrame
├── schema/
│   └── prompt_frame.schema.json  # JSON Schema
├── compiler/
│   └── prompt_compiler.py        # Prompt-Kompilierung
├── output/
│   ├── chapter_result.txt        # Generierter Text
│   └── chapter_result.json       # Metadaten
└── .env                          # API Keys
```

## 🎮 Kommandozeilen-Optionen

### build_and_execute.py
```bash
python build_and_execute.py [OPTIONS]

Options:
  --json-file JSON_FILE    JSON-PromptFrame Datei
  --optimize               Prompt mit Claude optimieren
  --output OUTPUT          Ausgabedatei
  --verbose                Detaillierte Ausgabe
  -h, --help               Hilfe anzeigen
```

### Beispiele
```bash
# Standard-Pipeline
python build_and_execute.py

# Mit Claude-Optimierung
python build_and_execute.py --optimize

# Benutzerdefinierte Dateien
python build_and_execute.py \
  --json-file data/my_chapter.json \
  --output output/my_result.txt \
  --optimize

# Detaillierte Ausgabe
python build_and_execute.py --verbose
```

## 📊 Ausgabe-Format

### Kapiteltext (chapter_result.txt)
```
Kapitel 1: Der erste Flug

Hoch oben auf dem Felsvorsprung der gemütlichen Drachenhöhle stand Feuerherz...
[Vollständiger generierter Kapiteltext]
```

### Metadaten (chapter_result.json)
```json
{
  "generated_at": "2025-08-02T21:30:42.951233",
  "pipeline_version": "1.0.0",
  "optimization_used": false,
  "chapter_info": {
    "number": 1,
    "title": "Der erste Flug",
    "narrative_purpose": "Einführung der Hauptfigur...",
    "position_in_arc": "setup",
    "length_words": 800
  },
  "book_info": {
    "title": "Die Abenteuer des kleinen Drachen",
    "genre": "Kinderbuch",
    "target_audience": "Kinder im Alter von 6-10 Jahren"
  },
  "word_count": 471
}
```

## 🔍 Monitoring & Logging

### Logging-Level
```python
import logging

# INFO (Standard)
logging.basicConfig(level=logging.INFO)

# DEBUG (Detailliert)
logging.basicConfig(level=logging.DEBUG)
```

### Pipeline-Status
```python
# Erfolgreiche Ausführung
{
    'success': True,
    'output_file': 'output/chapter_result.txt',
    'chapter_text': '...',
    'metadata': {...},
    'duration_seconds': 20.48,
    'word_count': 471
}

# Fehlerhafte Ausführung
{
    'success': False,
    'error': 'Fehlermeldung',
    'duration_seconds': 5.23
}
```

## 🛠️ Fehlerbehebung

### Häufige Probleme

#### 1. API Key Fehler
```bash
# Prüfe API Keys
python key_check.py

# Lösche .env und erstelle neu
rm .env
echo "OPENAI_API_KEY=dein-openai-key" > .env
echo "ANTHROPIC_API_KEY=dein-claude-key" >> .env
```

#### 2. Bibliotheks-Versionen
```bash
# Aktualisiere Bibliotheken
pip install --upgrade openai anthropic

# Prüfe Versionen
pip show openai anthropic
```

#### 3. Schema-Validierung
```bash
# Prüfe JSON-Format
python -c "import json; json.load(open('data/generate_chapter_full_extended.json'))"

# Validiere gegen Schema
python -c "from schema.validate_input import validate_json_schema; print(validate_json_schema(json.load(open('data/generate_chapter_full_extended.json')), 'schema/prompt_frame.schema.json'))"
```

## 🎯 Erweiterte Features

### Batch-Verarbeitung
```python
# Mehrere Kapitel generieren
for i in range(1, 6):
    pipeline.run_pipeline(
        json_file=f"data/chapter_{i}.json",
        output_file=f"output/chapter_{i}.txt"
    )
```

### Custom Prompt-Optimierung
```python
# Eigene Claude-Prompts
def custom_optimization(base_prompt, prompt_frame):
    # Implementiere eigene Optimierungslogik
    return optimized_prompt
```

### GUI-Integration
```python
# Pipeline in GUI einbinden
from build_and_execute import OneClickBookWriterPipeline

pipeline = OneClickBookWriterPipeline()
result = pipeline.run_pipeline(optimize_prompt=True)
```

## 📈 Performance-Metriken

### Typische Ausführungszeiten
- **Basis-Pipeline**: ~20-30 Sekunden
- **Mit Claude-Optimierung**: ~50-60 Sekunden
- **Wortanzahl**: 400-600 Wörter pro Kapitel

### Ressourcenverbrauch
- **API-Calls**: 1-2 pro Pipeline-Durchlauf
- **Speicher**: <100MB
- **CPU**: Minimal (hauptsächlich I/O)

## 🔐 Sicherheit

### API Key Schutz
- Keys werden nur aus `.env` geladen
- Keine Hardcoding von Keys
- Validierung des Key-Formats
- Sichere Übertragung über HTTPS

### Datenvalidierung
- JSON Schema-Validierung
- Input-Sanitization
- Fehlerbehandlung für alle API-Calls

## 📚 Weiterführende Dokumentation

- [OpenAI API Dokumentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [JSON Schema Spezifikation](https://json-schema.org/)
- [Python Logging](https://docs.python.org/3/library/logging.html)

---

**One Click Book Writer v1.0.0**  
*KI-gestützte Buchgenerierung mit zweistufiger Orchestrierung* 