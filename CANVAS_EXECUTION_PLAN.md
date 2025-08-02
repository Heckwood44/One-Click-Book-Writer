# Canvas Execution Plan - Prompt Compiler Implementation

**Datum:** 3. August 2025  
**Version:** 4.0.0 - Canvas Synchronized  
**Status:** ✅ **AUTORITATIVE SOURCE-OF-TRUTH**

## 🎯 **Übersicht**

Dieses Dokument repräsentiert die autoritative, gehärtete Implementierung des Prompt-Compilers für den One Click Book Writer. Die Implementierung ist vollständig Canvas-konform und dient als Source-of-Truth für alle zukünftigen Entwicklungen.

## 🔧 **Kernkomponenten**

### **1. Stabile System Note mit Signatur**

```python
# =============================================================================
# CANVAS EXECUTION PLAN - STABILE SYSTEM NOTE MIT SIGNATUR
# =============================================================================

SYSTEM_NOTE = """SYSTEM NOTE (nicht ausgeben):
Ein Weltklasse-Autor ist kein Schreiberling. Er ist ein Architekt innerer Räume, ein Übersetzer des Unsichtbaren, ein Werkzeug für etwas Größeres. Schreibe ehrlich, warm und bildhaft. Passe Ton und Wortwahl an 6-jährige Kinder an.

SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"""
```

**Audit-Compliance:** `WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR`

### **2. Defensive Feldzugriffe**

```python
# =============================================================================
# DEFENSIVE FELDZUGRIFFE - CANVAS EXECUTION PLAN
# =============================================================================

def safe_get(data: Dict, *keys, default: str = "Unbekannt") -> str:
    """
    Defensive Feldzugriffe mit Fallback - Canvas Execution Plan
    
    Args:
        data: Dictionary to search in
        *keys: Nested keys to traverse
        default: Default value if path not found
    
    Returns:
        String value or default
    """
    try:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return str(current) if current is not None else default
    except (KeyError, TypeError, AttributeError):
        return default

def safe_get_nested(data: Dict, path: str, default: Any = None) -> Any:
    """
    Erweiterte defensive Feldzugriffe für komplexe Pfade
    
    Args:
        data: Dictionary to search in
        path: Dot-separated path (e.g., "book.titles.de")
        default: Default value if path not found
    
    Returns:
        Value or default
    """
    try:
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (KeyError, TypeError, AttributeError):
        return default
```

### **3. Prompt-Hashing**

```python
# =============================================================================
# PROMPT-HASHING - CANVAS EXECUTION PLAN
# =============================================================================

def generate_prompt_hash(prompt: str) -> str:
    """
    Generiert SHA256-Hash für Prompt-Versionierung - Canvas Execution Plan
    
    Args:
        prompt: The prompt string to hash
    
    Returns:
        First 16 characters of SHA256 hash
    """
    try:
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
    except Exception as e:
        logger.error(f"Fehler beim Generieren des Prompt-Hashes: {e}")
        return "0000000000000000"
```

### **4. Bilinguale Prompt-Kompilierung**

