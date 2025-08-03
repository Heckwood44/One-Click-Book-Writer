#!/usr/bin/env python3
"""
Tests für Core Architecture
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import hashlib

from core.architecture import (
    ComponentType, LayerType, Layer, PromptTemplate, PromptFrame,
    GenerationRequest, GenerationResult, EvaluationResult, FeedbackEntry,
    OptimizationResult, ABTestResult, PipelineResult,
    ComponentInterface, ArchitectureRegistry,
    register_component, get_component, get_template
)


class TestEnums(unittest.TestCase):
    """Test Enum-Definitionen"""
    
    def test_component_types(self):
        """Test ComponentType Enum"""
        self.assertEqual(ComponentType.PROMPT_FRAME.value, "prompt_frame")
        self.assertEqual(ComponentType.COMPILER.value, "compiler")
        self.assertEqual(ComponentType.ROUTER.value, "router")
        self.assertEqual(ComponentType.OPTIMIZER.value, "optimizer")
        self.assertEqual(ComponentType.GENERATOR.value, "generator")
        self.assertEqual(ComponentType.EVALUATOR.value, "evaluator")
        self.assertEqual(ComponentType.OUTPUT_HANDLER.value, "output_handler")
        self.assertEqual(ComponentType.FEEDBACK.value, "feedback")
        self.assertEqual(ComponentType.CI.value, "ci")
    
    def test_layer_types(self):
        """Test LayerType Enum"""
        self.assertEqual(LayerType.SYSTEM_NOTE.value, "system_note")
        self.assertEqual(LayerType.TARGET_AUDIENCE.value, "target_audience")
        self.assertEqual(LayerType.GENRE.value, "genre")
        self.assertEqual(LayerType.EMOTION_DRAMA.value, "emotion_drama")
        self.assertEqual(LayerType.STYLE.value, "style")
        self.assertEqual(LayerType.CONTEXT.value, "context")
        self.assertEqual(LayerType.CONSTRAINTS.value, "constraints")
        self.assertEqual(LayerType.LANGUAGE.value, "language")
        self.assertEqual(LayerType.CUSTOM.value, "custom")


class TestLayer(unittest.TestCase):
    """Test Layer-Klasse"""
    
    def test_layer_creation(self):
        """Test Layer-Erstellung"""
        layer = Layer(
            layer_type=LayerType.SYSTEM_NOTE,
            content="Test content",
            weight=1.5,
            version="2.0.0"
        )
        
        self.assertEqual(layer.layer_type, LayerType.SYSTEM_NOTE)
        self.assertEqual(layer.content, "Test content")
        self.assertEqual(layer.weight, 1.5)
        self.assertEqual(layer.version, "2.0.0")
        self.assertEqual(layer.metadata, {})
    
    def test_layer_hash(self):
        """Test Layer-Hash-Generierung"""
        layer = Layer(
            layer_type=LayerType.GENRE,
            content="fantasy",
            weight=1.0,
            version="1.0.0"
        )
        
        hash_value = layer.get_hash()
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 16)
        
        # Hash sollte konsistent sein
        hash_value2 = layer.get_hash()
        self.assertEqual(hash_value, hash_value2)
    
    def test_layer_metadata(self):
        """Test Layer-Metadata"""
        metadata = {"priority": "high", "source": "template"}
        layer = Layer(
            layer_type=LayerType.CUSTOM,
            content="custom content",
            metadata=metadata
        )
        
        self.assertEqual(layer.metadata, metadata)


class TestPromptTemplate(unittest.TestCase):
    """Test PromptTemplate-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        self.layers = [
            Layer(LayerType.SYSTEM_NOTE, "System instruction", 1.0),
            Layer(LayerType.GENRE, "fantasy", 1.0),
            Layer(LayerType.TARGET_AUDIENCE, "children", 1.0)
        ]
    
    def test_template_creation(self):
        """Test Template-Erstellung"""
        template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="A test template",
            layers=self.layers
        )
        
        self.assertEqual(template.template_id, "test_template")
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.description, "A test template")
        self.assertEqual(len(template.layers), 3)
        self.assertEqual(template.version, "1.0.0")
        self.assertIsInstance(template.created_at, datetime)
    
    def test_template_hash(self):
        """Test Template-Hash-Generierung"""
        template = PromptTemplate(
            template_id="hash_test",
            name="Hash Test",
            description="Test hash generation",
            layers=self.layers
        )
        
        hash_value = template.get_hash()
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 16)
        
        # Hash sollte konsistent sein
        hash_value2 = template.get_hash()
        self.assertEqual(hash_value, hash_value2)
    
    def test_template_metadata(self):
        """Test Template-Metadata"""
        metadata = {"author": "test", "category": "children"}
        template = PromptTemplate(
            template_id="meta_test",
            name="Meta Test",
            description="Test metadata",
            layers=self.layers,
            metadata=metadata
        )
        
        self.assertEqual(template.metadata, metadata)


