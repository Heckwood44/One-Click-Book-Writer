#!/usr/bin/env python3
"""
One Click Book Writer - Minimal Smoke Test
Tests basic imports and pipeline initialization
"""

import sys
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

def run_minimal_smoke_test() -> bool:
    """Run a minimal smoke test for basic functionality"""
    logger.info("🧪 Starting Minimal Smoke Test")
    logger.info("=" * 60)
    
    try:
        # Test 1: Import pipeline
        from build_and_execute import OneClickBookWriterPipeline
        logger.info("✅ Pipeline import successful")
        
        # Test 2: Initialize pipeline
        pipeline = OneClickBookWriterPipeline()
        logger.info("✅ Pipeline initialized")
        
        # Test 3: Load PromptFrame
        prompt_frame = pipeline.load_prompt_frame()
        logger.info("✅ PromptFrame loaded")
        
        # Test 4: Basic validation
        from compiler.prompt_compiler import validate_prompt_structure
        from schema.validate_input import validate_json_schema
        
        schema_valid = validate_json_schema(prompt_frame, str(pipeline.schema_file))
        structure_valid = validate_prompt_structure(prompt_frame)
        
        if not (schema_valid and structure_valid):
            logger.error("❌ Validation failed")
            return False
        
        logger.info("✅ Validation passed")
        
        # Test 5: Compile prompt
        prompt = pipeline.compile_prompt(prompt_frame, optimize_with_claude=False)
        if len(prompt) < 100:
            logger.error("❌ Prompt too short")
            return False
        
        logger.info(f"✅ Prompt compiled (length: {len(prompt)})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        return False

def main():
    """Run the smoke test"""
    success = run_minimal_smoke_test()
    
    if success:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("💥 Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
