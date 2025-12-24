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
    
    # Check if we're running from backend directory (Railway) or project root (local)
    # If CWD is backend, use "app:app", otherwise use "backend.app:app"
    cwd = Path.cwd()
    if cwd.name == "backend" or str(cwd).endswith("/backend"):
        # Running from backend directory - import directly
        app_import = "app:app"
    else:
        # Running from project root - use backend prefix
        app_import = "backend.app:app"
    
    uvicorn.run(
        app_import,
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
    )

