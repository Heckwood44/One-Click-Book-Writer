#!/usr/bin/env python3
"""
One Click Book Writer - Prompt Versioning
Version: 2.0.0
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptVersioning:
    def __init__(self, history_file: str = "output/prompt_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Lädt die Prompt-Historie"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Prompt-Historie: {e}")
                return {"versions": [], "metadata": {}}
        return {"versions": [], "metadata": {}}
    
    def _save_history(self):
        """Speichert die Prompt-Historie"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Prompt-Historie: {e}")
    
    def generate_prompt_hash(self, prompt: str) -> str:
        """Generiert einen SHA-256 Hash für den Prompt"""
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
    
    def create_version_entry(self, 
                           prompt_frame: Dict, 
                           raw_prompt: str, 
                           optimized_prompt: Optional[str] = None,
                           chapter_number: int = 1,
                           language: str = "de") -> Dict:
        """Erstellt einen neuen Versions-Eintrag"""
        raw_hash = self.generate_prompt_hash(raw_prompt)
        optimized_hash = None
        diff = None
        
        if optimized_prompt:
            optimized_hash = self.generate_prompt_hash(optimized_prompt)
            diff = self._generate_diff(raw_prompt, optimized_prompt)
        
        version_entry = {
            "timestamp": datetime.now().isoformat(),
            "chapter_number": chapter_number,
            "language": language,
            "raw_prompt_hash": raw_hash,
            "optimized_prompt_hash": optimized_hash,
            "prompt_length": len(raw_prompt),
            "optimized_length": len(optimized_prompt) if optimized_prompt else None,
            "diff": diff,
            "metadata": {
                "book_title": prompt_frame.get('input', {}).get('book', {}).get('title', 'Unknown'),
                "chapter_title": prompt_frame.get('input', {}).get('chapter', {}).get('title', 'Unknown'),
                "genre": prompt_frame.get('input', {}).get('book', {}).get('genre', 'Unknown'),
                "is_bilingual": prompt_frame.get('input', {}).get('language', {}).get('bilingual_output', False)
            }
        }
        
        return version_entry
    
    def add_version(self, 
                   prompt_frame: Dict, 
                   raw_prompt: str, 
                   optimized_prompt: Optional[str] = None,
                   chapter_number: int = 1,
                   language: str = "de") -> str:
        """Fügt eine neue Prompt-Version hinzu"""
        version_entry = self.create_version_entry(
            prompt_frame, raw_prompt, optimized_prompt, chapter_number, language
        )
        
        self.history["versions"].append(version_entry)
        self._save_history()
        
        logger.info(f"Neue Prompt-Version hinzugefügt: {version_entry['raw_prompt_hash']}")
        return version_entry['raw_prompt_hash']
    
    def _generate_diff(self, raw_prompt: str, optimized_prompt: str) -> Dict:
        """Generiert einen einfachen Diff zwischen den Prompts"""
        raw_lines = raw_prompt.split('\n')
        opt_lines = optimized_prompt.split('\n')
        
        diff = {
            "raw_lines": len(raw_lines),
            "optimized_lines": len(opt_lines),
            "line_difference": len(opt_lines) - len(raw_lines),
            "character_difference": len(optimized_prompt) - len(raw_prompt)
        }
        
        return diff
    
    def get_version_by_hash(self, prompt_hash: str) -> Optional[Dict]:
        """Findet eine Version anhand des Hashes"""
        for version in self.history["versions"]:
            if (version.get('raw_prompt_hash') == prompt_hash or 
                version.get('optimized_prompt_hash') == prompt_hash):
                return version
        return None
    
    def get_versions_for_chapter(self, chapter_number: int) -> List[Dict]:
        """Gibt alle Versionen für ein Kapitel zurück"""
        return [v for v in self.history["versions"] if v.get('chapter_number') == chapter_number]
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken über die Prompt-Versionen zurück"""
        versions = self.history.get("versions", [])
        
        if not versions:
            return {"total_versions": 0}
        
        total_versions = len(versions)
        optimized_count = sum(1 for v in versions if v.get('optimized_prompt_hash'))
        bilingual_count = sum(1 for v in versions if v.get('metadata', {}).get('is_bilingual'))
        
        avg_prompt_length = sum(v.get('prompt_length', 0) for v in versions) / total_versions
        
        return {
            "total_versions": total_versions,
            "optimized_versions": optimized_count,
            "bilingual_versions": bilingual_count,
            "average_prompt_length": round(avg_prompt_length, 2),
            "optimization_rate": round(optimized_count / total_versions * 100, 2) if total_versions > 0 else 0
        }
    
    def export_metadata_for_chapter(self, chapter_number: int, output_file: str) -> Dict:
        """Exportiert Metadaten für ein Kapitel in chapter_meta.json"""
        versions = self.get_versions_for_chapter(chapter_number)
        
        if not versions:
            return {}
        
        latest_version = max(versions, key=lambda x: x.get('timestamp', ''))
        
        metadata = {
            "chapter_number": chapter_number,
            "prompt_versioning": {
                "total_versions": len(versions),
                "latest_version_hash": latest_version.get('raw_prompt_hash'),
                "latest_optimized_hash": latest_version.get('optimized_prompt_hash'),
                "latest_timestamp": latest_version.get('timestamp'),
                "prompt_length": latest_version.get('prompt_length'),
                "optimized_length": latest_version.get('optimized_length'),
                "diff": latest_version.get('diff')
            },
            "book_metadata": latest_version.get('metadata', {})
        }
        
        # Speichere in chapter_meta.json
        try:
            meta_file = Path(output_file)
            meta_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Prompt-Metadaten exportiert: {output_file}")
        except Exception as e:
            logger.error(f"Fehler beim Exportieren der Metadaten: {e}")
        
        return metadata 