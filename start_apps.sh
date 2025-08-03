#!/bin/bash

# One Click Book Writer - Start-Skript
# Automatisch das richtige Verzeichnis verwenden

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Projektverzeichnis
PROJECT_DIR="/Users/tonyhegewald/Entwicklung/Projects/one-click-book-writer"

echo -e "${BLUE}🚀 One Click Book Writer - Start-Skript${NC}"
echo -e "${YELLOW}Wechsle zum Projektverzeichnis: ${PROJECT_DIR}${NC}"

# Zum Projektverzeichnis wechseln
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Fehler: Projektverzeichnis nicht gefunden!${NC}"
    exit 1
}

echo -e "${GREEN}✅ Verzeichnis gewechselt zu: $(pwd)${NC}"

# Virtual Environment aktivieren
echo -e "${YELLOW}Aktiviere Virtual Environment...${NC}"
source .venv/bin/activate

# Funktion zum Starten einer Anwendung
start_app() {
    local app_name=$1
    local app_file=$2
    local description=$3
    
    echo -e "${BLUE}📱 Starte ${app_name}...${NC}"
    echo -e "${YELLOW}Beschreibung: ${description}${NC}"
    
    if [ -f "$app_file" ]; then
        python3 "$app_file" &
        local pid=$!
        echo -e "${GREEN}✅ ${app_name} gestartet (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}❌ Datei nicht gefunden: $app_file${NC}"
        return 1
    fi
}

# Menü anzeigen
show_menu() {
    echo -e "\n${BLUE}📋 Verfügbare Anwendungen:${NC}"
    echo -e "${GREEN}1)${NC} Test-Anwendung (ohne API-Keys)"
    echo -e "${GREEN}2)${NC} Hauptanwendung (simple_gui.py)"
    echo -e "${GREEN}3)${NC} Erweiterte GUI (mit API-Keys)"
    echo -e "${GREEN}4)${NC} Alle Anwendungen starten"
    echo -e "${GREEN}5)${NC} Status der laufenden Anwendungen"
    echo -e "${GREEN}6)${NC} Alle Anwendungen beenden"
    echo -e "${GREEN}0)${NC} Beenden"
    echo -e "\n${YELLOW}Wählen Sie eine Option (0-6):${NC} "
}

# Status der laufenden Anwendungen anzeigen
show_status() {
    echo -e "\n${BLUE}📊 Status der laufenden Anwendungen:${NC}"
    
    local apps=("test_app.py" "simple_gui.py" "gui_enhanced.py")
    local running=0
    
    for app in "${apps[@]}"; do
        if pgrep -f "$app" > /dev/null; then
            local pids=$(pgrep -f "$app")
            echo -e "${GREEN}✅ $app läuft (PID: $pids)${NC}"
            ((running++))
        else
            echo -e "${RED}❌ $app läuft nicht${NC}"
        fi
    done
    
    echo -e "\n${YELLOW}Insgesamt laufen: $running Anwendung(en)${NC}"
}

# Alle Anwendungen beenden
stop_all() {
    echo -e "\n${YELLOW}🛑 Beende alle laufenden Anwendungen...${NC}"
    
    local apps=("test_app.py" "simple_gui.py" "gui_enhanced.py")
    local stopped=0
    
    for app in "${apps[@]}"; do
        if pgrep -f "$app" > /dev/null; then
            local pids=$(pgrep -f "$app")
            kill $pids 2>/dev/null
            echo -e "${GREEN}✅ $app beendet (PID: $pids)${NC}"
            ((stopped++))
        else
            echo -e "${YELLOW}ℹ️  $app läuft nicht${NC}"
        fi
    done
    
    echo -e "\n${GREEN}Beendet: $stopped Anwendung(en)${NC}"
}

# Hauptschleife
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            start_app "Test-Anwendung" "test_app.py" "Demo-Anwendung ohne API-Keys"
            ;;
        2)
            start_app "Hauptanwendung" "simple_gui.py" "Vollständige GUI mit allen Features"
            ;;
        3)
            start_app "Erweiterte GUI" "gui_enhanced.py" "Erweiterte Features (benötigt API-Keys)"
            ;;
        4)
            echo -e "\n${BLUE}🚀 Starte alle Anwendungen...${NC}"
            start_app "Test-Anwendung" "test_app.py" "Demo-Anwendung"
            sleep 2
            start_app "Hauptanwendung" "simple_gui.py" "Vollständige GUI"
            sleep 2
            start_app "Erweiterte GUI" "gui_enhanced.py" "Erweiterte Features"
            echo -e "\n${GREEN}✅ Alle Anwendungen gestartet!${NC}"
            ;;
        5)
            show_status
            ;;
        6)
            stop_all
            ;;
        0)
            echo -e "\n${BLUE}👋 Auf Wiedersehen!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}❌ Ungültige Option. Bitte wählen Sie 0-6.${NC}"
            ;;
    esac
    
    echo -e "\n${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    clear
done 