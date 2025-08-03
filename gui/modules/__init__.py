"""
GUI Modules Package
Modulare GUI-Komponenten für One Click Book Writer
"""

from .api_client import APIClient
from .gui_components import ChapterTab, StoryTab, CharacterTab
from .config_manager import ConfigManager

__all__ = [
    'APIClient',
    'ChapterTab', 
    'StoryTab',
    'CharacterTab',
    'ConfigManager'
]

# Version des GUI-Moduls
__version__ = "1.0.0" 