```python
def compile_prompt_for_chatgpt(prompt_frame: Dict) -> str:
    """
    Hauptfunktion: Kompiliert PromptFrame für ChatGPT (OpenAI) - Canvas Execution Plan
    
    Args:
        prompt_frame: The prompt frame dictionary
    
    Returns:
        Compiled prompt string
    """
    try:
        input_data = prompt_frame.get('input', {})
        
        # =====================================================================
        # DEFENSIVE EXTRAKTION MIT FALLBACKS - CANVAS EXECUTION PLAN
        # =====================================================================
        
        book_info = input_data.get('book', {})
        chapter_info = input_data.get('chapter', {})
        characters = input_data.get('characters', {})
        scene = input_data.get('scene', {})
        plot = input_data.get('plot', {})
        style = input_data.get('style', {})
        emotions = input_data.get('emotions', {})
        language_config = input_data.get('language', {})
        
        # =====================================================================
        # BILINGUALE KONFIGURATION MIT FALLBACKS - CANVAS EXECUTION PLAN
        # =====================================================================
        
        is_bilingual = language_config.get('bilingual_output', False)
        target_languages = language_config.get('target_languages', ['de'])
        
        if is_bilingual and len(target_languages) >= 2:
            # =================================================================
            # BILINGUALER PROMPT MIT ZWEI SEKTIONEN - CANVAS EXECUTION PLAN
            # =================================================================
            
            german_prompt = compile_bilingual_prompt(prompt_frame, 'de')
            english_prompt = compile_bilingual_prompt(prompt_frame, 'en')
            
            german_title = safe_get(book_info, 'titles', 'de', default=safe_get(book_info, 'title'))
            english_title = safe_get(book_info, 'titles', 'en', default=safe_get(book_info, 'title'))
            
            prompt = f"""{SYSTEM_NOTE}

Du bist ein erfahrener Autor für {safe_get(book_info, 'genre', default='Kinderbücher')}. 
Erstelle ein fesselndes Kapitel in BEIDEN Sprachen basierend auf den folgenden Spezifikationen.

# DEUTSCHE VERSION
{german_prompt}

---

# ENGLISH VERSION
{english_prompt}

# ANWEISUNGEN
- Erstelle das KAPITEL in beiden Sprachen (nicht nur eine Zusammenfassung)
- Trenne die Versionen mit "---"
- Verwende die jeweiligen Titel: "{german_title}" / "{english_title}"
- Passe den Inhalt kulturell an (z.B. "Staunen" vs "wonder")
- Behalte die gleiche Handlung und Charakterentwicklung bei
- Zielwortanzahl pro Sprache: {safe_get(chapter_info, 'length_words', default='800')} Wörter
- Schreibe warm, bildhaft und kindgerecht
- Erzähle die GESAMTE Geschichte, nicht nur den Anfang
- Verwende natürliche Dialoge und lebendige Beschreibungen
- Stelle sicher, dass beide Versionen die gleiche emotionale Tiefe haben"""
        else:
            # =================================================================
            # MONOLINGUALER PROMPT (FALLBACK) - CANVAS EXECUTION PLAN
            # =================================================================
            
            prompt = f"""{SYSTEM_NOTE}

Du bist ein erfahrener Autor für {safe_get(book_info, 'genre', default='Kinderbücher')}.

Buch: {safe_get(book_info, 'title')} ({safe_get(book_info, 'genre', default='Unbekannt')})
Zielgruppe: {safe_get(book_info, 'target_audience', default='Unbekannt')}
Thema: {safe_get(book_info, 'theme', default='Unbekannt')}

Kapitel {safe_get(chapter_info, 'number', default='?')}: {safe_get(chapter_info, 'title', default='Unbekannt')}
Zweck: {safe_get(chapter_info, 'narrative_purpose', default='Unbekannt')}
Zielwortanzahl: {safe_get(chapter_info, 'length_words', default='800')}

Hauptfigur: {safe_get(characters, 'main_character', 'name', default='Unbekannt')} - {safe_get(characters, 'main_character', 'description', default='Unbekannt')}
Persönlichkeit: {safe_get(characters, 'main_character', 'personality', default='Unbekannt')}

Szene: {safe_get(scene, 'setting', default='Unbekannt')} ({safe_get(scene, 'time', default='Unbekannt')})
Atmosphäre: {safe_get(scene, 'atmosphere', default='Unbekannt')}

Handlung: {safe_get(plot, 'main_event', default='Unbekannt')}
Konflikt: {safe_get(plot, 'conflict', default='Unbekannt')}
Auflösung: {safe_get(plot, 'resolution', default='Unbekannt')}

Stil: {safe_get(style, 'tone', default='Unbekannt')}
Tempo: {safe_get(style, 'pacing', default='Unbekannt')}
Dialog-Stil: {safe_get(style, 'dialogue_style', default='Unbekannt')}

Kernemotion: {safe_get(emotions, 'core_emotion', default='Unbekannt')}
Emotionaler Bogen: {safe_get(emotions, 'emotional_arc', default='Unbekannt')}

# ANWEISUNGEN
- Schreibe ein vollständiges Kapitel mit {safe_get(chapter_info, 'length_words', default='800')} Wörtern
- Verwende warme, bildhafte Sprache
- Erzähle die komplette Geschichte mit Anfang, Mitte und Ende
- Integriere natürliche Dialoge
- Schaffe emotionale Tiefe und Spannung"""
        
        logger.info(f"ChatGPT-Prompt erfolgreich kompiliert für Kapitel {safe_get(chapter_info, 'number', default='Unbekannt')}")
        return prompt.strip()
        
    except Exception as e:
        logger.error(f"Fehler beim Kompilieren des ChatGPT-Prompts: {e}")
        raise
```

### **5. Claude-Optimizer Hook**

