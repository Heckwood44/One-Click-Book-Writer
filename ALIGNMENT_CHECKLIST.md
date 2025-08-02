# One Click Book Writer - Erweiterte Alignment-Checklist

## 🎯 **Pipeline-Validierung**

### **1. Prompt Compiler Tests**
- [ ] `compile_prompt` produziert zwei Abschnitte (DE/EN) wenn bilingual konfiguriert
- [ ] Prompt-Hash wird erzeugt und mit `chapter_meta.json` gespeichert
- [ ] Sprachspezifische Titel werden korrekt verwendet
- [ ] Kulturelle Anpassung ist im Prompt enthalten (z.B. "Staunen" vs "wonder")
- [ ] Fallback für fehlende bilinguale Konfiguration funktioniert

### **2. Claude-Optimierung**
- [ ] Claude-Optimierung wird angewendet oder sauber geloggt gefallbackt
- [ ] Optimierter Prompt wird gehasht und versioniert
- [ ] Diff zwischen Original und optimiertem Prompt ist verfügbar
- [ ] Token-Limits werden eingehalten (max 4000 für Claude)

### **3. GPT-Generierung**
- [ ] GPT-4-Antwort enthält die Trennlinie "---" 
- [ ] Bilinguales Parsing ergibt zwei separate Versionen
- [ ] Token-Logging stimmt mit generiertem Output überein
- [ ] Kosten werden korrekt berechnet und geloggt

### **4. Qualitätsbewertung**
- [ ] Alle Qualitätskomponenten werden berechnet:
  - [ ] Wortlimit-Compliance (25% Gewichtung)
  - [ ] Kernemotion-Präsenz (20% Gewichtung)
  - [ ] Wiederholungs-Score (15% Gewichtung)
  - [ ] Lesbarkeit (20% Gewichtung)
  - [ ] Struktur-Qualität (20% Gewichtung)
- [ ] Score-Schwellen werden geprüft:
  - [ ] Score < 0.7 → Review-Flag gesetzt
  - [ ] Score < 0.5 → Kritische Probleme-Flag gesetzt
- [ ] Verbesserungsvorschläge werden generiert

### **5. Fallback-Mechanismen**
- [ ] Fehlende bilinguale Konfiguration wird erkannt und dokumentiert
- [ ] Legacy-PromptFrames werden automatisch downgradet
- [ ] Fehlende Felder werden mit Defaults gefüllt
- [ ] Fallback-Aktionen sind im Meta dokumentiert

## 📊 **Output-Validierung**

### **6. Datei-Integrität**
- [ ] Ausgabe-Dateien existieren und sind UTF-8 kodiert:
  - [ ] `chapter_X_de.txt` (Deutsche Version)
  - [ ] `chapter_X_en.txt` (Englische Version)
  - [ ] `chapter_X_bilingual.txt` (Kombinierte Version)
  - [ ] `chapter_X_meta.json` (Metadaten)
- [ ] Alle Dateien sind nicht leer (> 100 Zeichen)
- [ ] Deutsche und englische Versionen haben ähnliche Länge (±20%)

### **7. Metadaten-Validierung**
- [ ] `chapter_meta.json` enthält alle erforderlichen Felder:
  - [ ] `prompt_versioning` mit Hash und Diff
  - [ ] `quality_evaluation` mit Scores und Flags
  - [ ] `review_required` und `critical_issues` Flags
  - [ ] `book_metadata` mit Titel und Genre
- [ ] Prompt-Hash ist konsistent zwischen Versioning und Meta
- [ ] Token-Usage stimmt mit API-Logs überein

## 🔍 **Qualitäts-Gates**

### **8. Review-Schwellen**
- [ ] **Score ≥ 0.8**: Excellent - Keine Aktion erforderlich
- [ ] **Score 0.6-0.79**: Good - Optional Review
- [ ] **Score 0.4-0.59**: Fair - Review erforderlich
- [ ] **Score < 0.4**: Poor - Kritische Probleme, manuelle Intervention

### **9. Spezifische Problem-Flags**
- [ ] **WORTLIMIT_PROBLEM**: Abweichung > 30% vom Ziel
- [ ] **EMOTION_PROBLEM**: Kernemotion < 0.5 Score
- [ ] **REPETITION_PROBLEM**: Wiederholungen > 40%
- [ ] **READABILITY_PROBLEM**: Satzlänge ungeeignet für Zielgruppe
- [ ] **STRUCTURE_PROBLEM**: Absatzstruktur unausgewogen

