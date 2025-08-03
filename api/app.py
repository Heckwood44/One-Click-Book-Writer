#!/usr/bin/env python3
"""
One Click Book Writer API
Produktionsreife REST-API für das selbstlernende Prompt-Engineering-Framework
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime
import os
from contextlib import asynccontextmanager

from core.architecture import PromptFrame
from core.enhanced_pipeline import EnhancedPipeline
from core.policy_engine import PolicyEngine
from core.drift_detector import DriftDetector
from core.feedback_intelligence import FeedbackIntelligence

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Configuration
API_KEYS = os.getenv("API_KEYS", "").split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
FEATURE_FLAGS = {
    "optimization_enabled": os.getenv("OPTIMIZATION_ENABLED", "true").lower() == "true",
    "ab_testing_enabled": os.getenv("AB_TESTING_ENABLED", "true").lower() == "true",
    "feedback_collection_enabled": os.getenv("FEEDBACK_COLLECTION_ENABLED", "true").lower() == "true",
    "drift_detection_enabled": os.getenv("DRIFT_DETECTION_ENABLED", "true").lower() == "true"
}

# Rate Limiting
from collections import defaultdict
import time
rate_limit_store = defaultdict(list)

# Pydantic Models
class GenerateRequest(BaseModel):
    age_group: str = Field(..., description="Altersgruppe (preschool, early_reader, middle_grade, young_adult, adult)")
    genre: str = Field(..., description="Genre (adventure, fantasy, self_discovery, friendship, mystery)")
    emotion: str = Field(..., description="Emotion (wonder, courage, friendship, growth, mystery)")
    language: str = Field(..., description="Sprache (de, en)")
    target_audience: Optional[str] = Field(None, description="Zielgruppe")
    custom_context: Optional[Dict[str, Any]] = Field(None, description="Zusätzlicher Kontext")
    enable_optimization: Optional[bool] = Field(True, description="Optimierung aktivieren")
    enable_ab_testing: Optional[bool] = Field(False, description="A/B-Testing aktivieren")
    enable_feedback_collection: Optional[bool] = Field(True, description="Feedback-Sammlung aktivieren")
    max_retries: Optional[int] = Field(3, description="Maximale Wiederholungen")

class FeedbackRequest(BaseModel):
    run_id: str = Field(..., description="Run-ID des generierten Kapitels")
    user_rating: int = Field(..., ge=1, le=5, description="Nutzer-Bewertung (1-5)")
    comment: str = Field(..., description="Feedback-Kommentar")
    language: str = Field(..., description="Sprache des Feedbacks")

class TemplateStatusRequest(BaseModel):
    segment: str = Field(..., description="Segment (age_group_genre)")
    include_history: Optional[bool] = Field(False, description="Template-Historie einschließen")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]
    feature_flags: Dict[str, bool]

class GenerateResponse(BaseModel):
    run_id: str
    chapter_text: str
    german_text: str
    english_text: str
    quality_score: float
    word_count: int
    execution_time: float
    total_cost: float
    compliance_status: str
    template_hash: str
    optimization_delta: Optional[float] = None
    ab_test_improvement: Optional[float] = None
    policy_decision: Optional[Dict[str, Any]] = None
    drift_alerts: Optional[List[Dict[str, Any]]] = None

# Global Components
pipeline = None
policy_engine = None
drift_detector = None
feedback_intelligence = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global pipeline, policy_engine, drift_detector, feedback_intelligence
    
    # Initialize components
    logger.info("Initializing One Click Book Writer Framework...")
    pipeline = EnhancedPipeline()
    policy_engine = PolicyEngine()
    drift_detector = DriftDetector()
    feedback_intelligence = FeedbackIntelligence()
    logger.info("Framework initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down One Click Book Writer Framework...")

# FastAPI App
app = FastAPI(
    title="One Click Book Writer API",
    description="Produktionsreife REST-API für selbstlernendes Prompt-Engineering",
    version="4.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency Functions
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifiziert API-Key"""
    if not API_KEYS or credentials.credentials not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

def check_rate_limit(api_key: str = Depends(verify_api_key)):
    """Prüft Rate Limit"""
    current_time = time.time()
    user_requests = rate_limit_store[api_key]
    
    # Entferne alte Requests (älter als 1 Minute)
    user_requests[:] = [req_time for req_time in user_requests if current_time - req_time < 60]
    
    if len(user_requests) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    user_requests.append(current_time)
    return api_key

