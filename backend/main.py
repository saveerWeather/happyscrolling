"""Entry point for FastAPI app - can be run from anywhere"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import os
    import uvicorn
    # Use PORT from environment (Railway provides this) or default to 8000
    port = int(os.getenv("PORT", 8000))
    # Use import string format for reload to work properly
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
    )

