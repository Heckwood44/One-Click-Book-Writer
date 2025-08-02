# One Click Book Writer - API Dokumentation

## 📚 **Übersicht**

Das One Click Book Writer System bietet eine vollständige API für die automatisierte Generierung von Kinderbuch-Kapiteln mit bilingualer Unterstützung (Deutsch/Englisch).

## 🔧 **Kern-Komponenten**

### **1. Prompt Router (`prompt_router.py`)**

Die Haupt-Pipeline für die Kapitelgenerierung.

#### **Hauptklasse: `PromptRouter`**

```python
from prompt_router import PromptRouter

router = PromptRouter()
result = router.run_full_pipeline(
    prompt_frame_path="data/generate_chapter_full_extended.json",
    optimize_with_claude=True,
    chapter_number=1
)
```

#### **Methoden:**

- `load_and_validate_prompt_frame(path)` - Lädt und validiert JSON-Input
- `optimize_prompt_with_claude(raw_prompt, prompt_frame)` - Claude-Optimierung
- `generate_chapter_with_gpt(prompt, prompt_frame)` - GPT-4 Generierung
- `parse_bilingual_response(response)` - DE/EN Trennung
- `run_full_pipeline(path, optimize, chapter)` - Vollständige Pipeline

### **2. Prompt Compiler (`compiler/prompt_compiler.py`)**

Kompiliert JSON-Input in AI-Prompts.

#### **Hauptfunktionen:**

```python
from compiler.prompt_compiler import (
    compile_prompt_for_chatgpt,
    validate_prompt_structure,
    generate_prompt_hash,
    get_prompt_metadata
)

# Prompt kompilieren
prompt = compile_prompt_for_chatgpt(prompt_frame)

# Struktur validieren
is_valid = validate_prompt_structure(prompt_frame)

# Hash generieren
prompt_hash = generate_prompt_hash(prompt)
```

### **3. Quality Evaluator (`utils/quality_evaluator.py`)**

Bewertet die Qualität generierter Kapitel.

#### **Hauptklasse: `QualityEvaluator`**

```python
from utils.quality_evaluator import QualityEvaluator

evaluator = QualityEvaluator()
evaluation = evaluator.calculate_overall_quality_score(
    text=chapter_text,
    target_words=800,
    target_emotion="wonder",
    target_audience="children",
    language="de"
)
```

#### **Bewertungskomponenten:**

1. **Wortlimit-Compliance** (25% Gewichtung)
2. **Kernemotion-Präsenz** (20% Gewichtung)
3. **Wiederholungs-Score** (15% Gewichtung)
4. **Lesbarkeit** (20% Gewichtung)
5. **Struktur-Qualität** (20% Gewichtung)

### **4. API Adapter (`engine/`)**

#### **OpenAI Adapter (`engine/openai_adapter.py`)**

```python
from engine.openai_adapter import OpenAIAdapter

adapter = OpenAIAdapter()
if adapter.is_available():
    result = adapter.generate_text(prompt)
```

#### **Claude Adapter (`engine/claude_adapter.py`)**

```python
from engine.claude_adapter import ClaudeAdapter

adapter = ClaudeAdapter()
if adapter.is_available():
    result = adapter.generate_text(prompt)
```

## 📊 **JSON-Schema**

### **PromptFrame-Struktur:**

