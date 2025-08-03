# 🚀 One Click Book Writer - Quick Start

## 🎯 **NEUE ALIASE - Nie wieder Virtual Environment Probleme!**

Ich habe praktische Aliase für dich erstellt, damit du das leidige Virtual Environment Problem nie wieder hast:

### **📋 Verfügbare Aliase:**

```bash
# 🔑 API Keys prüfen
bookwriter-check

# 🖥️  GUI starten
bookwriter-gui

# ⚡ Pipeline ausführen (Standard)
bookwriter-pipeline

# 🌍 Bilinguale Pipeline (Deutsch/Englisch)
bookwriter-pipeline --optimize

# 🎯 Projektverzeichnis aktivieren
bookwriter
```

### **🎮 Einfache Verwendung:**

```bash
# 1. API Keys prüfen
bookwriter-check

# 2. GUI starten
bookwriter-gui

# 3. Bilinguale Pipeline mit Claude-Optimierung
bookwriter-pipeline --optimize

# 4. Pipeline mit benutzerdefinierten Dateien
bookwriter-pipeline --json-file data/my_chapter.json --output output/my_result.txt
```

### **🌍 Bilinguale Generierung:**

```bash
# Erstellt automatisch deutsche UND englische Versionen:
# - chapter_1_de.txt (Deutsch)
# - chapter_1_en.txt (Englisch)
# - chapter_1_metadata.json (Metadaten)

bookwriter-pipeline --optimize
```

## 🎊 **Das leidige Virtual Environment Problem ist gelöst!**

**Vorher (immer wieder falsch):**
```bash
# ❌ FALSCH - Das globale venv
source /Users/tonyhegewald/Entwicklung/.venv/bin/activate
python simple_gui.py  # Fehler!
```

**Jetzt (immer richtig):**
```bash
# ✅ RICHTIG - Einfache Aliase
bookwriter-gui  # Funktioniert sofort!
```

## 🔧 **Falls die Aliase nicht funktionieren:**

```bash
# Terminal neu starten oder .zshrc neu laden
source ~/.zshrc

# Oder manuell (falls nötig)
cd /Users/tonyhegewald/Entwicklung/Projects/one-click-book-writer
source venv/bin/activate
python simple_gui.py
```

## 📚 **Vollständige Dokumentation:**

- **Build & Execution Guide**: `BUILD_EXECUTION_GUIDE.md`
- **API Key Management**: `key_check.py`
- **Pipeline**: `build_and_execute.py`
- **GUI**: `simple_gui.py`

---

**🎉 Das leidige Thema ist endgültig gelöst!** 🚀✨ 