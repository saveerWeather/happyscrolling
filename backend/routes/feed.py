"""Feed routes"""
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

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Dict

# Try imports with backend prefix first, fallback to direct imports
try:
    from backend.utils.database import get_db
    from backend.models import FeedItem, User, UserEmail
    from backend.schemas import FeedItemResponse, FeedResponse
    from backend.routes.auth import get_current_user
    from backend.utils.link_preview import fetch_link_preview
except ImportError:
    from utils.database import get_db
    from models import FeedItem, User, UserEmail
    from schemas import FeedItemResponse, FeedResponse
    from routes.auth import get_current_user
    from utils.link_preview import fetch_link_preview

router = APIRouter(prefix="/api/feed", tags=["feed"])

@router.get("", response_model=FeedResponse)
def get_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's feed items"""
    # Get all email addresses linked to this user
    linked_emails = db.query(UserEmail.email_address).filter(
        UserEmail.user_id == current_user.id
    ).all()
    linked_email_list = [email[0] for email in linked_emails]
    
    # Also include user's own email
    linked_email_list.append(current_user.email)
    
    if not linked_email_list:
        return FeedResponse(items=[], total=0, page=page, limit=limit, has_more=False)
    
    # Build query
    query = db.query(FeedItem).filter(
        FeedItem.sender_email.in_(linked_email_list)
    )
    
    # Filter by specific email if provided
    if email:
        query = query.filter(FeedItem.sender_email == email)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    items = query.order_by(FeedItem.received_date.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Fetch previews on-demand for each item
    items_with_previews = []
    for item in items:
        preview_data = fetch_link_preview(item.core_link)
        item_dict = FeedItemResponse(
            id=item.id,
            sender_email=item.sender_email,
            core_link=item.core_link,
            received_date=item.received_date,
            processed_date=item.processed_date,
            preview=preview_data
        )
        items_with_previews.append(item_dict)
    
    has_more = (page * limit) < total
    
    return FeedResponse(
        items=items_with_previews,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more
    )

