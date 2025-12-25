"""Authentication routes"""
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

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

# Use direct imports (Railway runs from /backend directory)
from utils.database import get_db
from models import User
from schemas import UserRegister, UserLogin, UserResponse
from utils.auth import verify_password, get_password_hash

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from session"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Register a new user"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing email/username: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Set user ID in session (auto-login after registration)
        request.session["user_id"] = new_user.id
        logger.info(f"User {new_user.id} registered successfully")
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login and create session"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Login attempt for email: {credentials.email}")
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            logger.warning(f"Login attempt with non-existent email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        logger.info(f"User found: {user.id}, verifying password...")
        password_valid = verify_password(credentials.password, user.password_hash)
        logger.info(f"Password verification result: {password_valid}")
        
        if not password_valid:
            logger.warning(f"Login attempt with incorrect password for: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Set user ID in session
        request.session["user_id"] = user.id
        logger.info(f"User {user.id} logged in successfully")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
def logout(request: Request):
    """Logout and clear session"""
    request.session.clear()
    return {"message": "Logged out successfully"}