## 🚨 **Governance & Audit**

### **10. Automatisierte Review-Gates**
- [ ] Bei Score < 0.7: Pipeline stoppt und erfordert manuelle Freigabe
- [ ] Bei Score < 0.5: Kritische Warnung und automatische Pause
- [ ] Alle 5 Kapitel: Automatischer Review-Snapshot
- [ ] Bei bilingualem Parsing-Fehler: Fallback auf Monolingual

### **11. Audit-Trail**
- [ ] Prompt-Hashes für alle Versionen gespeichert
- [ ] Diff zwischen Original und optimiertem Prompt verfügbar
- [ ] Token-Usage und Kosten vollständig geloggt
- [ ] Qualitäts-Score-Verlauf dokumentiert
- [ ] Review-Entscheidungen und Gründe protokolliert

## 🧪 **Test-Automatisierung**

### **12. Smoke Test Erweiterungen**
```python
def test_bilingual_prompt_generation():
    """Testet bilinguale Prompt-Generierung"""
    prompt = compile_prompt_for_chatgpt(prompt_frame)
    assert "DEUTSCHE VERSION" in prompt
    assert "ENGLISH VERSION" in prompt
    assert "---" in prompt

def test_prompt_hashing():
    """Testet Prompt-Hashing"""
    hash1 = generate_prompt_hash(prompt1)
    hash2 = generate_prompt_hash(prompt2)
    assert hash1 != hash2  # Verschiedene Prompts = verschiedene Hashes

def test_quality_thresholds():
    """Testet Qualitäts-Schwellen"""
    evaluation = quality_evaluator.calculate_overall_quality_score(...)
    if evaluation["overall_score"] < 0.7:
        assert evaluation["review_required"] == True
    if evaluation["overall_score"] < 0.5:
        assert evaluation["critical_issues"] == True

def test_fallback_mechanisms():
    """Testet Fallback-Mechanismen"""
    # Test ohne bilinguale Konfiguration
    legacy_prompt_frame = {...}  # Ohne language-Sektion
    validate_prompt_structure(legacy_prompt_frame)
    assert legacy_prompt_frame["input"]["language"]["bilingual_output"] == False
```

## 📈 **Performance-Metriken**

### **13. Erfolgs-Kriterien**
- [ ] **Pipeline-Erfolgsrate**: > 95% erfolgreiche Durchläufe
- [ ] **Qualitäts-Score**: Durchschnitt > 0.7
- [ ] **Review-Rate**: < 20% der Kapitel erfordern Review
- [ ] **Kritische Probleme**: < 5% der Kapitel
- [ ] **Bilinguale Konsistenz**: > 0.8 Konsistenz-Score

### **14. Monitoring-Dashboard**
- [ ] Qualitäts-Score-Verlauf über Zeit
- [ ] Token-Usage und Kosten-Tracking
- [ ] Review-Trigger und Gründe
- [ ] Prompt-Versionierung-Statistiken
- [ ] Fallback-Nutzung und Legacy-Konversionen

---

## 🔄 **Ausführungsanweisungen**

### **Vor jedem Commit:**
1. Führe `python tests/smoke_test.py` aus
2. Prüfe alle Checklist-Punkte für das letzte Kapitel
3. Validiere Metadaten-Integrität
4. Überprüfe Qualitäts-Schwellen

### **Bei Review-Trigger:**
1. Analysiere Qualitäts-Score-Breakdown
2. Prüfe spezifische Problem-Flags
3. Entscheide: Weiterlaufen, Neu-Generierung oder manuelle Bearbeitung
4. Dokumentiere Entscheidung in Metadaten

### **Wöchentliche Audit-Reviews:**
1. Analysiere Qualitäts-Trends
2. Überprüfe Prompt-Versionierung
3. Validiere Kosten-Effizienz
4. Aktualisiere Governance-Regeln bei Bedarf

---

**Diese Checkliste stellt sicher, dass alle kritischen Aspekte der Pipeline validiert werden und Qualitätsstandards eingehalten werden!** 🎯 