#!/bin/bash

# One Click Book Writer - Simple GUI Launcher
# Startet die Hauptanwendung

echo "🚀 One Click Book Writer - Hauptanwendung"
echo "Wechsle zum Projektverzeichnis..."

# Zum Projektverzeichnis wechseln
cd "/Users/tonyhegewald/Entwicklung/Projects/one-click-book-writer" || {
    echo "❌ Fehler: Projektverzeichnis nicht gefunden!"
    exit 1
}

echo "✅ Verzeichnis gewechselt zu: $(pwd)"

# Virtual Environment aktivieren
echo "Aktiviere Virtual Environment..."
source ".venv/bin/activate"

# Hauptanwendung starten
echo "📱 Starte Hauptanwendung..."
python3 simple_gui.py 