class TestPromptFrame(unittest.TestCase):
    """Test PromptFrame-Klasse"""
    
    def test_prompt_frame_creation(self):
        """Test PromptFrame-Erstellung"""
        frame = PromptFrame(
            age_group="children",
            genre="fantasy",
            emotion="joy",
            language="de",
            target_audience="early_reader"
        )
        
        self.assertEqual(frame.age_group, "children")
        self.assertEqual(frame.genre, "fantasy")
        self.assertEqual(frame.emotion, "joy")
        self.assertEqual(frame.language, "de")
        self.assertEqual(frame.target_audience, "early_reader")
        self.assertIsNone(frame.custom_context)
        self.assertIsNone(frame.template_overrides)
        self.assertEqual(frame.metadata, {})
    
    def test_prompt_frame_with_context(self):
        """Test PromptFrame mit Custom Context"""
        custom_context = {"setting": "forest", "characters": ["hero", "villain"]}
        frame = PromptFrame(
            age_group="adult",
            genre="mystery",
            emotion="fear",
            custom_context=custom_context
        )
        
        self.assertEqual(frame.custom_context, custom_context)


class TestGenerationRequest(unittest.TestCase):
    """Test GenerationRequest-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        self.prompt_frame = PromptFrame(
            age_group="children",
            genre="fantasy",
            emotion="joy"
        )
        self.template = PromptTemplate(
            template_id="test",
            name="Test",
            description="Test",
            layers=[Layer(LayerType.SYSTEM_NOTE, "test", 1.0)]
        )
    
    def test_generation_request_creation(self):
        """Test GenerationRequest-Erstellung"""
        request = GenerationRequest(
            prompt_frame=self.prompt_frame,
            template=self.template
        )
        
        self.assertEqual(request.prompt_frame, self.prompt_frame)
        self.assertEqual(request.template, self.template)
        self.assertTrue(request.optimization_enabled)
        self.assertFalse(request.ab_testing_enabled)
        self.assertTrue(request.feedback_collection)
        self.assertTrue(request.retry_on_failure)
        self.assertEqual(request.max_retries, 3)
    
    def test_generation_request_custom_settings(self):
        """Test GenerationRequest mit Custom Settings"""
        request = GenerationRequest(
            prompt_frame=self.prompt_frame,
            template=self.template,
            optimization_enabled=False,
            ab_testing_enabled=True,
            feedback_collection=False,
            retry_on_failure=False,
            max_retries=5
        )
        
        self.assertFalse(request.optimization_enabled)
        self.assertTrue(request.ab_testing_enabled)
        self.assertFalse(request.feedback_collection)
        self.assertFalse(request.retry_on_failure)
        self.assertEqual(request.max_retries, 5)


class TestGenerationResult(unittest.TestCase):
    """Test GenerationResult-Klasse"""
    
    def test_generation_result_success(self):
        """Test erfolgreiches GenerationResult"""
        result = GenerationResult(
            success=True,
            german_text="Deutscher Text",
            english_text="English text",
            prompt_hash="abc123",
            template_hash="def456",
            generation_time=1.5,
            word_count=50
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.german_text, "Deutscher Text")
        self.assertEqual(result.english_text, "English text")
        self.assertEqual(result.prompt_hash, "abc123")
        self.assertEqual(result.template_hash, "def456")
        self.assertEqual(result.generation_time, 1.5)
        self.assertEqual(result.word_count, 50)
        self.assertEqual(result.errors, [])
    
    def test_generation_result_failure(self):
        """Test fehlgeschlagenes GenerationResult"""
        errors = ["API error", "Timeout"]
        result = GenerationResult(
            success=False,
            errors=errors
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.errors, errors)
        self.assertEqual(result.german_text, "")
        self.assertEqual(result.english_text, "")


class TestEvaluationResult(unittest.TestCase):
    """Test EvaluationResult-Klasse"""
    
    def test_evaluation_result_creation(self):
        """Test EvaluationResult-Erstellung"""
        result = EvaluationResult(
            overall_score=0.85,
            readability_score=0.9,
            age_appropriateness=0.95,
            genre_compliance=0.8,
            emotional_depth=0.7,
            engagement_score=0.75
        )
        
        self.assertEqual(result.overall_score, 0.85)
        self.assertEqual(result.readability_score, 0.9)
        self.assertEqual(result.age_appropriateness, 0.95)
        self.assertEqual(result.genre_compliance, 0.8)
        self.assertEqual(result.emotional_depth, 0.7)
        self.assertEqual(result.engagement_score, 0.75)
        self.assertEqual(result.flags, [])
        self.assertEqual(result.recommendations, [])
        self.assertEqual(result.evaluation_time, 0.0)
    
    def test_evaluation_result_with_flags(self):
        """Test EvaluationResult mit Flags"""
        flags = ["too_short", "low_engagement"]
        recommendations = ["Add more dialogue", "Increase conflict"]
        
        result = EvaluationResult(
            overall_score=0.6,
            readability_score=0.8,
            age_appropriateness=0.9,
            genre_compliance=0.7,
            emotional_depth=0.5,
            engagement_score=0.4,
            flags=flags,
            recommendations=recommendations,
            evaluation_time=2.5
        )
        
        self.assertEqual(result.flags, flags)
        self.assertEqual(result.recommendations, recommendations)
        self.assertEqual(result.evaluation_time, 2.5)


class TestFeedbackEntry(unittest.TestCase):
    """Test FeedbackEntry-Klasse"""
    
    def test_feedback_entry_creation(self):
        """Test FeedbackEntry-Erstellung"""
        entry = FeedbackEntry(
            chapter_number=1,
            prompt_hash="abc123",
            quality_score=0.8,
            user_rating=4,
            comment="Great chapter!",
            language="de"
        )
        
        self.assertEqual(entry.chapter_number, 1)
        self.assertEqual(entry.prompt_hash, "abc123")
        self.assertEqual(entry.quality_score, 0.8)
        self.assertEqual(entry.user_rating, 4)
        self.assertEqual(entry.comment, "Great chapter!")
        self.assertEqual(entry.language, "de")
        self.assertEqual(entry.metadata, {})
        self.assertIsInstance(entry.timestamp, datetime)


class TestOptimizationResult(unittest.TestCase):
    """Test OptimizationResult-Klasse"""
    
    def test_optimization_result_success(self):
        """Test erfolgreiches OptimizationResult"""
        result = OptimizationResult(
            original_prompt_hash="abc123",
            optimized_prompt_hash="def456",
            quality_score_delta=0.15,
            prompt_diff={"added": ["more dialogue"], "removed": ["redundant text"]},
            optimization_focus="engagement"
        )
        
        self.assertEqual(result.original_prompt_hash, "abc123")
        self.assertEqual(result.optimized_prompt_hash, "def456")
        self.assertEqual(result.quality_score_delta, 0.15)
        self.assertEqual(result.prompt_diff, {"added": ["more dialogue"], "removed": ["redundant text"]})
        self.assertEqual(result.optimization_focus, "engagement")
        self.assertTrue(result.success)
    
    def test_optimization_result_failure(self):
        """Test fehlgeschlagenes OptimizationResult"""
        result = OptimizationResult(
            original_prompt_hash="abc123",
            optimized_prompt_hash="abc123",
            quality_score_delta=0.0,
            prompt_diff={},
            optimization_focus="none",
            success=False
        )
        
        self.assertFalse(result.success)


class TestABTestResult(unittest.TestCase):
    """Test ABTestResult-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        self.original_result = GenerationResult(success=True, german_text="Original")
        self.optimized_result = GenerationResult(success=True, german_text="Optimized")
    
    def test_ab_test_result_creation(self):
        """Test ABTestResult-Erstellung"""
        result = ABTestResult(
            test_id="test_001",
            segment="children_fantasy",
            original_result=self.original_result,
            optimized_result=self.optimized_result,
            comparison={"quality_delta": 0.2, "engagement_delta": 0.15},
            significant_improvement=True,
            recommendation="Use optimized version"
        )
        
        self.assertEqual(result.test_id, "test_001")
        self.assertEqual(result.segment, "children_fantasy")
        self.assertEqual(result.original_result, self.original_result)
        self.assertEqual(result.optimized_result, self.optimized_result)
        self.assertEqual(result.comparison, {"quality_delta": 0.2, "engagement_delta": 0.15})
        self.assertTrue(result.significant_improvement)
        self.assertEqual(result.recommendation, "Use optimized version")


