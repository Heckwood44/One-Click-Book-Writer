# One Click Book Writer - Vollständige Projekt-Übersicht für ChatGPT

## 🎯 **Projekt-Ziel**
Ein KI-gestütztes Tool zur automatisierten Generierung von Buchkapiteln aus strukturierten JSON-Eingaben, mit bilingualer Unterstützung (Deutsch/Englisch) und umfassender Qualitätsbewertung.

## 🏗️ **Architektur-Übersicht**

### **Kern-Komponenten:**
1. **Prompt Compiler** (`compiler/prompt_compiler.py`) - Transformiert JSON in KI-Prompts
2. **AI Adapter** (`engine/openai_adapter.py`, `engine/claude_adapter.py`) - API-Integration
3. **Pipeline Orchestrator** (`prompt_router.py`) - Haupt-Controller
4. **Quality Evaluator** (`utils/quality_evaluator.py`) - Automatische Bewertung
5. **GUI** (`simple_gui.py`) - Benutzeroberfläche

### **Datenfluss:**
```
JSON Input → Prompt Compiler → Claude (Optional) → GPT-4 → Bilingual Parser → Quality Evaluator → Output Files
```

## 📁 **Projekt-Struktur**
```
one-click-book-writer/
├── compiler/           # Prompt-Kompilierung
├── engine/            # AI-Adapter (OpenAI, Claude)
├── schema/            # JSON-Validierung
├── utils/             # Hilfsmodule (Versioning, Token-Logging, etc.)
├── gui/               # Benutzeroberfläche
├── output/            # Generierte Kapitel
├── data/              # JSON-Templates
├── tests/             # Test-Suite
├── docs/              # Dokumentation
├── prompt_router.py   # Haupt-Pipeline
├── simple_gui.py      # GUI-Anwendung
└── requirements.txt   # Dependencies
```

## 🔧 **Technische Details**

### **JSON-Schema** (`schema/prompt_frame.schema.json`)
```json
{
  "input": {
    "book": {
      "title": "string",
      "genre": "string",
      "target_audience": "string",
      "titles": {"de": "string", "en": "string"}
    },
    "chapter": {
      "number": "integer",
      "title": "string",
      "length_words": "integer"
    },
    "characters": {
      "main_character": {
        "name": "string",
        "language_variants": {"de": "string", "en": "string"}
      }
    },
    "scene": {"setting": "string", "time": "string"},
    "plot": {"main_event": "string", "conflict": "string"},
    "style": {"dialogue_style": "string", "pacing": "string"},
    "emotions": {"primary_emotion": "string"},
    "language": {
      "bilingual_output": "boolean",
      "target_languages": ["de", "en"]
    }
  }
}
```

### **AI-Integration**
- **OpenAI GPT-4**: Hauptgenerator für Kapitel
- **Anthropic Claude**: Optional für Prompt-Optimierung
- **Token-Logging**: Kostenverfolgung
- **Fallback-Mechanismen**: Robuste Fehlerbehandlung

### **Bilinguale Features**
- **Simultane Generierung**: DE + EN in einem API-Call
- **Kulturelle Anpassung**: Sprache-spezifische Inhalte
- **Separate Dateien**: `chapter_X_de.txt`, `chapter_X_en.txt`
- **Kombinierte Version**: `chapter_X_bilingual.txt`

## 🚀 **Haupt-Pipeline** (`prompt_router.py`)

### **Schritte:**
1. **Validierung**: JSON-Schema + Struktur-Check
2. **Prompt-Kompilierung**: JSON → KI-Prompt
3. **Claude-Optimierung**: Optional, mit Fallback
4. **GPT-Generierung**: Kapitel-Text erstellen
5. **Bilinguales Parsing**: DE/EN trennen
6. **Qualitätsbewertung**: Automatische Scoring
7. **Datei-Speicherung**: Alle Versionen + Metadaten

### **Qualitäts-Score (0.0-1.0):**
- **Wortlimit-Compliance** (25%)
- **Kernemotion-Präsenz** (20%)
- **Wiederholungs-Penalty** (15%)
- **Lesbarkeit** (20%)
- **Struktur-Qualität** (20%)

## 📊 **Erweiterte Features**

### **Prompt Versioning** (`utils/prompt_versioning.py`)
- **Hash-basierte Tracking**: SHA-256 für Prompts
- **Versions-Historie**: Alle Änderungen dokumentiert
- **Diff-Generierung**: Unterschiede zwischen Versionen
- **Metadaten-Export**: Integration in `chapter_meta.json`

### **Token Logging** (`utils/token_logging.py`)
- **API-Nutzung**: Calls, Tokens, Kosten
- **Provider-Tracking**: OpenAI vs. Anthropic
- **Budget-Alerts**: Kostenwarnungen
- **Kosten-Schätzung**: Vor API-Calls

### **User Feedback** (`utils/user_feedback.py`)
- **Rating-System**: 1-5 Sterne
- **Kommentare**: Freitext-Feedback
- **Qualitäts-Analyse**: Verbesserungsvorschläge
- **Trend-Tracking**: Entwicklung über Zeit

## 🧪 **Testing & CI/CD**

### **Smoke Test** (`tests/smoke_test.py`)
```python
def run_minimal_smoke_test():
    # 1. Pipeline-Import testen
    # 2. PromptFrame laden
    # 3. Validierung durchführen
    # 4. Prompt kompilieren
    # 5. Länge prüfen (>100 Zeichen)
```

