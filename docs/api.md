# One Click Book Writer Framework - API Dokumentation

## Übersicht

Das One Click Book Writer Framework v4.1.3 bietet eine umfassende API für die automatisierte Generierung von Kinderbüchern mit KI-Unterstützung.

## Core Components

### EnhancedPipeline

Die zentrale Orchestrierungskomponente für den Buchgenerierungsprozess.

#### Konstruktor
```python
from core.enhanced_pipeline import EnhancedPipeline

pipeline = EnhancedPipeline()
```

#### Methoden

##### `run_enhanced_pipeline(prompt_frame, enable_optimization=True, enable_ab_testing=True, enable_feedback_collection=True)`

Führt den vollständigen Generierungszyklus durch.

**Parameter:**
- `prompt_frame`: PromptFrame - Eingabe-Daten für die Generierung
- `enable_optimization`: bool - Aktiviert Prompt-Optimierung (Standard: True)
- `enable_ab_testing`: bool - Aktiviert A/B-Testing (Standard: True)
- `enable_feedback_collection`: bool - Aktiviert Feedback-Sammlung (Standard: True)

**Rückgabe:**
- `PipelineResult` - Ergebnis der Pipeline-Ausführung

**Beispiel:**
```python
from core.enhanced_pipeline import EnhancedPipeline
from schema.validate_input import PromptFrame

pipeline = EnhancedPipeline()
prompt_frame = PromptFrame(
    title="Das magische Abenteuer",
    age_group="children",
    genre="fantasy",
    word_count=500
)

result = pipeline.run_enhanced_pipeline(
    prompt_frame=prompt_frame,
    enable_optimization=True,
    enable_ab_testing=True,
    enable_feedback_collection=True
)
```

##### `run_batch_pipeline(prompt_frames, options=None)`

Führt Batch-Generierung für mehrere Prompt-Frames durch.

**Parameter:**
- `prompt_frames`: List[PromptFrame] - Liste von Eingabe-Daten
- `options`: dict - Optionale Konfiguration

**Rückgabe:**
- `List[PipelineResult]` - Liste der Ergebnisse

### FeedbackIntelligence

Analysiert und verarbeitet User-Feedback automatisch.

#### Methoden

##### `analyze_feedback(feedback_data)`

Analysiert Feedback-Daten und extrahiert Insights.

**Parameter:**
- `feedback_data`: dict - Feedback-Daten

**Rückgabe:**
- `FeedbackAnalysis` - Analyse-Ergebnis

### PromptOptimizer

Optimiert Prompts mit Claude A/B-Testing.

#### Methoden

##### `optimize_prompt_with_claude(original_prompt, optimization_focus)`

Optimiert einen Prompt mit Claude.

**Parameter:**
- `original_prompt`: str - Ursprünglicher Prompt
- `optimization_focus`: str - Fokus der Optimierung

**Rückgabe:**
- `OptimizationResult` - Optimierungs-Ergebnis

### RobustnessManager

Stellt Systemstabilität und Error-Handling sicher.

#### Methoden

##### `check_system_health()`

Überprüft die System-Gesundheit.

**Rückgabe:**
- `HealthReport` - Gesundheits-Report

## Data Models

### PromptFrame

Eingabe-Daten für die Generierung.

```python
from schema.validate_input import PromptFrame

prompt_frame = PromptFrame(
    title="Buchtitel",
    age_group="children",  # "children", "teens", "adults"
    genre="fantasy",       # "fantasy", "adventure", "educational"
    word_count=500,        # Ziel-Wortanzahl
    language="de",         # "de", "en", "bilingual"
    theme="friendship",    # Optional: spezifisches Thema
    characters=["Held", "Freund"],  # Optional: Charaktere
    setting="Wald"         # Optional: Setting
)
```

### PipelineResult

Ergebnis der Pipeline-Ausführung.

```python
class PipelineResult:
    generation_result: GenerationResult
    evaluation_result: EvaluationResult
    optimization_result: Optional[OptimizationResult]
    ab_test_result: Optional[ABTestResult]
    feedback_entries: List[FeedbackEntry]
    compliance_status: str
    total_cost: float
    execution_time: float
```

### GenerationResult

Ergebnis der Text-Generierung.