class TestPipelineResult(unittest.TestCase):
    """Test PipelineResult-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        self.prompt_frame = PromptFrame(age_group="children", genre="fantasy", emotion="joy")
        self.generation_result = GenerationResult(success=True, german_text="Test")
        self.evaluation_result = EvaluationResult(overall_score=0.8, readability_score=0.9,
                                                 age_appropriateness=0.95, genre_compliance=0.8,
                                                 emotional_depth=0.7, engagement_score=0.75)
    
    def test_pipeline_result_creation(self):
        """Test PipelineResult-Erstellung"""
        result = PipelineResult(
            run_id="run_001",
            prompt_frame=self.prompt_frame,
            generation_result=self.generation_result,
            evaluation_result=self.evaluation_result
        )
        
        self.assertEqual(result.run_id, "run_001")
        self.assertEqual(result.prompt_frame, self.prompt_frame)
        self.assertEqual(result.generation_result, self.generation_result)
        self.assertEqual(result.evaluation_result, self.evaluation_result)
        self.assertIsNone(result.optimization_result)
        self.assertIsNone(result.ab_test_result)
        self.assertEqual(result.feedback_entries, [])
        self.assertEqual(result.compliance_status, "pending")
        self.assertEqual(result.total_cost, 0.0)
        self.assertEqual(result.execution_time, 0.0)
    
    def test_pipeline_result_with_optional_fields(self):
        """Test PipelineResult mit optionalen Feldern"""
        optimization_result = OptimizationResult(
            original_prompt_hash="abc", optimized_prompt_hash="def",
            quality_score_delta=0.1, prompt_diff={}, optimization_focus="test"
        )
        feedback_entry = FeedbackEntry(
            chapter_number=1, prompt_hash="abc", quality_score=0.8,
            user_rating=4, comment="Good", language="de"
        )
        
        result = PipelineResult(
            run_id="run_002",
            prompt_frame=self.prompt_frame,
            generation_result=self.generation_result,
            evaluation_result=self.evaluation_result,
            optimization_result=optimization_result,
            feedback_entries=[feedback_entry],
            compliance_status="approved",
            total_cost=0.05,
            execution_time=5.2
        )
        
        self.assertEqual(result.optimization_result, optimization_result)
        self.assertEqual(len(result.feedback_entries), 1)
        self.assertEqual(result.feedback_entries[0], feedback_entry)
        self.assertEqual(result.compliance_status, "approved")
        self.assertEqual(result.total_cost, 0.05)
        self.assertEqual(result.execution_time, 5.2)


class TestComponentInterface(unittest.TestCase):
    """Test ComponentInterface-Klasse"""
    
    def test_component_interface_creation(self):
        """Test ComponentInterface-Erstellung"""
        component = ComponentInterface(ComponentType.COMPILER, "2.0.0")
        
        self.assertEqual(component.component_type, ComponentType.COMPILER)
        self.assertEqual(component.version, "2.0.0")
    
    def test_get_component_info(self):
        """Test get_component_info"""
        component = ComponentInterface(ComponentType.OPTIMIZER, "1.5.0")
        info = component.get_component_info()
        
        self.assertEqual(info["type"], ComponentType.OPTIMIZER.value)
        self.assertEqual(info["version"], "1.5.0")
        self.assertIn("metadata", info)
    
    def test_validate_input(self):
        """Test validate_input"""
        component = ComponentInterface(ComponentType.GENERATOR)
        
        # Standard-Implementierung sollte True zurückgeben
        self.assertTrue(component.validate_input("test"))
    
    def test_process(self):
        """Test process"""
        component = ComponentInterface(ComponentType.EVALUATOR)
        
        # Standard-Implementierung sollte NotImplementedError werfen
        with self.assertRaises(NotImplementedError):
            component.process("test input")


class TestArchitectureRegistry(unittest.TestCase):
    """Test ArchitectureRegistry-Klasse"""
    
    def setUp(self):
        """Setup für Tests"""
        self.registry = ArchitectureRegistry()
        self.component = ComponentInterface(ComponentType.COMPILER)
        self.template = PromptTemplate(
            template_id="test_template",
            name="Test Template",
            description="Test",
            layers=[Layer(LayerType.SYSTEM_NOTE, "test", 1.0)]
        )
    
    def test_register_component(self):
        """Test register_component"""
        self.registry.register_component(self.component)
        
        # Komponente sollte registriert sein
        retrieved = self.registry.get_component(ComponentType.COMPILER)
        self.assertEqual(retrieved, self.component)
    
    def test_get_nonexistent_component(self):
        """Test get_component für nicht existierende Komponente"""
        result = self.registry.get_component(ComponentType.GENERATOR)
        self.assertIsNone(result)
    
    def test_register_template(self):
        """Test register_template"""
        self.registry.register_template(self.template)
        
        # Template sollte registriert sein
        retrieved = self.registry.get_template("test_template")
        self.assertEqual(retrieved, self.template)
    
    def test_get_nonexistent_template(self):
        """Test get_template für nicht existierendes Template"""
        result = self.registry.get_template("nonexistent")
        self.assertIsNone(result)
    
    def test_define_pipeline(self):
        """Test define_pipeline"""
        components = [ComponentType.COMPILER, ComponentType.GENERATOR, ComponentType.EVALUATOR]
        self.registry.define_pipeline("test_pipeline", components)
        
        # Pipeline sollte definiert sein
        retrieved = self.registry.get_pipeline("test_pipeline")
        self.assertEqual(retrieved, components)
    
    def test_get_nonexistent_pipeline(self):
        """Test get_pipeline für nicht existierende Pipeline"""
        result = self.registry.get_pipeline("nonexistent")
        self.assertEqual(result, [])


class TestGlobalFunctions(unittest.TestCase):
    """Test globale Funktionen"""
    
    def test_register_component_global(self):
        """Test globale register_component Funktion"""
        component = ComponentInterface(ComponentType.ROUTER)
        register_component(component)
        
        # Komponente sollte über globale Funktion verfügbar sein
        retrieved = get_component(ComponentType.ROUTER)
        self.assertEqual(retrieved, component)
    
    def test_get_template_global(self):
        """Test globale get_template Funktion"""
        template = PromptTemplate(
            template_id="global_test",
            name="Global Test",
            description="Test",
            layers=[Layer(LayerType.SYSTEM_NOTE, "test", 1.0)]
        )
        
        # Template registrieren
        registry = ArchitectureRegistry()
        registry.register_template(template)
        
        # Template sollte über globale Funktion verfügbar sein
        # Da get_template eine globale Funktion ist, die auf ARCHITECTURE_REGISTRY zugreift,
        # müssen wir das globale Registry verwenden
        from core.architecture import ARCHITECTURE_REGISTRY
        ARCHITECTURE_REGISTRY.register_template(template)
        
        retrieved = get_template("global_test")
        self.assertEqual(retrieved, template)


if __name__ == "__main__":
    unittest.main() 