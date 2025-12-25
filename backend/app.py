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
    logger.info("Database utilities imported successfully")
    # Log database configuration (after logging is configured)
    logger.info(f"DATABASE_URL is set: {bool(DATABASE_URL)}")
    logger.info(f"DATABASE_URL starts with: {DATABASE_URL[:20] if DATABASE_URL else 'None'}...")
    logger.info(f"USE_POSTGRES: {USE_POSTGRES}")
    is_postgres = USE_POSTGRES and DATABASE_URL and not DATABASE_URL.startswith('sqlite')
    logger.info(f"Will use PostgreSQL: {is_postgres}")
    if is_postgres:
        # Hide password in log
        safe_url = DATABASE_URL
        if '@' in DATABASE_URL:
            parts = DATABASE_URL.split('@')
            if len(parts) == 2:
                safe_url = parts[0].split('//')[0] + '//***@' + parts[1]
        logger.info(f"PostgreSQL connection string: {safe_url}")
    else:
        logger.info("Using SQLite database")
except Exception as e:
    logger.error(f"Failed to import database utilities: {e}", exc_info=True)
    raise

try:
    from routes import auth, feed, settings as settings_routes
    logger.info("Routes imported successfully")
except Exception as e:
    logger.error(f"Failed to import routes: {e}", exc_info=True)
    raise

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

try:
    app = FastAPI(
        title="Happy Scrolling API",
        description="Email feed aggregator API",
        version="1.0.0"
    )
    logger.info("FastAPI app created successfully")
except Exception as e:
    logger.error(f"Failed to create FastAPI app: {e}", exc_info=True)
    raise

# CORS middleware (MUST be before Session middleware for preflight requests)
# Log what we're actually using
logger.info(f"Setting CORS with origins: {settings.cors_origins}")
# CORS configuration - use explicit lists for compatibility
# FastAPI's CORSMiddleware may not support ["*"] in all versions
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

# Session middleware (after CORS)
# Use "none" for cross-origin support (required for Railway where frontend/backend are different domains)
# This allows cookies to be sent cross-origin when using HTTPS
# Note: same_site="none" requires Secure cookies (HTTPS), which Railway provides
try:
    # For same_site="none", cookies MUST be Secure (HTTPS only)
    # Railway provides HTTPS, so we can use secure cookies
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.jwt_secret,  # Reuse JWT secret for session signing
        max_age=60 * 60 * 24 * 7,  # 7 days
        same_site="none",
        # Note: Starlette's SessionMiddleware doesn't have a 'secure' parameter
        # It should automatically set Secure=True when same_site="none" on HTTPS
    )
    logger.info("SessionMiddleware configured successfully with same_site='none'")
except Exception as e:
    logger.error(f"Failed to configure SessionMiddleware: {e}", exc_info=True)
    # Fallback to lax for local development
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.jwt_secret,
        max_age=60 * 60 * 24 * 7,
        same_site="lax",
    )
    logger.warning("Using same_site='lax' as fallback")

# Middleware to ensure session cookies have Secure flag when on HTTPS
@app.middleware("http")
async def secure_session_cookies(request: Request, call_next):
    """Ensure session cookies have Secure flag for HTTPS (required for SameSite=None)"""
    response = await call_next(request)
    
    # Check if we're on HTTPS (Railway provides this via X-Forwarded-Proto)
    is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    
    if is_https:
        # Get all Set-Cookie headers
        set_cookie_headers = response.headers.getlist("set-cookie")
        
        # Find and fix session cookie if it exists
        modified = False
        new_cookies = []
        for cookie_header in set_cookie_headers:
            if cookie_header.startswith("session="):
                # Check if Secure flag is missing
                if "; Secure" not in cookie_header and " Secure" not in cookie_header:
                    # Add Secure flag before samesite or at the end
                    if "; samesite=" in cookie_header.lower():
                        cookie_header = cookie_header.replace("; samesite=", "; Secure; samesite=", 1)
                        cookie_header = cookie_header.replace("; SameSite=", "; Secure; SameSite=", 1)
                    else:
                        cookie_header = cookie_header + "; Secure"
                    modified = True
                    logger.info("Added Secure flag to session cookie")
            new_cookies.append(cookie_header)
        
        # If we modified cookies, update all Set-Cookie headers
        if modified:
            # Remove all existing Set-Cookie headers
            while "set-cookie" in response.headers:
                response.headers.pop("set-cookie")
            # Add back all cookies (with Secure added to session)
            for cookie in new_cookies:
                response.headers.append("set-cookie", cookie)
    
    return response

# Add request logging middleware (after CORS and session security)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    origin = request.headers.get("origin", "no origin")
    logger.info(f"{request.method} {request.url.path} from origin: {origin}")
    
    # Log cookies in request
    cookies = list(request.cookies.keys())
    logger.info(f"{request.method} {request.url.path} - Request cookies: {cookies}")
    
    # Log preflight request details
    if request.method == "OPTIONS":
        access_control_method = request.headers.get("access-control-request-method", "not set")
        access_control_headers = request.headers.get("access-control-request-headers", "not set")
        logger.info(f"OPTIONS preflight - method: {access_control_method}, headers: {access_control_headers}")
    
    try:
        response = await call_next(request)
        # Log CORS headers in response
        cors_origin = response.headers.get("access-control-allow-origin", "not set")
        cors_methods = response.headers.get("access-control-allow-methods", "not set")
        cors_headers = response.headers.get("access-control-allow-headers", "not set")
        cors_credentials = response.headers.get("access-control-allow-credentials", "not set")
        
        # Log Set-Cookie headers in response
        set_cookie_headers = response.headers.getlist("set-cookie")
        logger.info(f"{request.method} {request.url.path} - {response.status_code} | CORS origin: {cors_origin}, credentials: {cors_credentials}, Set-Cookie headers: {len(set_cookie_headers)}")
        
        # For OPTIONS preflight, credentials header is critical
        if request.method == "OPTIONS":
            if cors_credentials != "true":
                logger.warning(f"⚠️ OPTIONS preflight missing Access-Control-Allow-Credentials: true! Got: {cors_credentials}")
            else:
                logger.info("✓ OPTIONS preflight includes Access-Control-Allow-Credentials: true")
        
        if set_cookie_headers:
            for cookie in set_cookie_headers:
                # Log first 150 chars of cookie (to see Secure, SameSite, etc)
                logger.info(f"  Cookie: {cookie[:150]}...")
        
        return response
    except Exception as e:
        logger.error(f"Error processing {request.method} {request.url.path}: {e}", exc_info=True)
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
    """Log when the application is fully started"""
    logger.info("=" * 50)
    logger.info("FastAPI application is ready to accept requests")
    logger.info("=" * 50)

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

