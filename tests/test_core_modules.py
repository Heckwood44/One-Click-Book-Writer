#!/usr/bin/env python3
"""
Einfache Tests für Core-Module
"""

import unittest
from unittest.mock import Mock, patch

# Import-Mocks für Module die möglicherweise nicht vollständig implementiert sind
try:
    from core.drift_detector import DriftDetector, DriftType, DriftAlert
    DRIFT_DETECTOR_AVAILABLE = True
except ImportError:
    DRIFT_DETECTOR_AVAILABLE = False

try:
    from core.enhanced_pipeline import EnhancedPipeline
    ENHANCED_PIPELINE_AVAILABLE = True
except ImportError:
    ENHANCED_PIPELINE_AVAILABLE = False

try:
    from core.feedback_intelligence import FeedbackIntelligence
    FEEDBACK_INTELLIGENCE_AVAILABLE = True
except ImportError:
    FEEDBACK_INTELLIGENCE_AVAILABLE = False

try:
    from core.layered_compiler import LayeredCompositionEngine
    LAYERED_COMPILER_AVAILABLE = True
except ImportError:
    LAYERED_COMPILER_AVAILABLE = False

try:
    from core.policy_engine import PolicyEngine
    POLICY_ENGINE_AVAILABLE = True
except ImportError:
    POLICY_ENGINE_AVAILABLE = False

try:
    from core.prompt_optimizer import PromptOptimizer
    PROMPT_OPTIMIZER_AVAILABLE = True
except ImportError:
    PROMPT_OPTIMIZER_AVAILABLE = False

try:
    from core.robustness_manager import RobustnessManager
    ROBUSTNESS_MANAGER_AVAILABLE = True
except ImportError:
    ROBUSTNESS_MANAGER_AVAILABLE = False


class TestDriftDetector(unittest.TestCase):
    """Test DriftDetector"""
    
    @unittest.skipUnless(DRIFT_DETECTOR_AVAILABLE, "DriftDetector nicht verfügbar")
    def test_drift_detector_initialization(self):
        """Test DriftDetector-Initialisierung"""
        detector = DriftDetector()
        self.assertIsNotNone(detector)
    
    @unittest.skipUnless(DRIFT_DETECTOR_AVAILABLE, "DriftDetector nicht verfügbar")
    def test_drift_types(self):
        """Test DriftType Enum"""
        self.assertIsNotNone(DriftType.SCORE_DECLINE)
        self.assertIsNotNone(DriftType.FEEDBACK_DECLINE)
        self.assertIsNotNone(DriftType.CONSISTENCY_LOSS)
        self.assertIsNotNone(DriftType.TEMPLATE_AGING)
        self.assertIsNotNone(DriftType.SEGMENT_DRIFT)
    
    @unittest.skipUnless(DRIFT_DETECTOR_AVAILABLE, "DriftDetector nicht verfügbar")
    def test_drift_alert_creation(self):
        """Test DriftAlert-Erstellung"""
        from datetime import datetime
        alert = DriftAlert(
            drift_type=DriftType.SCORE_DECLINE,
            segment="test_segment",
            severity="medium",
            current_value=0.7,
            baseline_value=0.85,
            drift_percentage=0.18,
            confidence=0.8,
            timestamp=datetime.now(),
            metadata={}
        )
        self.assertIsNotNone(alert)
        self.assertEqual(alert.drift_type, DriftType.SCORE_DECLINE)
        self.assertEqual(alert.segment, "test_segment")


class TestEnhancedPipeline(unittest.TestCase):
    """Test EnhancedPipeline"""
    
    @unittest.skipUnless(ENHANCED_PIPELINE_AVAILABLE, "EnhancedPipeline nicht verfügbar")
    def test_enhanced_pipeline_initialization(self):
        """Test EnhancedPipeline-Initialisierung"""
        with patch('core.enhanced_pipeline.LayeredCompositionEngine'), \
             patch('core.enhanced_pipeline.PromptOptimizer'), \
             patch('core.enhanced_pipeline.RobustnessManager'), \
             patch('core.enhanced_pipeline.TargetGroupEvaluator'), \
             patch('core.enhanced_pipeline.UserFeedbackSystem'), \
             patch('core.enhanced_pipeline.OpenAIAdapter'), \
             patch('core.enhanced_pipeline.ARCHITECTURE_REGISTRY'):
            
            pipeline = EnhancedPipeline()
            self.assertIsNotNone(pipeline)


