"""Settings routes for email management"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.utils.database import get_db
from backend.models import User, UserEmail, FeedItem
from backend.schemas import UserEmailResponse, AddEmailRequest
from backend.routes.auth import get_current_user

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/emails", response_model=list[UserEmailResponse])
def get_linked_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all email addresses linked to user"""
    emails = db.query(UserEmail).filter(UserEmail.user_id == current_user.id).all()
    return emails

@router.post("/emails", response_model=UserEmailResponse, status_code=status.HTTP_201_CREATED)
def add_linked_email(
    email_data: AddEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an email address to user's linked emails"""
    # Check if already linked
    existing = db.query(UserEmail).filter(
        UserEmail.user_id == current_user.id,
        UserEmail.email_address == email_data.email_address
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already linked"
        )
    
    new_email = UserEmail(
        user_id=current_user.id,
        email_address=email_data.email_address,
        verified=False  # Could add email verification later
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    
    # Auto-link existing feed items from this email
    db.query(FeedItem).filter(
        FeedItem.sender_email == email_data.email_address,
        FeedItem.user_id.is_(None)
    ).update({"user_id": current_user.id})
    db.commit()
    
    return new_email

@router.delete("/emails/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_linked_email(
    email_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a linked email address"""
    email = db.query(UserEmail).filter(
        UserEmail.id == email_id,
        UserEmail.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    db.delete(email)
    db.commit()
    return None

