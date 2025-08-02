#!/usr/bin/env python3
"""
One Click Book Writer - Comprehensive Smoke Test
Tests the complete pipeline including chapter generation
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_comprehensive_smoke_test() -> bool:
    """Run a comprehensive smoke test including chapter generation"""
    logger.info("🧪 Starting Comprehensive Smoke Test")
    logger.info("=" * 60)
    
    try:
        # Test 1: Import current pipeline
        from prompt_router import PromptRouter
        logger.info("✅ PromptRouter import successful")
        
        # Test 2: Initialize router
        router = PromptRouter()
        logger.info("✅ Router initialized")
        
        # Test 3: Load and validate PromptFrame
        input_file = project_root / "data" / "generate_chapter_full_extended.json"
        if not input_file.exists():
            logger.error(f"❌ Input file not found: {input_file}")
            return False
        
        with open(input_file, 'r', encoding='utf-8') as f:
            prompt_frame = json.load(f)
        logger.info("✅ PromptFrame loaded")
        
        # Test 4: Validate structure
        from compiler.prompt_compiler import validate_prompt_structure
        from schema.validate_input import validate_json_schema
        
        schema_file = project_root / "schema" / "prompt_frame.schema.json"
        if schema_file.exists():
            success, message = validate_json_schema(prompt_frame, str(schema_file))
            if not success:
                logger.error(f"❌ Schema validation failed: {message}")
                return False
            logger.info("✅ Schema validation passed")
        
        if not validate_prompt_structure(prompt_frame):
            logger.error("❌ Structure validation failed")
            return False
        logger.info("✅ Structure validation passed")
        
        # Test 5: Compile prompt
        from compiler.prompt_compiler import compile_prompt_for_chatgpt, generate_prompt_hash
        
        prompt = compile_prompt_for_chatgpt(prompt_frame)
        prompt_hash = generate_prompt_hash(prompt)
        
        if len(prompt) < 100:
            logger.error("❌ Prompt too short")
            return False
        
        # Check for required elements
        required_elements = ["---"]
        missing_elements = [elem for elem in required_elements if elem not in prompt]
        
        # System Note with signature check - Canvas Execution Plan
        system_note_signature = "SYSTEM NOTE SIGNATURE: WORLDCLASS_AUTHOR_ARCHITECT_INVISIBLE_TRANSLATOR"
        if system_note_signature in prompt:
            logger.info("✅ System Note with signature found (Canvas compliant)")
        elif "Ein Weltklasse-Autor ist kein" in prompt:
            logger.info("✅ System Note found (fuzzy match)")
        else:
            missing_elements.append("System Note")
        
        if missing_elements:
            logger.error(f"❌ Missing prompt elements: {missing_elements}")
            return False
        
        logger.info(f"✅ Prompt compiled (length: {len(prompt)}, hash: {prompt_hash[:8]})")
        
        # Test 6: Generate chapter (if API keys available)
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.warning("⚠️  OpenAI API key not found - skipping generation test")
            logger.info("✅ Smoke test completed (without generation)")
            return True
        
        logger.info("🚀 Starting chapter generation...")
        
        # Run pipeline
        result = router.run_full_pipeline(
            prompt_frame_path="data/generate_chapter_full_extended.json",
            optimize_with_claude=True,
            chapter_number=1
        )
        
        if not result["success"]:
            logger.error(f"❌ Generation failed: {result.get('errors', ['Unknown error'])}")
            return False
        
        logger.info("✅ Chapter generation successful")
        
        # Test 7: Verify output files
        output_files = result.get("output_files", {})
        required_files = ["german", "english", "metadata"]
        
        for file_type in required_files:
            file_path = output_files.get(file_type, "")
            if not file_path or not os.path.exists(file_path):
                logger.error(f"❌ Output file missing: {file_type}")
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.error(f"❌ Output file empty: {file_type}")
                return False
            
            logger.info(f"✅ {file_type} file created ({file_size} bytes)")
        
        # Test 8: Verify metadata structure
        meta_file = output_files.get("metadata", "")
        if meta_file and os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            required_meta_fields = [
                "chapter_number", "prompt_versioning", 
                "book_metadata", "quality_evaluation"
            ]
            
            missing_meta_fields = [field for field in required_meta_fields if field not in metadata]
            if missing_meta_fields:
                logger.error(f"❌ Missing metadata fields: {missing_meta_fields}")
                return False
            
            logger.info("✅ Metadata structure valid")
        
        # Test 9: Check quality evaluation
        quality_data = result.get("quality_evaluation", {})
        if quality_data:
            overall_score = quality_data.get("overall_bilingual_score", 0)
            logger.info(f"✅ Quality evaluation completed (score: {overall_score:.3f})")
            
            if overall_score < 0.3:
                logger.warning(f"⚠️  Low quality score: {overall_score}")
        
        logger.info("🎉 All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run the smoke test"""
    success = run_comprehensive_smoke_test()
    
    if success:
        logger.info("🎉 Smoke test completed successfully!")
        return 0
    else:
        logger.error("💥 Smoke test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
