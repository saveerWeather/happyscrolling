"""FastAPI application"""
import sys
from pathlib import Path

# Add current directory and project root to Python path
# This works whether running from project root or backend directory
current_dir = Path(__file__).parent
project_root = current_dir.parent

# Add current directory first (for Railway when root is /backend)
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
# Add project root (for local development)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, that's okay

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Try imports with backend prefix first, fallback to direct imports
try:
    from backend.config import settings
    from backend.utils.database import engine, Base
    from backend.routes import auth, feed, settings as settings_routes
except ImportError:
    # Running from backend directory - use direct imports
    from config import settings
    from utils.database import engine, Base
    from routes import auth, feed, settings as settings_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Happy Scrolling API",
    description="Email feed aggregator API",
    version="1.0.0"
)

# Session middleware (must be before CORS)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,  # Reuse JWT secret for session signing
    max_age=60 * 60 * 24 * 7,  # 7 days
    same_site="lax"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(settings_routes.router)

@app.get("/")
def root():
    return {"message": "Happy Scrolling API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/debug/db")
def debug_db():
    """Debug endpoint to see which database is being used"""
    try:
        from backend.utils.database import DATABASE_URL, USE_POSTGRES
    except ImportError:
        from utils.database import DATABASE_URL, USE_POSTGRES
    
    db_type = "PostgreSQL" if USE_POSTGRES and not DATABASE_URL.startswith('sqlite') else "SQLite"
    # Hide password in URL for security
    safe_url = DATABASE_URL
    if '@' in DATABASE_URL:
        parts = DATABASE_URL.split('@')
        if len(parts) == 2:
            safe_url = parts[0].split('//')[0] + '//***@' + parts[1]
    
    return {
        "database_type": db_type,
        "database_url": safe_url,
        "using_postgres": USE_POSTGRES and not DATABASE_URL.startswith('sqlite')
    }

