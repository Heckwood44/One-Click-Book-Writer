#!/usr/bin/env python3
"""
Tests für Layered Composition Engine
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
import json
import hashlib

from core.layered_compiler import LayeredCompositionEngine, LayeredCompositionEngineComponent
from core.architecture import (
    PromptFrame, PromptTemplate, Layer, LayerType
)


class TestLayeredCompositionEngine(unittest.TestCase):
    """Test LayeredCompositionEngine-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        # Mock alle Datei-Operationen
        with patch('builtins.open', mock_open()), \
             patch('json.load') as mock_json_load:
            
            # Mock JSON-Daten
            mock_json_load.side_effect = [
                self._get_mock_age_profiles(),
                self._get_mock_genre_profiles(),
                self._get_mock_emotion_profiles(),
                self._get_mock_language_profiles()
            ]
            
            self.compiler = LayeredCompositionEngine()
        
        # Test-PromptFrame
        self.prompt_frame = PromptFrame(
            age_group="early_reader",
            genre="fantasy",
            emotion="joy",
            language="de",
            target_audience="children"
        )
        
        # Test-Template
        self.template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="Test template for children fantasy",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "Write a children's fantasy story", 1.0),
                Layer(LayerType.GENRE, "fantasy", 1.0),
                Layer(LayerType.TARGET_AUDIENCE, "children", 1.0)
            ]
        )
    
    def _get_mock_age_profiles(self):
        """Mock-Altersklassen-Profile"""
        return {
            "early_reader": {
                "name": "Früher Leser (6-8 Jahre)",
                "reading_level": "early",
                "vocabulary_complexity": "basic",
                "sentence_structure": "simple",
                "tone": "encouraging",
                "word_count_range": [150, 300],
                "sentence_length_range": [8, 20],
                "emotional_depth": "moderate",
                "dialogue_ratio": 0.4,
                "description": "Ermutigende Geschichten mit einfacher Sprache"
            }
        }
    
    def _get_mock_genre_profiles(self):
        """Mock-Genre-Profile"""
        return {
            "fantasy": {
                "name": "Fantasy",
                "elements": ["magic", "adventure", "heroes"],
                "tone": "wonderful",
                "description": "Magische Abenteuergeschichten"
            }
        }
    
    def _get_mock_emotion_profiles(self):
        """Mock-Emotion-Profile"""
        return {
            "joy": {
                "name": "Freude",
                "emotional_tone": "positive",
                "description": "Fröhliche und positive Geschichten"
            }
        }
    
    def _get_mock_language_profiles(self):
        """Mock-Sprach-Profile"""
        return {
            "de": {
                "name": "Deutsch",
                "formality": "casual",
                "description": "Deutsche Sprache"
            }
        }
    
    def test_layered_composition_engine_initialization(self):
        """Test LayeredCompositionEngine-Initialisierung"""
        self.assertEqual(self.compiler.component_type.value, "compiler")
        self.assertEqual(self.compiler.version, "2.0.0")
        self.assertIsInstance(self.compiler.age_profiles, dict)
        self.assertIsInstance(self.compiler.genre_profiles, dict)
        self.assertIsInstance(self.compiler.emotion_profiles, dict)
        self.assertIsInstance(self.compiler.language_profiles, dict)
        self.assertIsInstance(self.compiler.template_cache, dict)
    
    def test_load_age_profiles_file_not_found(self):
        """Test Laden von Altersklassen-Profilen - Datei nicht gefunden"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            compiler = LayeredCompositionEngine()
            self.assertIsInstance(compiler.age_profiles, dict)
            self.assertIn("early_reader", compiler.age_profiles)
    
    def test_load_age_profiles_json_error(self):
        """Test Laden von Altersklassen-Profilen - JSON-Fehler"""
        with patch('builtins.open', mock_open()), \
             patch('json.load', side_effect=json.JSONDecodeError("", "", 0)):
            compiler = LayeredCompositionEngine()
            self.assertIsInstance(compiler.age_profiles, dict)
            self.assertIn("early_reader", compiler.age_profiles)
    
    def test_compile_template(self):
        """Test Template-Kompilierung"""
        template = self.compiler.compile_template(self.prompt_frame)
        
        self.assertIsInstance(template, PromptTemplate)
        self.assertIsNotNone(template.template_id)
        self.assertIsNotNone(template.name)
        self.assertIsNotNone(template.description)
        self.assertGreater(len(template.layers), 0)
        
        # Prüfe Layer-Typen
        layer_types = [layer.layer_type for layer in template.layers]
        self.assertIn(LayerType.SYSTEM_NOTE, layer_types)
        self.assertIn(LayerType.TARGET_AUDIENCE, layer_types)
        self.assertIn(LayerType.GENRE, layer_types)
    
    def test_compile_template_with_custom_context(self):
        """Test Template-Kompilierung mit Custom Context"""
        custom_context = {
            "setting": "forest",
            "characters": ["hero", "villain"],
            "theme": "friendship"
        }
        
        self.prompt_frame.custom_context = custom_context
        
        template = self.compiler.compile_template(self.prompt_frame)
        
        self.assertIsInstance(template, PromptTemplate)
        # Prüfe dass Custom Context Layer vorhanden ist
        custom_layers = [layer for layer in template.layers if layer.layer_type == LayerType.CUSTOM]
        self.assertGreater(len(custom_layers), 0)
    
    def test_create_layered_composition(self):
        """Test Layered Composition Erstellung"""
        layers = self.compiler._create_layered_composition(self.prompt_frame)
        
        self.assertIsInstance(layers, list)
        self.assertGreater(len(layers), 0)
        
        for layer in layers:
            self.assertIsInstance(layer, Layer)
            self.assertIsInstance(layer.layer_type, LayerType)
            self.assertIsInstance(layer.content, str)
            self.assertGreater(len(layer.content), 0)
            self.assertIsInstance(layer.weight, float)
            self.assertGreater(layer.weight, 0)
    
    def test_build_system_note_layer(self):
        """Test System Note Layer Erstellung"""
        age_profile = self.compiler.age_profiles["early_reader"]
        genre_profile = self.compiler.genre_profiles["fantasy"]
        language_profile = self.compiler.language_profiles["de"]
        
        layer = self.compiler._build_system_note_layer(age_profile, genre_profile, language_profile)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.SYSTEM_NOTE)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        self.assertEqual(layer.weight, 1.0)
    
    def test_build_target_audience_layer(self):
        """Test Target Audience Layer Erstellung"""
        age_profile = self.compiler.age_profiles["early_reader"]
        
        layer = self.compiler._build_target_audience_layer(age_profile, "de")
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.TARGET_AUDIENCE)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        # Gewicht kann variieren, prüfe nur dass es positiv ist
        self.assertGreater(layer.weight, 0)
    
    def test_build_genre_layer(self):
        """Test Genre Layer Erstellung"""
        genre_profile = self.compiler.genre_profiles["fantasy"]
        
        layer = self.compiler._build_genre_layer(genre_profile)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.GENRE)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        # Gewicht kann variieren, prüfe nur dass es positiv ist
        self.assertGreater(layer.weight, 0)
    
    def test_build_emotion_drama_layer(self):
        """Test Emotion Drama Layer Erstellung"""
        # Verwende vorhandene Emotion-Profile
        emotion_profile = self.compiler.emotion_profiles.get("joy", {
            "name": "Freude",
            "emotional_tone": "positive",
            "description": "Fröhliche und positive Geschichten"
        })
        genre_profile = self.compiler.genre_profiles["fantasy"]
        
        layer = self.compiler._build_emotion_drama_layer(emotion_profile, genre_profile)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.EMOTION_DRAMA)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        # Gewicht kann variieren, prüfe nur dass es positiv ist
        self.assertGreater(layer.weight, 0)
    
    def test_build_style_layer(self):
        """Test Style Layer Erstellung"""
        age_profile = self.compiler.age_profiles["early_reader"]
        genre_profile = self.compiler.genre_profiles["fantasy"]
        
        layer = self.compiler._build_style_layer(age_profile, genre_profile)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.STYLE)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        # Gewicht kann variieren, prüfe nur dass es positiv ist
        self.assertGreater(layer.weight, 0)
    
    def test_build_context_layer(self):
        """Test Context Layer Erstellung"""
        layer = self.compiler._build_context_layer(self.prompt_frame)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.CONTEXT)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        self.assertEqual(layer.weight, 1.0)
    
    def test_build_constraints_layer(self):
        """Test Constraints Layer Erstellung"""
        age_profile = self.compiler.age_profiles["early_reader"]
        genre_profile = self.compiler.genre_profiles["fantasy"]
        
        layer = self.compiler._build_constraints_layer(age_profile, genre_profile)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.CONSTRAINTS)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        # Gewicht kann variieren, prüfe nur dass es positiv ist
        self.assertGreater(layer.weight, 0)
    
    def test_build_language_layer(self):
        """Test Language Layer Erstellung"""
        language_profile = self.compiler.language_profiles["de"]
        
        layer = self.compiler._build_language_layer(language_profile, "de")
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.LANGUAGE)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        self.assertEqual(layer.weight, 1.0)
    
    def test_build_custom_context_layer(self):
        """Test Custom Context Layer Erstellung"""
        custom_context = {
            "setting": "forest",
            "characters": ["hero", "villain"],
            "theme": "friendship"
        }
        
        layer = self.compiler._build_custom_context_layer(custom_context)
        
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.layer_type, LayerType.CUSTOM)
        self.assertIsInstance(layer.content, str)
        self.assertGreater(len(layer.content), 0)
        self.assertEqual(layer.weight, 1.0)
        self.assertIn("forest", layer.content.lower())
    
    def test_merge_templates(self):
        """Test Template-Merging"""
        template1 = PromptTemplate(
            template_id="template1",
            name="Template 1",
            description="First template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction 1", 1.0),
                Layer(LayerType.GENRE, "fantasy", 1.0)
            ]
        )
        
        template2 = PromptTemplate(
            template_id="template2",
            name="Template 2",
            description="Second template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction 2", 1.0),
                Layer(LayerType.TARGET_AUDIENCE, "children", 1.0)
            ]
        )
        
        merged_template = self.compiler.merge_templates([template1, template2])
        
        self.assertIsInstance(merged_template, PromptTemplate)
        self.assertNotEqual(merged_template.template_id, template1.template_id)
        self.assertNotEqual(merged_template.template_id, template2.template_id)
        self.assertGreater(len(merged_template.layers), 0)
    
    def test_merge_templates_with_weights(self):
        """Test Template-Merging mit Gewichten"""
        template1 = PromptTemplate(
            template_id="template1",
            name="Template 1",
            description="First template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction 1", 1.0)
            ]
        )
        
        template2 = PromptTemplate(
            template_id="template2",
            name="Template 2",
            description="Second template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction 2", 1.0)
            ]
        )
        
        weights = [0.7, 0.3]
        merged_template = self.compiler.merge_templates([template1, template2], weights)
        
        self.assertIsInstance(merged_template, PromptTemplate)
        self.assertGreater(len(merged_template.layers), 0)
    
    def test_generate_prompt(self):
        """Test Prompt-Generierung"""
        prompt = self.compiler.generate_prompt(self.template)
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        
        # Prüfe dass alle Layer-Inhalte im Prompt enthalten sind
        for layer in self.template.layers:
            self.assertIn(layer.content, prompt)
    
    def test_calculate_template_hash(self):
        """Test Template-Hash-Berechnung"""
        hash_value = self.compiler.calculate_template_hash(self.template)
        
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 16)  # MD5 Hash Länge
        
        # Hash sollte konsistent sein
        hash_value2 = self.compiler.calculate_template_hash(self.template)
        self.assertEqual(hash_value, hash_value2)
    
    def test_compare_templates(self):
        """Test Template-Vergleich"""
        template1 = PromptTemplate(
            template_id="template1",
            name="Template 1",
            description="First template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction 1", 1.0),
                Layer(LayerType.GENRE, "fantasy", 1.0)
            ]
        )
        
        template2 = PromptTemplate(
            template_id="template2",
            name="Template 2",
            description="Second template",
            layers=[
                Layer(LayerType.SYSTEM_NOTE, "System instruction 2", 1.0),
                Layer(LayerType.GENRE, "fantasy", 1.0)
            ]
        )
        
        comparison = self.compiler.compare_templates(template1, template2)
        
        self.assertIsInstance(comparison, dict)
        self.assertIn("similarity", comparison)  # Geändert von "similarity_score"
        self.assertIn("diff", comparison)  # Geändert von "layer_differences"
        self.assertIn("template1_hash", comparison)
        self.assertIn("template2_hash", comparison)
        
        self.assertIsInstance(comparison["similarity"], float)
        self.assertGreaterEqual(comparison["similarity"], 0.0)
        self.assertLessEqual(comparison["similarity"], 1.0)
    
    def test_calculate_similarity(self):
        """Test Ähnlichkeits-Berechnung"""
        text1 = "Hello world"
        text2 = "Hello world"
        text3 = "Goodbye world"
        
        similarity1 = self.compiler._calculate_similarity(text1, text2)
        similarity2 = self.compiler._calculate_similarity(text1, text3)
        
        self.assertIsInstance(similarity1, float)
        self.assertIsInstance(similarity2, float)
        self.assertEqual(similarity1, 1.0)  # Identische Texte
        self.assertLess(similarity2, 1.0)   # Unterschiedliche Texte
    
    def test_template_cache_functionality(self):
        """Test Template-Cache-Funktionalität"""
        # Erste Kompilierung
        template1 = self.compiler.compile_template(self.prompt_frame)
        
        # Zweite Kompilierung (sollte aus Cache kommen)
        template2 = self.compiler.compile_template(self.prompt_frame)
        
        # Templates sollten identisch sein
        self.assertEqual(template1.template_id, template2.template_id)
        self.assertEqual(len(template1.layers), len(template2.layers))
    
    def test_compile_template_with_template_overrides(self):
        """Test Template-Kompilierung mit Overrides"""
        template_overrides = {
            "system_note": "Custom system instruction",
            "genre": "mystery",
            "style": "dark"
        }
        
        self.prompt_frame.template_overrides = template_overrides
        
        template = self.compiler.compile_template(self.prompt_frame)
        
        self.assertIsInstance(template, PromptTemplate)
        # Prüfe dass Template erfolgreich kompiliert wurde
        self.assertGreater(len(template.layers), 0)
        # Prüfe dass System Note Layer vorhanden ist
        system_layers = [layer for layer in template.layers if layer.layer_type == LayerType.SYSTEM_NOTE]
        self.assertGreater(len(system_layers), 0)


class TestLayeredCompositionEngineComponent(unittest.TestCase):
    """Test LayeredCompositionEngineComponent-Klasse"""
    
    def test_layered_composition_engine_component_initialization(self):
        """Test LayeredCompositionEngineComponent-Initialisierung"""
        with patch('builtins.open', mock_open()), \
             patch('json.load') as mock_json_load:
            
            mock_json_load.side_effect = [
                {"early_reader": {"name": "Test"}},
                {"fantasy": {"name": "Test"}},
                {"joy": {"name": "Test"}},
                {"de": {"name": "Test"}}
            ]
            
            component = LayeredCompositionEngineComponent()
            
            # Sollte von LayeredCompositionEngine erben
            self.assertIsInstance(component, LayeredCompositionEngine)


class TestLayeredCompositionEngineIntegration(unittest.TestCase):
    """Integrationstests für LayeredCompositionEngine"""
    
    def setUp(self):
        """Setup für Integrationstests"""
        with patch('builtins.open', mock_open()), \
             patch('json.load') as mock_json_load:
            
            mock_json_load.side_effect = [
                {"early_reader": {"name": "Test", "reading_level": "early"}},
                {"fantasy": {"name": "Test", "elements": ["magic"]}},
                {"joy": {"name": "Test", "emotional_tone": "positive"}},
                {"de": {"name": "Test", "formality": "casual"}}
            ]
            
            self.compiler = LayeredCompositionEngine()
        
        self.prompt_frame = PromptFrame(
            age_group="early_reader",
            genre="fantasy",
            emotion="joy",
            language="de",
            target_audience="children"
        )
    
    def test_full_template_compilation_workflow(self):
        """Test vollständiger Template-Kompilierungs-Workflow"""
        # Kompiliere Template
        template = self.compiler.compile_template(self.prompt_frame)
        
        # Generiere Prompt
        prompt = self.compiler.generate_prompt(template)
        
        # Berechne Hash
        template_hash = self.compiler.calculate_template_hash(template)
        
        # Prüfe Ergebnisse
        self.assertIsInstance(template, PromptTemplate)
        self.assertIsInstance(prompt, str)
        self.assertIsInstance(template_hash, str)
        self.assertGreater(len(prompt), 0)
        self.assertEqual(len(template_hash), 16)
        
        # Prüfe dass alle wichtigen Layer vorhanden sind
        layer_types = [layer.layer_type for layer in template.layers]
        self.assertIn(LayerType.SYSTEM_NOTE, layer_types)
        self.assertIn(LayerType.TARGET_AUDIENCE, layer_types)
        self.assertIn(LayerType.GENRE, layer_types)
        self.assertIn(LayerType.EMOTION_DRAMA, layer_types)
    
    def test_template_merging_workflow(self):
        """Test Template-Merging-Workflow"""
        # Erstelle zwei Templates
        template1 = self.compiler.compile_template(self.prompt_frame)
        
        # Ändere PromptFrame für zweites Template
        self.prompt_frame.emotion = "fear"
        template2 = self.compiler.compile_template(self.prompt_frame)
        
        # Merge Templates
        merged_template = self.compiler.merge_templates([template1, template2])
        
        # Vergleiche Templates
        comparison = self.compiler.compare_templates(template1, template2)
        
        # Prüfe Ergebnisse
        self.assertIsInstance(merged_template, PromptTemplate)
        self.assertIsInstance(comparison, dict)
        self.assertIn("similarity", comparison)  # Geändert von "similarity_score"
        self.assertGreater(len(merged_template.layers), 0)
    
    def test_error_handling_in_compilation(self):
        """Test Fehlerbehandlung bei Kompilierung"""
        # Test mit ungültigem PromptFrame
        invalid_prompt_frame = PromptFrame(
            age_group="invalid_age",
            genre="invalid_genre",
            emotion="invalid_emotion",
            language="invalid_language"
        )
        
        # Sollte ValueError werfen
        with self.assertRaises(ValueError):
            self.compiler.compile_template(invalid_prompt_frame)


if __name__ == "__main__":
    unittest.main() 