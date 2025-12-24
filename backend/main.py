"""Entry point for FastAPI app - can be run from anywhere"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    # Use PORT from environment (Railway provides this) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    # Always use "app:app" since we're in the backend directory
    # The path setup above ensures imports work correctly
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
    )