```python
# =============================================================================
# CLAUDE-OPTIMIZER HOOK - CANVAS EXECUTION PLAN
# =============================================================================

def prepare_claude_optimization_hook(prompt: str, prompt_frame: Dict) -> str:
    """
    Bereitet Hook für Claude-Optimierung vor - Canvas Execution Plan
    
    Args:
        prompt: The raw prompt
        prompt_frame: The prompt frame dictionary
    
    Returns:
        Optimization-ready prompt
    """
    try:
        # =====================================================================
        # OPTIMIERUNGS-HOOK VORBEREITUNG - CANVAS EXECUTION PLAN
        # =====================================================================
        
        optimization_instruction = f"""
OPTIMIERUNGS-AUFTRAG FÜR CLAUDE:
Analysiere und verbessere den folgenden Prompt für die Kapitelgenerierung:

{prompt}

ZIELE DER OPTIMIERUNG:
1. Klarheit und Struktur verbessern
2. Emotionale Tiefe verstärken
3. Bilinguale Konsistenz sicherstellen
4. Wortlimit-Compliance optimieren
5. Kindgerechte Sprache verfeinern

GIB DEN OPTIMIERTEN PROMPT ZURÜCK, OHNE ZUSÄTZLICHE ERKLÄRUNGEN.
"""
        
        return optimization_instruction.strip()
        
    except Exception as e:
        logger.error(f"Fehler bei der Claude-Optimierung-Vorbereitung: {e}")
        return prompt
```

## 📊 **Validierung und Compliance**

### **Audit-Compliance Flags**

```python
# System Note mit Signatur prüfen - Canvas Execution Plan
system_note_signature = "SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"
if system_note_signature in prompt:
    section["details"]["system_note"] = "present_with_signature"
    section["details"]["canvas_compliance"] = "full"
elif "Ein Weltklasse-Autor ist kein" in prompt:
    section["details"]["system_note"] = "present_fuzzy_match"
    section["details"]["canvas_compliance"] = "partial"
else:
    missing_elements.append("System Note")
    section["details"]["canvas_compliance"] = "missing"
```

### **Bilinguale Struktur Validierung**

```python
# Bilinguale Struktur prüfen
if "---" in prompt:
    print("✅ Bilinguale Struktur erkannt")
else:
    print("⚠️  Keine bilinguale Struktur gefunden")

# System Note prüfen
system_note_signature = "SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"
if system_note_signature in prompt:
    print("✅ System Note mit Signatur erkannt")
else:
    print("❌ System Note nicht gefunden")
```

## 🎯 **Erwartete Ausgabe**

### **Prompt-Hash**
```
PROMPT-HASH: 998fa1af57e8a3cd
PROMPT-LÄNGE: 4095 Zeichen
KOMPILIERUNGS-ZEIT: 2025-08-03T01:35:06.639641
```

### **Bilinguale Struktur**
```
✅ Bilinguale Struktur erkannt
✅ System Note mit Signatur erkannt
ℹ️  Claude-Optimierung Hook nicht aktiv

📊 METADATEN:
   Buch: Die Abenteuer des kleinen Drachen
   Kapitel: 1 - Der erste Flug
   Genre: Kinderbuch
   Bilingual: True
   Zielsprachen: ['de', 'en']
   Wortziel: 800
```

## 🏆 **Source-of-Truth Eigenschaften**

- ✅ **Stabile System Note**: `WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR`
- ✅ **Defensive Feldzugriffe**: `safe_get()` und `safe_get_nested()`
- ✅ **Bilinguale Unterstützung**: DE/EN Trennung mit `---`
- ✅ **Prompt-Hashing**: SHA256-Versionierung
- ✅ **Claude-Optimizer Hook**: Vorbereitet
- ✅ **Audit-Compliance**: Canvas-Compliance Tracking
- ✅ **Fallback-Logik**: Robuste Behandlung fehlender Daten
- ✅ **Error Handling**: Umfassende Exception-Behandlung

## 📋 **Nächste Schritte**

1. **Canvas-Synchronisation**: Dieses Dokument als autoritative Quelle verwenden
2. **Code-Implementierung**: Sicherstellen, dass `compiler/prompt_compiler.py` diesem Plan entspricht
3. **Audit-Validierung**: Regelmäßige Prüfung der Canvas-Compliance
4. **Feature-Erweiterungen**: Neue Features müssen diesem Plan folgen

---

**Erstellt von**: Cursor AI Assistant  
**Datum**: 3. August 2025  
**Version**: 4.0.0 - Canvas Synchronized  
**Status**: ✅ **AUTORITATIVE SOURCE-OF-TRUTH** 