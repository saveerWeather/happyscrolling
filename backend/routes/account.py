"""Account management routes"""
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

from utils.database import get_db
from models import User, EmailVerificationToken, PasswordResetToken
from schemas import (
    UpdateProfileRequest, ChangePasswordRequest,
    RequestPasswordResetRequest, ResetPasswordRequest,
    VerifyEmailRequest, ResendVerificationRequest,
    DeleteAccountRequest, UserResponse
)
from utils.auth import verify_password, get_password_hash
from utils.email import email_service
from routes.auth import get_current_user

router = APIRouter(prefix="/api/account", tags=["account"])

def generate_token() -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(48)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    # Check if username is taken (if changing)
    if data.username and data.username != current_user.username:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = data.username

    # Check if email is taken (if changing)
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = data.email
        current_user.email_verified = False  # Need to re-verify

        # Send verification email
        token = generate_token()
        expires = datetime.utcnow() + timedelta(hours=24)
        verification = EmailVerificationToken(
            user_id=current_user.id,
            token=token,
            email=data.email,
            expires_at=expires
        )
        db.add(verification)
        db.commit()

        base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        email_service.send_verification_email(data.email, token, base_url)

    if data.display_name is not None:
        current_user.display_name = data.display_name

    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change password"""
    # Verify current password
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    # Update password
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}

@router.post("/request-password-reset")
def request_password_reset(data: RequestPasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset email"""
    user = db.query(User).filter(User.email == data.email).first()

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If that email exists, a reset link has been sent"}

    # Generate token
    token = generate_token()
    expires = datetime.utcnow() + timedelta(hours=1)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires
    )
    db.add(reset_token)
    db.commit()

    # Send email
    base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    email_service.send_password_reset_email(data.email, token, base_url)

    return {"message": "If that email exists, a reset link has been sent"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token"""
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.used == False
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Validate new password
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    # Update password
    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.password_hash = get_password_hash(data.new_password)
    token_record.used = True
    db.commit()

    return {"message": "Password reset successfully"}

@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify email with token"""
    token_record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == data.token,
        EmailVerificationToken.used == False
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )

    # Mark email as verified
    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.email_verified = True
    token_record.used = True
    db.commit()

    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
def resend_verification(
    data: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """Resend verification email"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        return {"message": "If that email exists, a verification link has been sent"}

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Generate new token
    token = generate_token()
    expires = datetime.utcnow() + timedelta(hours=24)
    verification = EmailVerificationToken(
        user_id=user.id,
        token=token,
        email=user.email,
        expires_at=expires
    )
    db.add(verification)
    db.commit()

    base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    email_service.send_verification_email(user.email, token, base_url)

    return {"message": "Verification email sent"}

@router.delete("/delete")
def delete_account(
    data: DeleteAccountRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user account (requires password confirmation)"""
    # Verify password
    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect"
        )

    # Delete user (cascade will delete related records)
    db.delete(current_user)
    db.commit()

    # Clear session
    request.session.clear()

    return {"message": "Account deleted successfully"}
