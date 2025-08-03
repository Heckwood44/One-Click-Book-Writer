#!/usr/bin/env python3
"""
Enhanced Pipeline
Erweiterte Pipeline mit allen neuen Komponenten und vollständiger Orchestrierung
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import time

from core.architecture import (
    ComponentInterface, ComponentType, PromptFrame, PromptTemplate,
    GenerationRequest, GenerationResult, EvaluationResult, 
    OptimizationResult, ABTestResult, PipelineResult, FeedbackEntry,
    get_component, get_template, ARCHITECTURE_REGISTRY
)
from core.layered_compiler import LayeredCompositionEngine
from core.prompt_optimizer import PromptOptimizer
from core.robustness_manager import RobustnessManager
from utils.target_group_evaluator import TargetGroupEvaluator
from scripts.user_feedback_system import UserFeedbackSystem
from engine.openai_adapter import OpenAIAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPipeline(ComponentInterface):
    """Erweiterte Pipeline mit allen neuen Komponenten"""
    
    def __init__(self):
        super().__init__(ComponentType.ROUTER, version="2.0.0")
        
        # Initialisiere Komponenten
        self.compiler = LayeredCompositionEngine()
        self.optimizer = PromptOptimizer()
        self.robustness_manager = RobustnessManager()
        self.evaluator = TargetGroupEvaluator()
        self.feedback_system = UserFeedbackSystem()
        self.generator = OpenAIAdapter()
        
        # Registriere Komponenten
        ARCHITECTURE_REGISTRY.register_component(self.compiler)
        ARCHITECTURE_REGISTRY.register_component(self.optimizer)
        ARCHITECTURE_REGISTRY.register_component(self.robustness_manager)
        
        # Pipeline-Statistiken
        self.pipeline_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_execution_time": 0.0,
            "total_cost": 0.0
        }
    
    def run_enhanced_pipeline(self, 
                            prompt_frame: PromptFrame,
                            enable_optimization: bool = True,
                            enable_ab_testing: bool = False,
                            enable_feedback_collection: bool = True,
                            max_retries: int = 3) -> PipelineResult:
        """Führt erweiterte Pipeline aus"""
        start_time = time.time()
        run_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(prompt_frame).encode()).hexdigest()[:8]}"
        
        logger.info(f"Starte erweiterte Pipeline: {run_id}")
        
        try:
            # 1. Template-Kompilierung
            template = self.compiler.compile_template(prompt_frame)
            logger.info(f"Template kompiliert: {template.template_id}")
            
            # 2. Prompt-Generierung
            prompt = self.compiler.generate_prompt(template)
            prompt_hash = self.compiler.calculate_template_hash(template)
            
            # 3. Text-Generierung mit Retry-Mechanismus
            generation_result = self._generate_with_retry(
                prompt, prompt_frame, template, max_retries
            )
            
            # 4. Evaluation
            evaluation_result = self._evaluate_generation(generation_result, prompt_frame)
            
            # 5. Optimierung (optional)
            optimization_result = None
            if enable_optimization and generation_result.success:
                optimization_result = self._optimize_prompt(
                    template, prompt_frame, evaluation_result
                )
            
            # 6. A/B-Testing (optional)
            ab_test_result = None
            if enable_ab_testing and optimization_result and optimization_result.success:
                ab_test_result = self._run_ab_test(
                    generation_result, optimization_result, prompt_frame
                )
            
            # 7. Feedback-Sammlung (optional)
            feedback_entries = []
            if enable_feedback_collection:
                feedback_entries = self._collect_feedback(
                    generation_result, evaluation_result, prompt_frame
                )
            
            # 8. Compliance-Check
            compliance_status = self._check_compliance(
                generation_result, evaluation_result, prompt_frame
            )
            
            # 9. Kosten-Berechnung
            total_cost = self._calculate_costs(
                generation_result, optimization_result, ab_test_result
            )
            
            # Erstelle Pipeline-Ergebnis
            execution_time = time.time() - start_time
            pipeline_result = PipelineResult(
                run_id=run_id,
                prompt_frame=prompt_frame,
                generation_result=generation_result,
                evaluation_result=evaluation_result,
                optimization_result=optimization_result,
                ab_test_result=ab_test_result,
                feedback_entries=feedback_entries,
                compliance_status=compliance_status,
                total_cost=total_cost,
                execution_time=execution_time,
                metadata={
                    "template_hash": prompt_hash,
                    "pipeline_version": "2.0.0",
                    "components_used": [
                        "LayeredCompositionEngine",
                        "PromptOptimizer",
                        "RobustnessManager",
                        "TargetGroupEvaluator",
                        "UserFeedbackSystem"
                    ]
                }
            )
            
            # Update Statistiken
            self._update_pipeline_stats(pipeline_result)
            
            logger.info(f"Pipeline erfolgreich abgeschlossen: {run_id}")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"Pipeline-Fehler: {e}")
            execution_time = time.time() - start_time
            
            # Erstelle Fehler-Ergebnis
            error_result = PipelineResult(
                run_id=run_id,
                prompt_frame=prompt_frame,
                generation_result=GenerationResult(success=False, errors=[str(e)]),
                evaluation_result=EvaluationResult(
                    overall_score=0.0,
                    readability_score=0.0,
                    age_appropriateness=0.0,
                    genre_compliance=0.0,
                    emotional_depth=0.0,
                    engagement_score=0.0,
                    flags=["PIPELINE_ERROR"],
                    recommendations=[f"Pipeline-Fehler: {str(e)}"]
                ),
                compliance_status="failed",
                total_cost=0.0,
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
            
            self._update_pipeline_stats(error_result)
            return error_result
    
    def _generate_with_retry(self, 
                           prompt: str,
                           prompt_frame: PromptFrame,
                           template: PromptTemplate,
                           max_retries: int) -> GenerationResult:
        """Generiert Text mit Retry-Mechanismus"""
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Generiere Text
                response = self.generator.generate_text(prompt)
                
                # Parse bilinguale Antwort
                german_text, english_text = self._parse_bilingual_response(response)
                
                # Erstelle Generation-Ergebnis
                generation_result = GenerationResult(
                    success=True,
                    german_text=german_text,
                    english_text=english_text,
                    prompt_hash=self.compiler.calculate_template_hash(template),
                    template_hash=template.get_hash(),
                    word_count=len(german_text.split()),
                    retry_count=retry_count
                )
                
                # Validiere Ergebnis
                validation_result = self.robustness_manager.validate_generation_result(
                    generation_result, prompt_frame.age_group
                )
                
                # Wenn Retry benötigt wird
                if validation_result["retry_needed"] and retry_count < max_retries:
                    logger.info(f"Retry {retry_count + 1}/{max_retries} aufgrund von Validierungsproblemen")
                    
                    # Wende Retry-Anweisungen an
                    modified_prompt = self.robustness_manager.apply_retry_instructions(
                        prompt, validation_result["retry_instructions"]
                    )
                    
                    # Aktualisiere Prompt für nächsten Versuch
                    prompt = modified_prompt
                    retry_count += 1
                    continue
                
                # Erfolgreich oder maximale Retries erreicht
                generation_result.retry_count = retry_count
                generation_result.metadata["validation_result"] = validation_result
                
                return generation_result
                
            except Exception as e:
                logger.error(f"Generierungs-Fehler (Versuch {retry_count + 1}): {e}")
                retry_count += 1
                
                if retry_count > max_retries:
                    return GenerationResult(
                        success=False,
                        errors=[f"Maximale Retries erreicht: {str(e)}"],
                        retry_count=retry_count
                    )
        
        return GenerationResult(
            success=False,
            errors=["Unbekannter Fehler bei Text-Generierung"],
            retry_count=retry_count
        )
    
    def _parse_bilingual_response(self, response: str) -> Tuple[str, str]:
        """Parst bilinguale Antwort"""
        try:
            if "---" in response:
                parts = response.split("---")
                if len(parts) >= 2:
                    german_text = parts[0].strip()
                    english_text = parts[1].strip()
                    return german_text, english_text
            
            # Fallback: Verwende gesamte Antwort als deutsche Version
            return response.strip(), ""
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen der bilingualen Antwort: {e}")
            return response.strip(), ""
    
    def _evaluate_generation(self, 
                           generation_result: GenerationResult,
                           prompt_frame: PromptFrame) -> EvaluationResult:
        """Evaluiert Generierungs-Ergebnis"""
        if not generation_result.success:
            return EvaluationResult(
                overall_score=0.0,
                readability_score=0.0,
                age_appropriateness=0.0,
                genre_compliance=0.0,
                emotional_depth=0.0,
                engagement_score=0.0,
                flags=["GENERATION_FAILED"],
                recommendations=["Text-Generierung fehlgeschlagen"]
            )
        
        # Evaluiere deutsche Version
        evaluation = self.evaluator.evaluate_for_target_group(
            text=generation_result.german_text,
            age_group=prompt_frame.age_group,
            genre=prompt_frame.genre,
            language="de"
        )
        
        return evaluation
    
    def _optimize_prompt(self, 
                        template: PromptTemplate,
                        prompt_frame: PromptFrame,
                        evaluation_result: EvaluationResult) -> Optional[OptimizationResult]:
        """Optimiert Prompt basierend auf Evaluation"""
        try:
            # Bestimme Optimierungs-Fokus basierend auf Evaluation
            optimization_focus = self._determine_optimization_focus(evaluation_result)
            
            # Führe Optimierung durch
            optimization_result = self.optimizer.optimize_prompt_with_claude(
                template=template,
                prompt_frame={
                    "age_group": prompt_frame.age_group,
                    "genre": prompt_frame.genre,
                    "emotion": prompt_frame.emotion,
                    "target_words": self._get_target_words(prompt_frame.age_group)
                },
                optimization_focus=optimization_focus
            )
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Optimierungs-Fehler: {e}")
            return None
    
    def _determine_optimization_focus(self, evaluation_result: EvaluationResult) -> str:
        """Bestimmt Fokus für Optimierung"""
        scores = {
            "readability": evaluation_result.readability_score,
            "age_appropriateness": evaluation_result.age_appropriateness,
            "genre_compliance": evaluation_result.genre_compliance,
            "emotional_depth": evaluation_result.emotional_depth,
            "engagement": evaluation_result.engagement_score
        }
        
        # Finde niedrigsten Score
        min_score_key = min(scores, key=scores.get)
        min_score = scores[min_score_key]
        
        if min_score < 0.5:
            return f"Verbessere {min_score_key}"
        else:
            return "Erhöhe emotionale Tiefe und Engagement"
    
    def _get_target_words(self, age_group: str) -> int:
        """Gibt Zielwortanzahl für Altersgruppe zurück"""
        targets = {
            "preschool": 200,
            "early_reader": 400,
            "middle_grade": 800,
            "young_adult": 1200,
            "adult": 1500
        }
        return targets.get(age_group, 800)
    
    def _run_ab_test(self, 
                    original_result: GenerationResult,
                    optimization_result: OptimizationResult,
                    prompt_frame: PromptFrame) -> Optional[ABTestResult]:
        """Führt A/B-Test durch"""
        try:
            # Generiere Text mit optimiertem Prompt
            optimized_prompt = self.optimizer._generate_raw_prompt(
                self._create_template_from_hash(optimization_result.optimized_prompt_hash)
            )
            
            optimized_response = self.generator.generate_text(optimized_prompt)
            optimized_german, optimized_english = self._parse_bilingual_response(optimized_response)
            
            # Erstelle optimiertes Ergebnis
            optimized_generation = GenerationResult(
                success=True,
                german_text=optimized_german,
                english_text=optimized_english,
                prompt_hash=optimization_result.optimized_prompt_hash,
                word_count=len(optimized_german.split())
            )
            
            # Evaluiere optimiertes Ergebnis
            optimized_evaluation = self._evaluate_generation(optimized_generation, prompt_frame)
            
            # Vergleiche Ergebnisse
            comparison = {
                "original_score": original_result.metadata.get("quality_score", 0),
                "optimized_score": optimized_evaluation.overall_score,
                "score_delta": optimized_evaluation.overall_score - original_result.metadata.get("quality_score", 0),
                "improvement_percentage": 0
            }
            
            if comparison["original_score"] > 0:
                comparison["improvement_percentage"] = (
                    comparison["score_delta"] / comparison["original_score"]
                ) * 100
            
            significant_improvement = comparison["score_delta"] > 0.1
            
            return ABTestResult(
                test_id=f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                segment=f"{prompt_frame.age_group}_{prompt_frame.genre}",
                original_result=original_result,
                optimized_result=optimized_generation,
                comparison=comparison,
                significant_improvement=significant_improvement,
                recommendation="Optimierte Version verwenden" if significant_improvement else "Original beibehalten"
            )
            
        except Exception as e:
            logger.error(f"A/B-Test-Fehler: {e}")
            return None
    
    def _create_template_from_hash(self, template_hash: str) -> PromptTemplate:
        """Erstellt Template aus Hash (vereinfachte Implementierung)"""
        # Vereinfachte Implementierung - in der Praxis würde hier ein Template-Lookup erfolgen
        return PromptTemplate(
            template_id=f"template_{template_hash}",
            name="Optimized Template",
            description="Template aus Optimierung",
            layers=[],
            version="2.0.0"
        )
    
    def _collect_feedback(self, 
                         generation_result: GenerationResult,
                         evaluation_result: EvaluationResult,
                         prompt_frame: PromptFrame) -> List[FeedbackEntry]:
        """Sammelt Feedback"""
        feedback_entries = []
        
        try:
            # Simuliere Nutzer-Feedback basierend auf Evaluation
            quality_score = evaluation_result.overall_score
            
            if quality_score > 0.8:
                user_rating = 5
                comment = f"Exzellente {prompt_frame.genre}-Geschichte für {prompt_frame.age_group}"
            elif quality_score > 0.6:
                user_rating = 4
                comment = f"Gute {prompt_frame.genre}-Geschichte mit Verbesserungspotential"
            elif quality_score > 0.4:
                user_rating = 3
                comment = f"Durchschnittliche Qualität für {prompt_frame.genre}"
            else:
                user_rating = 2
                comment = f"Qualität verbesserungsbedürftig für {prompt_frame.genre}"
            
            # Sammle Feedback
            feedback_entry = FeedbackEntry(
                chapter_number=1,
                prompt_hash=generation_result.prompt_hash,
                quality_score=quality_score,
                user_rating=user_rating,
                comment=comment,
                language="de",
                metadata={
                    "age_group": prompt_frame.age_group,
                    "genre": prompt_frame.genre,
                    "emotion": prompt_frame.emotion,
                    "evaluation_scores": {
                        "readability": evaluation_result.readability_score,
                        "age_appropriateness": evaluation_result.age_appropriateness,
                        "genre_compliance": evaluation_result.genre_compliance,
                        "emotional_depth": evaluation_result.emotional_depth,
                        "engagement": evaluation_result.engagement_score
                    }
                }
            )
            
            self.feedback_system.collect_feedback(
                chapter_number=feedback_entry.chapter_number,
                prompt_hash=feedback_entry.prompt_hash,
                quality_score=feedback_entry.quality_score,
                language=feedback_entry.language,
                rating=feedback_entry.user_rating,
                comment=feedback_entry.comment,
                metadata=feedback_entry.metadata
            )
            
            feedback_entries.append(feedback_entry)
            
        except Exception as e:
            logger.error(f"Feedback-Sammlungs-Fehler: {e}")
        
        return feedback_entries
    
    def _check_compliance(self, 
                         generation_result: GenerationResult,
                         evaluation_result: EvaluationResult,
                         prompt_frame: PromptFrame) -> str:
        """Prüft Compliance"""
        compliance_checks = []
        
        # System Note Check
        if "WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR" in generation_result.german_text:
            compliance_checks.append("system_note_present")
        
        # Bilingual Check
        if generation_result.english_text and len(generation_result.english_text) > 50:
            compliance_checks.append("bilingual_present")
        
        # Quality Score Check
        if evaluation_result.overall_score >= 0.7:
            compliance_checks.append("quality_threshold_met")
        
        # Age Appropriateness Check
        if evaluation_result.age_appropriateness >= 0.8:
            compliance_checks.append("age_appropriate")
        
        # Genre Compliance Check
        if evaluation_result.genre_compliance >= 0.5:
            compliance_checks.append("genre_compliant")
        
        # Bestimme Compliance-Status
        if len(compliance_checks) >= 4:
            return "full"
        elif len(compliance_checks) >= 3:
            return "partial"
        else:
            return "failed"
    
    def _calculate_costs(self, 
                        generation_result: GenerationResult,
                        optimization_result: Optional[OptimizationResult],
                        ab_test_result: Optional[ABTestResult]) -> float:
        """Berechnet Gesamtkosten"""
        total_cost = 0.0
        
        # Basis-Generierung (geschätzt)
        if generation_result.success:
            word_count = generation_result.word_count
            total_cost += word_count * 0.0001  # Geschätzte Kosten pro Wort
        
        # Optimierung
        if optimization_result:
            total_cost += 0.01  # Geschätzte Claude-Kosten
        
        # A/B-Test
        if ab_test_result:
            total_cost += ab_test_result.optimized_result.word_count * 0.0001
        
        return total_cost
    
    def _update_pipeline_stats(self, pipeline_result: PipelineResult):
        """Aktualisiert Pipeline-Statistiken"""
        self.pipeline_stats["total_runs"] += 1
        
        if pipeline_result.compliance_status != "failed":
            self.pipeline_stats["successful_runs"] += 1
        else:
            self.pipeline_stats["failed_runs"] += 1
        
        # Update durchschnittliche Ausführungszeit
        current_avg = self.pipeline_stats["average_execution_time"]
        total_runs = self.pipeline_stats["total_runs"]
        self.pipeline_stats["average_execution_time"] = (
            (current_avg * (total_runs - 1) + pipeline_result.execution_time) / total_runs
        )
        
        # Update Gesamtkosten
        self.pipeline_stats["total_cost"] += pipeline_result.total_cost
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Gibt Pipeline-Statistiken zurück"""
        return self.pipeline_stats.copy()
    
    def run_batch_pipeline(self, 
                          prompt_frames: List[PromptFrame],
                          **kwargs) -> List[PipelineResult]:
        """Führt Batch-Pipeline für mehrere PromptFrames aus"""
        results = []
        
        for i, prompt_frame in enumerate(prompt_frames, 1):
            logger.info(f"Batch-Pipeline: Verarbeite {i}/{len(prompt_frames)}")
            
            result = self.run_enhanced_pipeline(prompt_frame, **kwargs)
            results.append(result)
        
        return results

# Registrierte Version der Enhanced Pipeline
class EnhancedPipelineComponent(EnhancedPipeline):
    """Registrierte Version der Enhanced Pipeline"""
    def __init__(self):
        super().__init__() 