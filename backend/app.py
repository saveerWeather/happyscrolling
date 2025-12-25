"""FastAPI application"""
import sys
import os
from pathlib import Path

# Add current directory and project root to Python path
# This works whether running from project root or backend directory
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()

# Add current directory first (for Railway when root is /backend)
# This MUST be first so imports work when running from backend directory
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use direct imports (Railway runs from /backend directory)
# The path setup above ensures these imports work
from config import settings
from utils.database import engine, Base
from routes import auth, feed, settings as settings_routes

# Log CORS origins for debugging
logger.info(f"CORS origins configured: {settings.cors_origins}")
logger.info(f"CORS origins type: {type(settings.cors_origins)}")
logger.info(f"CORS origins length: {len(settings.cors_origins)}")

# Create database tables (with error handling)
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}", exc_info=True)
    # Don't crash - tables might already exist

app = FastAPI(
    title="Happy Scrolling API",
    description="Email feed aggregator API",
    version="1.0.0"
)

# CORS middleware (MUST be before Session middleware for preflight requests)
# Log what we're actually using
logger.info(f"Setting CORS with origins: {settings.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["*"],
    max_age=3600,
)

# Session middleware (after CORS)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,  # Reuse JWT secret for session signing
    max_age=60 * 60 * 24 * 7,  # 7 days
    same_site="lax"
)

# Add request logging middleware (after CORS)
@app.middleware("http")
async def log_requests(request, call_next):
    origin = request.headers.get("origin", "no origin")
    logger.info(f"{request.method} {request.url.path} from origin: {origin}")
    response = await call_next(request)
    # Log CORS headers in response
    cors_origin = response.headers.get("access-control-allow-origin", "not set")
    logger.info(f"{request.method} {request.url.path} - {response.status_code} | CORS origin: {cors_origin}")
    return response

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

