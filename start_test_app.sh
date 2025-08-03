#!/bin/bash

# One Click Book Writer - Test-Anwendung Launcher
# Startet die Demo-Anwendung ohne API-Keys

echo "🚀 One Click Book Writer - Test-Anwendung"
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

# Test-Anwendung starten
echo "📱 Starte Test-Anwendung (ohne API-Keys)..."
python3 test_app.py 