"""Authentication utilities"""
import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

# Use direct imports (Railway runs from /backend directory)
from config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if not plain_password or not hashed_password:
            logger.warning("verify_password: Empty password or hash")
            return False
        
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Check if hash looks valid (bcrypt hashes start with $2a$, $2b$, or $2y$)
        if not hashed_password.startswith('$2'):
            logger.error(f"verify_password: Invalid hash format (doesn't start with $2): {hashed_password[:20]}...")
            return False
        
        result = bcrypt.checkpw(password_bytes, hashed_bytes)
        if not result:
            logger.warning(f"verify_password: Password mismatch (hash: {hashed_password[:20]}...)")
        return result
    except Exception as e:
        logger.error(f"verify_password error: {e}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None

