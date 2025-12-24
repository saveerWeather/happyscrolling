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
    # Import app directly instead of using string import
    # This ensures all path setup happens before uvicorn tries to load it
    from app import app
    
    # Use PORT from environment (Railway provides this) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
    )

