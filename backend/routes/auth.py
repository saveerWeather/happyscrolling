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
from datetime import datetime, timedelta
import secrets
import os

# Use direct imports (Railway runs from /backend directory)
from utils.database import get_db
from models import User, EmailVerificationToken
from schemas import UserRegister, UserLogin, UserResponse
from utils.auth import verify_password, get_password_hash
from utils.email import email_service

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
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            email_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate verification token
        token = secrets.token_urlsafe(48)
        expires = datetime.utcnow() + timedelta(hours=24)
        verification = EmailVerificationToken(
            user_id=new_user.id,
            token=token,
            email=new_user.email,
            expires_at=expires
        )
        db.add(verification)
        db.commit()

        # Send verification email
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        email_service.send_verification_email(new_user.email, token, base_url)

        # Set user ID in session
        request.session["user_id"] = new_user.id

        return new_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login and create session"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    password_valid = verify_password(credentials.password, user.password_hash)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Set user ID in session
    request.session["user_id"] = user.id
    
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
def logout(request: Request):
    """Logout and clear session"""
    request.session.clear()
    return {"message": "Logged out successfully"}

