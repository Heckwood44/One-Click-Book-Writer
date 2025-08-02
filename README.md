# 🚀 One Click Book Writer

**KI-basiertes Tool zur automatisierten Kapitelgenerierung aus strukturierten Promptdaten**

Ein eigenständig ausführbares Tool, das JSON-Eingaben verarbeitet, Claude/GPT-kompatible Prompts generiert und den Kapiteltext als Ausgabe erzeugt.

## ✨ Features

- **Duale AI-Engine-Unterstützung**: Claude (Anthropic) und ChatGPT (OpenAI)
- **Strukturierte Prompt-Kompilation**: JSON-Schema-basierte Eingabevalidierung
- **Mehrschichtige Kontrolle**: Narrative, emotionale und stilistische Ebenen
- **Robuste Fehlerbehandlung**: Retry-Mechanismen und Validierung
- **Flexible Ausgabeformate**: Text + JSON-Metadaten
- **Interaktiver und CLI-Modus**: Für verschiedene Anwendungsfälle

## 🏗️ Architektur

```
one-click-book-writer/
├── compiler/           # Prompt-Kompilierung
├── engine/            # AI-Engine Adapter
├── schema/            # JSON-Schema Validierung
├── gui/               # Benutzeroberfläche (geplant)
├── output/            # Generierte Kapitel
├── data/              # Beispiel-Eingabedaten
├── templates/         # Prompt-Templates
└── docs/              # Dokumentation
```

## 🚀 Installation

1. **Repository klonen:**
```bash
cd /Users/tonyhegewald/Entwicklung/Projects
git clone <repository-url> one-click-book-writer
cd one-click-book-writer
```

2. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

3. **Umgebungsvariablen konfigurieren:**
```bash
cp env.example .env
# Bearbeite .env und füge deine API-Keys hinzu
```

## 🔑 API-Keys konfigurieren

### Anthropic (Claude)
1. Gehe zu [Anthropic Console](https://console.anthropic.com/)
2. Erstelle einen API-Key
3. Füge ihn in `.env` hinzu: `ANTHROPIC_API_KEY=your_key_here`

### OpenAI (ChatGPT)
1. Gehe zu [OpenAI Platform](https://platform.openai.com/api-keys)
2. Erstelle einen API-Key
3. Füge ihn in `.env` hinzu: `OPENAI_API_KEY=your_key_here`

## 📖 Verwendung

### Interaktiver Modus
```bash
python main.py --interactive
```

### Kommandozeilen-Modus
```bash
# Mit Claude
python main.py --input data/generate_chapter_full_extended.json --engine claude

# Mit ChatGPT
python main.py --input data/generate_chapter_full_extended.json --engine chatgpt --output output/my_chapter.txt

# Mit angepassten Parametern
python main.py --input data/generate_chapter_full_extended.json --engine claude --temperature 0.7 --max-tokens 6000
```

### Batch-Verarbeitung (geplant)
```bash
python batch_generate.py --template children_story --chapters 5
```

## 📝 Eingabeformat

Das Tool verwendet ein strukturiertes JSON-Format für die Eingabe:

```json
{
  "input": {
    "chapter": {
      "number": 1,
      "title": "Der erste Flug",
      "narrative_purpose": "Einführung der Hauptfigur",
      "position_in_arc": "setup",
      "length_words": 800
    },
    "book": {
      "title": "Die Abenteuer des kleinen Drachen",
      "genre": "Kinderbuch",
      "target_audience": "Kinder im Alter von 6-10 Jahren"
    },
    "style": {
      "writing_style": "descriptive",
      "tone": "warm",
      "tense": "past",
      "perspective": "third_limited"
    },
    "story_context": {
      "current_scene": "Feuerherz steht am Rande der Höhle...",
      "previous_summary": "Kleiner Drache Feuerherz lebt..."
    },
    "constraints": {
      "structure": "linear",
      "format": "prose",
      "stylistic_dos": ["Verwende einfache Sätze"],
      "forbidden_elements": ["Gewalt"]
    }
  }
}
```

## 🎯 Prompt-Engineering

Das Tool verwendet ein mehrschichtiges Prompt-Engineering-System:

### 1. System Note
```
Ein Weltklasse-Autor ist kein "Schreiberling".
Er ist ein Architekt innerer Räume.
Ein Übersetzer des Unsichtbaren.
```

### 2. Strukturierte Sektionen
- **AUFGABE**: Kapitel-Kontext und Ziel
- **📖 INHALTLICHER KONTEXT**: Story-Hintergrund
- **💡 EMOTIONALE EBENE**: Gefühle und Stimmung
- **✍️ STIL**: Schreibstil und Technik
- **📏 REGELN & FORMAT**: Constraints und Vorgaben

### 3. Modellsteuerung
- Szenenpriorität
- Symbolik-Verwendung
- Emotionalverlauf
- Stilregel-Handhabung

## 📊 Ausgabe

Das Tool generiert:

1. **Kapiteltext** (`.txt`)
2. **Metadaten** (`.json`) mit:
   - Token-Verbrauch
   - Modell-Informationen
   - Generierungsparameter
   - Validierungsergebnisse

## 🔧 Entwicklung

### Projektstruktur erweitern
```bash
# Neue Templates hinzufügen
mkdir templates/new_genre
# Neue Engine-Adapter
mkdir engine/adapters/new_provider
```

### Tests ausführen
```bash
pytest tests/
```

### Code formatieren
```bash
black .
flake8 .
```

## 📚 Templates

Das Tool unterstützt verschiedene Genre-Templates:

- **Kinderbuch**: `templates/children_reimform_prompt.json`
- **Journal**: `templates/journal_reflection_prompt.json`
- **Ratgeber**: `templates/selfhelp_structured_prompt.json`

## 🛠️ Technische Details

### Unterstützte AI-Engines
- **Claude 3 Opus**: Höchste Qualität, längere Kontextfenster
- **GPT-4 Turbo**: Schnelle Generierung, gute Kreativität

### Token-Limits
- Claude 3 Opus: 320.000 Tokens
- GPT-4 Turbo: 128.000 Tokens

### Retry-Mechanismus
- Exponential Backoff bei API-Fehlern
- Automatische Wiederholung bis zu 3x

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Implementiere deine Änderungen
4. Füge Tests hinzu
5. Erstelle einen Pull Request

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

Bei Fragen oder Problemen:
1. Überprüfe die [Dokumentation](docs/)
2. Schaue in die [Issues](issues/)
3. Erstelle ein neues Issue mit detaillierter Beschreibung

---

**Entwickelt mit ❤️ für kreative Autoren und Content Creator** 