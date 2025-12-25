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

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use direct imports (Railway runs from /backend directory)
# The path setup above ensures these imports work
try:
    from config import settings
    logger.info("Settings imported successfully")
except Exception as e:
    logger.error(f"Failed to import settings: {e}", exc_info=True)
    raise

try:
    from utils.database import engine, Base, DATABASE_URL, USE_POSTGRES, get_db
    is_postgres = USE_POSTGRES and DATABASE_URL and not DATABASE_URL.startswith('sqlite')
    logger.info(f"Database: {'PostgreSQL' if is_postgres else 'SQLite'}")
except Exception as e:
    logger.error(f"Failed to import database utilities: {e}")
    raise

try:
    from routes import auth, feed, settings as settings_routes
except Exception as e:
    logger.error(f"Failed to import routes: {e}")
    raise

logger.info(f"CORS origins: {settings.cors_origins}")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")

app = FastAPI(
    title="Happy Scrolling API",
    description="Email feed aggregator API",
    version="1.0.0"
)

# CORS middleware
cors_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"]
cors_headers = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
    "Cookie",
    "Set-Cookie",
    "X-CSRFToken",
    "X-CSRF-Token",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=cors_methods,
    allow_headers=cors_headers,
    expose_headers=["*"],
    max_age=3600,
)

# Session middleware
is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.jwt_secret,
    max_age=60 * 60 * 24 * 7,  # 7 days
    same_site="none" if is_production else "lax",
    https_only=is_production,
)
logger.info(f"Session: production={is_production}, same_site={'none' if is_production else 'lax'}")

# Request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error: {request.method} {request.url.path} - {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Include routers
app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(settings_routes.router)

@app.get("/")
def root():
    try:
        return {"message": "Happy Scrolling API", "status": "running"}
    except Exception as e:
        logger.error(f"Root endpoint failed: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}, 500

@app.get("/health")
def health():
    """Health check endpoint for Railway"""
    try:
        # Simple health check - no database or complex operations
        return {"status": "healthy", "service": "backend"}
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}, 500

@app.on_event("startup")
async def startup_event():
    logger.info("Application ready")

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

@app.get("/debug/cors")
def debug_cors(request: Request):
    """Debug endpoint to check CORS configuration"""
    origin = request.headers.get("origin", "no origin")
    return {
        "configured_origins": settings.cors_origins,
        "request_origin": origin,
        "origin_allowed": origin in settings.cors_origins if origin != "no origin" else False,
        "cors_methods": cors_methods,
        "cors_headers": cors_headers,
    }

@app.get("/debug/users")
def debug_users(db: Session = Depends(get_db)):
    """Debug endpoint to list all users (email only for security)"""
    from models import User
    users = db.query(User).all()
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "created_at": str(user.created_at)
            }
            for user in users
        ]
    }

@app.delete("/debug/users/{email}")
def delete_user_by_email(email: str, db: Session = Depends(get_db)):
    """Debug endpoint to delete a user by email (for testing only)"""
    from models import User
    import logging
    logger = logging.getLogger(__name__)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": f"User with email {email} not found"}
    
    user_id = user.id
    db.delete(user)
    db.commit()
    logger.info(f"Deleted user {user_id} with email {email}")
    return {"message": f"User {user_id} with email {email} deleted successfully"}