```python
class GenerationResult:
    content: Dict[str, str]  # {"de": "Deutscher Text", "en": "English text"}
    word_count: int
    quality_score: float
    metadata: Dict[str, Any]
```

## Error Handling

Das Framework verwendet ein robustes Error-Handling-System:

```python
try:
    result = pipeline.run_enhanced_pipeline(prompt_frame)
    if result.compliance_status == "failed":
        print(f"Pipeline fehlgeschlagen: {result.error_message}")
    else:
        print(f"Erfolgreich generiert: {result.generation_result.word_count} Wörter")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
```

## Konfiguration

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Datenbank (optional)
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-key"

# Logging
export LOG_LEVEL="INFO"
```

### Pipeline Configuration

```python
from core.enhanced_pipeline import EnhancedPipeline

# Pipeline mit benutzerdefinierten Einstellungen
pipeline = EnhancedPipeline(
    max_retries=3,
    timeout=30,
    quality_threshold=0.7
)
```

## Beispiele

### Einfache Generierung

```python
from core.enhanced_pipeline import EnhancedPipeline
from schema.validate_input import PromptFrame

# Pipeline initialisieren
pipeline = EnhancedPipeline()

# Prompt-Frame erstellen
prompt_frame = PromptFrame(
    title="Der kleine Drache",
    age_group="children",
    genre="fantasy",
    word_count=300
)

# Generierung ausführen
result = pipeline.run_enhanced_pipeline(prompt_frame)

# Ergebnis verarbeiten
if result.compliance_status != "failed":
    german_text = result.generation_result.content["de"]
    english_text = result.generation_result.content["en"]
    print(f"Deutsch: {german_text}")
    print(f"English: {english_text}")
```

### Batch-Generierung

```python
# Mehrere Bücher generieren
prompt_frames = [
    PromptFrame(title="Abenteuer im Wald", age_group="children", genre="adventure", word_count=400),
    PromptFrame(title="Mathe ist cool", age_group="children", genre="educational", word_count=350),
    PromptFrame(title="Freundschaft", age_group="teens", genre="drama", word_count=600)
]

results = pipeline.run_batch_pipeline(prompt_frames)

for i, result in enumerate(results):
    if result.compliance_status != "failed":
        print(f"Buch {i+1}: {result.generation_result.word_count} Wörter")
```

### Mit Feedback-Integration

```python
# Generierung mit Feedback-Sammlung
result = pipeline.run_enhanced_pipeline(
    prompt_frame,
    enable_feedback_collection=True
)

# Feedback analysieren
from core.feedback_intelligence import FeedbackIntelligence

feedback_intelligence = FeedbackIntelligence()
analysis = feedback_intelligence.analyze_feedback(result.feedback_entries)

print(f"Feedback-Score: {analysis.overall_score}")
print(f"Verbesserungsvorschläge: {analysis.suggestions}")
```

## Best Practices

1. **Error Handling**: Immer try-catch Blöcke verwenden
2. **Resource Management**: Pipeline-Instanzen wiederverwenden
3. **Batch Processing**: Für mehrere Bücher Batch-Methoden verwenden
4. **Quality Gates**: Compliance-Status immer prüfen
5. **Cost Monitoring**: Kosten überwachen mit `total_cost`

## Troubleshooting

### Häufige Probleme

1. **API Key Fehler**: Überprüfen Sie die Environment Variables
2. **Timeout Fehler**: Erhöhen Sie die Timeout-Werte
3. **Quality Gate Failures**: Überprüfen Sie die Eingabe-Parameter
4. **Memory Issues**: Reduzieren Sie Batch-Größen

### Debug-Modus

```python
import logging
logging.basicConfig(level=logging.DEBUG)

pipeline = EnhancedPipeline()
# Debug-Informationen werden jetzt ausgegeben
```

## Versionierung

- **v4.1.3**: Aktuelle Version mit vollständiger API-Dokumentation
- **v4.0.0**: Major Release mit Enhanced Pipeline
- **v3.x**: Legacy-Versionen

## Support

Bei Fragen zur API:
- GitHub Issues: [Repository Issues](https://github.com/your-repo/one-click-book-writer/issues)
- Dokumentation: [User Guide](docs/user-guide.md)
- Beispiele: [Examples Directory](examples/) 