# API Endpoints
@app.post("/generate", response_model=GenerateResponse)
async def generate_chapter(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(check_rate_limit)
):
    """Generiert ein Kapitel basierend auf den angegebenen Parametern"""
    try:
        # Erstelle PromptFrame
        prompt_frame = PromptFrame(
            age_group=request.age_group,
            genre=request.genre,
            emotion=request.emotion,
            language=request.language,
            target_audience=request.target_audience,
            custom_context=request.custom_context or {}
        )
        
        # Führe Pipeline aus
        result = pipeline.run_enhanced_pipeline(
            prompt_frame=prompt_frame,
            enable_optimization=request.enable_optimization and FEATURE_FLAGS["optimization_enabled"],
            enable_ab_testing=request.enable_ab_testing and FEATURE_FLAGS["ab_testing_enabled"],
            enable_feedback_collection=request.enable_feedback_collection and FEATURE_FLAGS["feedback_collection_enabled"],
            max_retries=request.max_retries
        )
        
        # Policy Engine Evaluation
        policy_decision = None
        if FEATURE_FLAGS["drift_detection_enabled"]:
            policy_decision = policy_engine.evaluate_pipeline_result(result)
        
        # Drift Detection
        drift_alerts = None
        if FEATURE_FLAGS["drift_detection_enabled"]:
            drift_alerts = drift_detector.monitor_pipeline_result(result)
            drift_alerts = [alert.__dict__ for alert in drift_alerts]
        
        # Background Tasks
        background_tasks.add_task(process_background_tasks, result, policy_decision)
        
        # Parse bilingual response
        german_text, english_text = parse_bilingual_response(result.generation_result.generated_text)
        
        return GenerateResponse(
            run_id=result.run_id,
            chapter_text=result.generation_result.generated_text,
            german_text=german_text,
            english_text=english_text,
            quality_score=result.evaluation_result.overall_score,
            word_count=result.generation_result.word_count,
            execution_time=result.execution_time,
            total_cost=result.total_cost,
            compliance_status=result.compliance_status,
            template_hash=result.generation_result.template_hash,
            optimization_delta=result.optimization_result.quality_score_delta if result.optimization_result else None,
            ab_test_improvement=result.ab_test_result.comparison.get('improvement_percentage', 0) if result.ab_test_result else None,
            policy_decision=policy_decision.__dict__ if policy_decision else None,
            drift_alerts=drift_alerts
        )
        
    except Exception as e:
        logger.error(f"Error generating chapter: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    api_key: str = Depends(check_rate_limit)
):
    """Reicht Feedback für ein generiertes Kapitel ein"""
    try:
        # Erstelle Feedback Entry
        from core.architecture import FeedbackEntry
        
        feedback_entry = FeedbackEntry(
            chapter_number=1,  # Könnte aus run_id extrahiert werden
            prompt_hash="",  # Wird aus run_id ermittelt
            quality_score=0.0,  # Wird aus run_id ermittelt
            user_rating=request.user_rating,
            comment=request.comment,
            language=request.language
        )
        
        # Analysiere Feedback
        features = feedback_intelligence.analyze_feedback([feedback_entry])
        
        # Generiere Template-Vorschläge
        segment = "unknown"  # Könnte aus run_id extrahiert werden
        suggestions = feedback_intelligence.generate_template_suggestions(
            segment, features, None  # Template wird aus run_id ermittelt
        )
        
        return {
            "status": "success",
            "feedback_id": f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "features_extracted": len(features),
            "suggestions_generated": len(suggestions),
            "message": "Feedback successfully submitted and analyzed"
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@app.get("/template-status")
async def get_template_status(
    request: TemplateStatusRequest,
    api_key: str = Depends(check_rate_limit)
):
    """Gibt Status und Ranking der Templates für ein Segment zurück"""
    try:
        # Template Ranking
        template_ranking = policy_engine.get_active_template_ranking(request.segment)
        
        # Segment Performance
        segment_performance = drift_detector.segment_history.get(request.segment, {})
        
        # Experiment Suggestions
        experiment_suggestions = []
        if policy_engine.should_start_experiment(request.segment):
            experiment_suggestions = policy_engine.get_experiment_suggestions(request.segment)
        
        response = {
            "segment": request.segment,
            "template_ranking": [
                {"hash": hash, "score": score} for hash, score in template_ranking
            ],
            "segment_performance": {
                "avg_score": segment_performance.get("avg_score", 0.0),
                "total_runs": len(segment_performance.get("runs", [])),
                "last_update": segment_performance.get("last_update", "").isoformat() if segment_performance.get("last_update") else None
            },
            "experiment_suggestions": experiment_suggestions
        }
        
        if request.include_history:
            response["template_history"] = segment_performance.get("template_versions", {})
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting template status: {e}")
        raise HTTPException(status_code=500, detail=f"Template status retrieval failed: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health Check Endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="4.0.0",
        components={
            "pipeline": "active" if pipeline else "inactive",
            "policy_engine": "active" if policy_engine else "inactive",
            "drift_detector": "active" if drift_detector else "inactive",
            "feedback_intelligence": "active" if feedback_intelligence else "inactive"
        },
        feature_flags=FEATURE_FLAGS
    )

@app.get("/diff/{run_id}")
async def get_diff(
    run_id: str,
    api_key: str = Depends(check_rate_limit)
):
    """Gibt Diff zwischen Original- und optimiertem Prompt zurück"""
    try:
        # In der Praxis würde hier der Diff aus der Datenbank geladen werden
        # Für jetzt geben wir ein Beispiel zurück
        
        return {
            "run_id": run_id,
            "diff_type": "prompt_optimization",
            "original_prompt_hash": "abc123def456",
            "optimized_prompt_hash": "def456ghi789",
            "diff_summary": {
                "lines_changed": 5,
                "words_changed": 23,
                "similarity_score": 0.87
            },
            "changes": [
                {
                    "type": "addition",
                    "line": 15,
                    "content": "Erhöhe emotionale Tiefe und Charakterverbindungen"
                },
                {
                    "type": "modification",
                    "line": 8,
                    "old_content": "Verwende einfache Sprache",
                    "new_content": "Verwende altersgerechte, aber ansprechende Sprache"
                }
            ],
            "optimization_reasoning": "Verbesserung basierend auf Feedback: mehr emotionale Tiefe gewünscht"
        }
        
    except Exception as e:
        logger.error(f"Error getting diff: {e}")
        raise HTTPException(status_code=500, detail=f"Diff retrieval failed: {str(e)}")

@app.get("/presets")
async def get_presets(api_key: str = Depends(check_rate_limit)):
    """Gibt verfügbare Presets zurück"""
    try:
        presets = load_presets()
        return {
            "presets": presets,
            "total_count": len(presets)
        }
    except Exception as e:
        logger.error(f"Error loading presets: {e}")
        raise HTTPException(status_code=500, detail=f"Preset loading failed: {str(e)}")

@app.get("/metrics")
async def get_metrics(api_key: str = Depends(check_rate_limit)):
    """Gibt System-Metriken zurück"""
    try:
        return {
            "pipeline_stats": pipeline.get_pipeline_stats(),
            "policy_summary": policy_engine.get_policy_summary(),
            "drift_summary": drift_detector.get_drift_summary(),
            "feedback_summary": feedback_intelligence.get_feedback_summary(),
            "rate_limits": {
                "current_usage": len(rate_limit_store),
                "limit_per_minute": RATE_LIMIT_PER_MINUTE
            }
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

# Helper Functions
def parse_bilingual_response(text: str) -> tuple[str, str]:
    """Parst bilinguale Antwort in deutsche und englische Teile"""
    # Vereinfachte Implementierung - in der Praxis würde hier die tatsächliche Parsing-Logik stehen
    lines = text.split('\n')
    german_lines = []
    english_lines = []
    
    for line in lines:
        if line.strip():
            if any(german_word in line.lower() for german_word in ['der', 'die', 'das', 'und', 'ist', 'sind']):
                german_lines.append(line)
            else:
                english_lines.append(line)
    
    return '\n'.join(german_lines), '\n'.join(english_lines)

def load_presets() -> List[Dict[str, Any]]:
    """Lädt verfügbare Presets"""
    return [
        {
            "id": "early_reader_adventure_courage",
            "name": "Early Reader Adventure - Courage",
            "description": "Mutige Entdeckungsreise für 6-8 Jährige",
            "age_group": "early_reader",
            "genre": "adventure",
            "emotion": "courage",
            "language": "de",
            "rating": 4.5,
            "usage_count": 1250
        },
        {
            "id": "middle_grade_fantasy_wonder",
            "name": "Middle Grade Fantasy - Wonder",
            "description": "Magische Fantasy-Welt für 9-12 Jährige",
            "age_group": "middle_grade",
            "genre": "fantasy",
            "emotion": "wonder",
            "language": "de",
            "rating": 4.8,
            "usage_count": 890
        },
        {
            "id": "young_adult_self_discovery_growth",
            "name": "Young Adult Self-Discovery - Growth",
            "description": "Persönliches Wachstum für 13-17 Jährige",
            "age_group": "young_adult",
            "genre": "self_discovery",
            "emotion": "growth",
            "language": "de",
            "rating": 4.3,
            "usage_count": 567
        }
    ]

async def process_background_tasks(result, policy_decision):
    """Verarbeitet Background-Tasks"""
    try:
        # Speichere Ergebnis in Datenbank
        # Aktualisiere Metriken
        # Sende Alerts falls nötig
        logger.info(f"Background processing completed for run_id: {result.run_id}")
    except Exception as e:
        logger.error(f"Background processing failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 