### **CI/CD Pipeline**
- **GitHub Actions**: Automatische Tests bei Commits
- **Pre-commit Hook**: Lokale Validierung
- **Schema-Updates**: Automatische Validierung

## 🎨 **GUI-Features** (`simple_gui.py`)

### **Haupt-Tabs:**
1. **Kapitel-Generierung**: JSON-Input, Prompt-Preview, Generation
2. **Story-Entwicklung**: Claude-gestützte Plot-Entwicklung
3. **Charakter-Entwicklung**: KI-gestützte Charakter-Erstellung

### **Funktionen:**
- **JSON-Editor**: Validierung + Syntax-Highlighting
- **Prompt-Preview**: Live-Vorschau des kompilierten Prompts
- **API-Key-Management**: Sichere Konfiguration
- **Ergebnis-Anzeige**: Deutsche + Englische Versionen
- **Qualitäts-Metriken**: Automatische Bewertung

## 📈 **Aktuelle Erfolge**

### **Funktionierende Pipeline:**
```
✅ Validierung → ✅ Prompt-Kompilierung → ✅ GPT-Generierung → 
✅ Bilinguales Parsing → ✅ Qualitätsbewertung → ✅ Datei-Speicherung
```

### **Beispiel-Output:**
- **Kapitel:** "Der erste Flug" (Kinderbuch)
- **Qualitäts-Score:** 0.645/1.0 (Gut)
- **Tokens:** 1682 generiert
- **Kosten:** $0.0197
- **Dateien:** DE + EN + Bilingual + Meta

### **Metadaten-Beispiel:**
```json
{
  "chapter_number": 1,
  "prompt_versioning": {
    "total_versions": 7,
    "latest_version_hash": "4f4bc5bb0288c77c"
  },
  "quality_evaluation": {
    "overall_score": 0.645,
    "german_score": 0.623,
    "english_score": 0.667,
    "consistency_score": 0.645
  }
}
```

## 🔧 **Installation & Setup**

### **Dependencies** (`requirements.txt`):
```
openai>=1.0.0
anthropic>=0.7.0
python-dotenv>=1.0.0
jsonschema>=4.0.0
customtkinter>=5.0.0
```

### **Environment Variables** (`.env`):
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### **Shell Aliases** (`~/.zshrc`):
```bash
alias bookwriter-gui="cd /path/to/project && source .venv/bin/activate && python simple_gui.py"
alias bookwriter-pipeline="cd /path/to/project && source .venv/bin/activate && python prompt_router.py"
```

## 🎯 **Nächste Entwicklungsschritte**

### **Sofort umsetzbar:**
1. **GUI-Debugging**: Import-Probleme beheben
2. **Batch-Verarbeitung**: Mehrere Kapitel parallel
3. **Erweiterte Templates**: Verschiedene Genres
4. **Performance-Optimierung**: Caching + Parallelisierung

### **Mittelfristig:**
1. **Web-Interface**: Streamlit-Dashboard
2. **API-Service**: REST-API für Integration
3. **Erweiterte KI-Modelle**: GPT-4o, Claude 3.5
4. **Plotten-Integration**: Automatische Story-Struktur

### **Langfristig:**
1. **Multi-Language**: Weitere Sprachen
2. **Audio-Integration**: Text-zu-Sprache
3. **Illustration-API**: Automatische Bilder
4. **Publishing-Pipeline**: Direkt zu Amazon KDP

## 🐛 **Bekannte Issues & Lösungen**

### **Import-Probleme:**
- **Problem:** `ModuleNotFoundError: No module named 'openai'`
- **Lösung:** `pip install -r requirements.txt` + Virtual Environment

### **API-Key-Fehler:**
- **Problem:** `TypeError: Client.__init__() got unexpected keyword argument 'proxies'`
- **Lösung:** Adapter aktualisiert, `proxies` Parameter entfernt

### **Schema-Validierung:**
- **Problem:** `'story_context' is a required property`
- **Lösung:** Schema an neue JSON-Struktur angepasst

### **GUI-Launch:**
- **Problem:** Falsches Arbeitsverzeichnis
- **Lösung:** Shell-Alias `bookwriter-gui` erstellt

## 📚 **Code-Beispiele**

### **Pipeline-Ausführung:**
```bash
python prompt_router.py data/generate_chapter_full_extended.json --chapter 1
```

### **JSON-Template:**
```json
{
  "input": {
    "book": {
      "title": "Die Abenteuer des kleinen Drachen",
      "genre": "Kinderbuch",
      "target_audience": "Kinder 6-10",
      "titles": {
        "de": "Die Abenteuer des kleinen Drachen",
        "en": "The Little Dragon's Adventures"
      }
    },
    "chapter": {
      "number": 1,
      "title": "Der erste Flug",
      "length_words": 800
    },
    "language": {
      "bilingual_output": true,
      "target_languages": ["de", "en"]
    }
  }
}
```

### **Qualitäts-Evaluator:**
```python
evaluator = QualityEvaluator()
score = evaluator.calculate_overall_quality_score(
    text=chapter_text,
    target_words=800,
    target_emotion="wonder",
    target_audience="children",
    language="de"
)
```

---

**Diese Übersicht gibt ChatGPT alle notwendigen Informationen, um das Projekt vollständig zu verstehen und bei der Weiterentwicklung zu unterstützen!** 🚀 