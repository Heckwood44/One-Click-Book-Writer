# One Click Book Writer Framework v4.1.3

Ein fortschrittliches Framework für die automatisierte Generierung von Kinderbüchern mit KI-Unterstützung.

## 📊 Test Coverage Status

![Test Coverage](https://img.shields.io/badge/Test%20Coverage-88%25-brightgreen)
![Enhanced Pipeline](https://img.shields.io/badge/Enhanced%20Pipeline-76%25-green)
![Feedback Intelligence](https://img.shields.io/badge/Feedback%20Intelligence-89%25-green)
![Prompt Optimizer](https://img.shields.io/badge/Prompt%20Optimizer-93%25-green)
![Robustness Manager](https://img.shields.io/badge/Robustness%20Manager-93%25-green)

## 🎯 Coverage-Ziele - Alle ÜBERTROFFEN

| Modul | Ziel | Erreicht | Status |
|-------|------|----------|--------|
| `core/enhanced_pipeline.py` | ≥60% | **76%** | ✅ ÜBERTROFFEN |
| `core/feedback_intelligence.py` | ≥70% | **89%** | ✅ ÜBERTROFFEN |
| `core/prompt_optimizer.py` | ≥50% | **93%** | ✅ ÜBERTROFFEN |
| `core/robustness_manager.py` | ≥50% | **93%** | ✅ ÜBERTROFFEN |

**Durchschnittliche Coverage der Zielmodule: 88%** ✅

## 🚀 Features

### Core Components
- **Enhanced Pipeline**: Orchestriert den gesamten Buchgenerierungsprozess
- **Feedback Intelligence**: Analysiert und verarbeitet User-Feedback automatisch
- **Prompt Optimizer**: Optimiert Prompts mit Claude A/B-Testing
- **Robustness Manager**: Stellt Systemstabilität und Error-Handling sicher

### Advanced Features
- **Bilingual Output**: Automatische Generierung in Deutsch und Englisch
- **Age-Appropriate Content**: Constraint-Enforcement für verschiedene Altersgruppen
- **Quality Gates**: Automatische Qualitätsprüfungen und Guardrails
- **CI/CD Integration**: Vollständig automatisierte Test- und Deployment-Pipeline

## 📈 Erreichte Verbesserungen

### Coverage-Verbesserungen
- **Enhanced Pipeline**: 22% → 76% (+245% Verbesserung)
- **Feedback Intelligence**: 27% → 89% (+230% Verbesserung)
- **Prompt Optimizer**: 24% → 93% (+288% Verbesserung)
- **Robustness Manager**: 34% → 93% (+174% Verbesserung)

### Test-Suite
- **97 umfassende Tests** für kritische Module
- **Mock-basierte Tests** für externe Abhängigkeiten
- **Parametrisierte Tests** für wiederkehrende Szenarien
- **End-to-End Workflows** vollständig getestet

## 🛠️ Installation

```bash
# Repository klonen
git clone https://github.com/your-repo/one-click-book-writer.git
cd one-click-book-writer

# Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oder: .venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Tests ausführen
python -m pytest tests/ -v --cov=core --cov-report=html
```

## 🚀 Schnellstart

```bash
# GUI starten
python gui_enhanced.py

# Oder mit Universal-Start-Script (von überall ausführbar)
/Users/tonyhegewald/Entwicklung/start_book_writer.sh
```

## 🧪 Testing

```bash
# Alle Tests ausführen
python -m pytest tests/ -v

# Coverage-Report generieren
python -m pytest tests/ -v --cov=core --cov-report=term-missing

# Spezifische Module testen
python -m pytest tests/test_enhanced_pipeline_comprehensive.py -v --cov=core.enhanced_pipeline
```

## 📋 CI/CD Pipeline

Die CI/CD Pipeline läuft automatisch bei jedem Commit und Pull Request:

- ✅ **Coverage-Gates**: Minimum 50% Coverage erforderlich
- ✅ **Quality-Gates**: Automatische Qualitätsprüfungen
- ✅ **Regression-Detection**: Vergleich zwischen Runs
- ✅ **Automated Testing**: Vollständige Test-Suite

## 📊 Coverage-Reports

- **HTML Report**: `reports/coverage_html/index.html`
- **JSON Report**: `reports/test_coverage_report.json`
- **Markdown Report**: `reports/test_coverage_report.md`

## 🔧 Konfiguration

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-key"
```

### Pipeline Configuration
```python
from core.enhanced_pipeline import EnhancedPipeline

pipeline = EnhancedPipeline()
result = pipeline.run_enhanced_pipeline(
    prompt_frame=prompt_frame,
    enable_optimization=True,
    enable_ab_testing=True,
    enable_feedback_collection=True
)
```

## 📚 Dokumentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Development Guide](docs/development.md)
- [Test Coverage Report](reports/test_coverage_report.md)
- [Release Checklist](reports/release_checklist_report.md)

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Push zum Branch (`git push origin feature/amazing-feature`)
5. Öffne einen Pull Request

### Testing Guidelines
- Alle neuen Features müssen Tests haben
- Coverage darf nicht unter 50% fallen
- Alle Tests müssen bestehen

## 📄 License

Dieses Projekt ist unter der MIT License lizenziert - siehe [LICENSE](LICENSE) Datei für Details.

## 🏆 Achievements

- ✅ **Alle Coverage-Ziele übertroffen**
- ✅ **97 umfassende Tests erstellt**
- ✅ **CI/CD mit Coverage-Gates aktiv**
- ✅ **Quality-Gates implementiert**
- ✅ **Release-ready Status erreicht**

## 📞 Support

Bei Fragen oder Problemen:
- Erstelle ein Issue im GitHub Repository
- Kontaktiere das Entwicklungsteam
- Konsultiere die Dokumentation

---

**Version 4.1.3** - Ready for Release ✅  
**Letzte Aktualisierung**: 2024-12-19 