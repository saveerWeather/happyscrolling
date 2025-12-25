"""Entry point for FastAPI app - can be run from anywhere"""
import sys
import os
from pathlib import Path

# Add current directory (backend) to Python path first
# This ensures imports work when running from backend directory
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Add project root to Python path (for local development)
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Configure logging to output to stdout (Railway captures this)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 50)
        logger.info("Starting FastAPI application...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
        logger.info("=" * 50)
        
        # Use string import for uvicorn - this is the standard way
        # The path setup above ensures imports work correctly
        logger.info("Using string import for uvicorn: 'app:app'")
        
        # Use PORT from environment (Railway provides this) or default to 8000
        port = int(os.getenv("PORT", 8000))
        logger.info(f"Starting server on 0.0.0.0:{port}")
        logger.info("=" * 50)
        
        logger.info("Starting uvicorn server...")
        # Use string import for uvicorn - uvicorn will import the app module
        # and access the 'app' attribute from it
        uvicorn.run(
            "app:app",  # String import - uvicorn will import app.app
            host="0.0.0.0",
            port=port,
            reload=False,  # Disable reload in production
            log_level="info",
            access_log=True,  # Enable access logs
        )
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"CRITICAL: Failed to start application: {e}", exc_info=True)
        logger.error("=" * 50)
        # Don't raise - let Railway see the error in logs
        sys.exit(1)