```json
{
  "input": {
    "book": {
      "title": "Buchtitel",
      "genre": "Kinderbuch",
      "target_audience": "children",
      "theme": "Thema",
      "setting": "Setting",
      "titles": {
        "de": "Deutscher Titel",
        "en": "English Title"
      }
    },
    "chapter": {
      "number": 1,
      "title": "Kapiteltitel",
      "narrative_purpose": "Zweck",
      "position_in_arc": "setup",
      "length_words": 800,
      "titles": {
        "de": "Deutscher Kapiteltitel",
        "en": "English Chapter Title"
      }
    },
    "characters": {
      "main_character": {
        "name": "Name",
        "description": "Beschreibung",
        "personality": "Persönlichkeit",
        "goals": "Ziele",
        "language_variants": {
          "de": {"name": "Deutscher Name"},
          "en": {"name": "English Name"}
        }
      }
    },
    "scene": {
      "setting": "Szenen-Setting",
      "time": "Zeit",
      "atmosphere": "Atmosphäre"
    },
    "plot": {
      "main_event": "Hauptereignis",
      "conflict": "Konflikt",
      "resolution": "Auflösung"
    },
    "style": {
      "tone": "Ton",
      "pacing": "Tempo",
      "dialogue_style": "Dialog-Stil"
    },
    "emotions": {
      "core_emotion": "Kernemotion",
      "emotional_arc": "Emotionaler Bogen"
    },
    "language": {
      "bilingual_output": true,
      "target_languages": ["de", "en"],
      "bilingual_sequence": ["de", "en"]
    }
  }
}
```

## 🚀 **Verwendung**

### **Einfache Kapitelgenerierung:**

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

if result["success"]:
    print(f"✅ Kapitel generiert: {result['output_files']}")
    print(f"🎯 Qualitäts-Score: {result['quality_evaluation']['overall_bilingual_score']}")
else:
    print(f"❌ Fehler: {result['errors']}")
```

### **Batch-Verarbeitung:**

```python
from batch_generate import BatchGenerator

generator = BatchGenerator()
results = generator.generate_batch(
    prompt_frame_path="data/generate_chapter_full_extended.json",
    chapter_numbers=[1, 2, 3],
    optimize_with_claude=True
)
```

## 📈 **Qualitäts-Metriken**

### **Review-Schwellen:**

- **Score ≥ 0.8**: Excellent - Keine Aktion erforderlich
- **Score 0.6-0.79**: Good - Optional Review
- **Score 0.4-0.59**: Fair - Review erforderlich
- **Score < 0.4**: Poor - Kritische Probleme

### **Problem-Flags:**

- `WORTLIMIT_PROBLEM`: Abweichung > 30% vom Ziel
- `EMOTION_PROBLEM`: Kernemotion < 0.5 Score
- `REPETITION_PROBLEM`: Wiederholungen > 40%
- `READABILITY_PROBLEM`: Satzlänge ungeeignet
- `STRUCTURE_PROBLEM`: Absatzstruktur unausgewogen

## 🔧 **Konfiguration**

### **Umgebungsvariablen (.env):**

```bash
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### **Token-Limits:**

- **Claude**: max 4000 Tokens
- **GPT-4**: max 8000 Tokens
- **Kosten**: ~$0.02-0.03 pro Kapitel

## 🧪 **Testing**

### **Smoke Test:**

```bash
python tests/smoke_test.py
```

### **CI/CD:**

- **GitHub Actions**: Automatische Tests bei Commits
- **Pre-commit Hook**: Lokale Tests vor Commits

## 📝 **Output-Format**

### **Generierte Dateien:**

- `chapter_X_de.txt` - Deutsche Version
- `chapter_X_en.txt` - Englische Version
- `chapter_X_bilingual.txt` - Kombinierte Version
- `chapter_X_meta.json` - Metadaten mit Qualitätsbewertung

### **Metadaten-Struktur:**

```json
{
  "chapter_number": 1,
  "prompt_versioning": {
    "total_versions": 2,
    "latest_version_hash": "abc123...",
    "prompt_length": 3290,
    "optimized_length": 2199
  },
  "quality_evaluation": {
    "overall_bilingual_score": 0.624,
    "review_required": true,
    "critical_issues": false,
    "flags": ["WORTLIMIT_PROBLEM"]
  },
  "book_metadata": {
    "book_title": "Titel",
    "genre": "Kinderbuch",
    "is_bilingual": true
  }
}
```

---

**Version**: 2.0.0  
**Letzte Aktualisierung**: 3. August 2025 