class TestFeedbackIntelligence(unittest.TestCase):
    """Test FeedbackIntelligence"""
    
    @unittest.skipUnless(FEEDBACK_INTELLIGENCE_AVAILABLE, "FeedbackIntelligence nicht verfügbar")
    def test_feedback_intelligence_initialization(self):
        """Test FeedbackIntelligence-Initialisierung"""
        intelligence = FeedbackIntelligence()
        self.assertIsNotNone(intelligence)


class TestLayeredCompiler(unittest.TestCase):
    """Test LayeredCompositionEngine"""
    
    @unittest.skipUnless(LAYERED_COMPILER_AVAILABLE, "LayeredCompositionEngine nicht verfügbar")
    def test_layered_compiler_initialization(self):
        """Test LayeredCompositionEngine-Initialisierung"""
        compiler = LayeredCompositionEngine()
        self.assertIsNotNone(compiler)


class TestPolicyEngine(unittest.TestCase):
    """Test PolicyEngine"""
    
    @unittest.skipUnless(POLICY_ENGINE_AVAILABLE, "PolicyEngine nicht verfügbar")
    def test_policy_engine_initialization(self):
        """Test PolicyEngine-Initialisierung"""
        engine = PolicyEngine()
        self.assertIsNotNone(engine)


class TestPromptOptimizer(unittest.TestCase):
    """Test PromptOptimizer"""
    
    @unittest.skipUnless(PROMPT_OPTIMIZER_AVAILABLE, "PromptOptimizer nicht verfügbar")
    def test_prompt_optimizer_initialization(self):
        """Test PromptOptimizer-Initialisierung"""
        optimizer = PromptOptimizer()
        self.assertIsNotNone(optimizer)


class TestRobustnessManager(unittest.TestCase):
    """Test RobustnessManager"""
    
    @unittest.skipUnless(ROBUSTNESS_MANAGER_AVAILABLE, "RobustnessManager nicht verfügbar")
    def test_robustness_manager_initialization(self):
        """Test RobustnessManager-Initialisierung"""
        manager = RobustnessManager()
        self.assertIsNotNone(manager)


class TestCoreModuleImports(unittest.TestCase):
    """Test Core-Module-Imports"""
    
    def test_core_architecture_import(self):
        """Test core.architecture Import"""
        try:
            from core.architecture import ComponentType, LayerType
            self.assertIsNotNone(ComponentType)
            self.assertIsNotNone(LayerType)
        except ImportError as e:
            self.fail(f"core.architecture Import fehlgeschlagen: {e}")
    
    def test_core_security_import(self):
        """Test core.security Import"""
        try:
            from core.security import SecretManager
            self.assertIsNotNone(SecretManager)
        except ImportError as e:
            self.fail(f"core.security Import fehlgeschlagen: {e}")
    
    def test_core_validation_import(self):
        """Test core.validation Import"""
        try:
            from core.validation import validate_prompt_frame
            self.assertIsNotNone(validate_prompt_frame)
        except ImportError as e:
            self.fail(f"core.validation Import fehlgeschlagen: {e}")
    
    def test_core_promotion_guardrails_import(self):
        """Test core.promotion_guardrails Import"""
        try:
            from core.promotion_guardrails import PromotionGuardrails
            self.assertIsNotNone(PromotionGuardrails)
        except ImportError as e:
            self.fail(f"core.promotion_guardrails Import fehlgeschlagen: {e}")


class TestModuleAvailability(unittest.TestCase):
    """Test Modul-Verfügbarkeit"""
    
    def test_all_core_modules_exist(self):
        """Test dass alle Core-Module existieren"""
        import os
        
        core_modules = [
            "core/architecture.py",
            "core/security.py",
            "core/validation.py",
            "core/promotion_guardrails.py",
            "core/drift_detector.py",
            "core/enhanced_pipeline.py",
            "core/feedback_intelligence.py",
            "core/layered_compiler.py",
            "core/policy_engine.py",
            "core/prompt_optimizer.py",
            "core/robustness_manager.py"
        ]
        
        for module_path in core_modules:
            self.assertTrue(
                os.path.exists(module_path),
                f"Core-Modul {module_path} existiert nicht"
            )


if __name__ == "__main__":
    unittest.main() 