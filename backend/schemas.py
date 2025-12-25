"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# Auth schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Feed schemas
class LinkPreview(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    site_name: Optional[str] = None
    text_content: Optional[str] = None  # Full text content (e.g., tweet text)
    images: Optional[List[str]] = None  # Multiple images
    author: Optional[str] = None  # Author/username
    platform: Optional[str] = None  # twitter, reddit, article, youtube, etc.
    subreddit: Optional[str] = None  # For Reddit posts
    published_time: Optional[str] = None  # For articles
    embed_html: Optional[str] = None  # HTML for embeddable content (YouTube, Twitter, etc.)
    embeddable: Optional[bool] = False  # Whether this content should be embedded

class FeedItemResponse(BaseModel):
    id: int
    sender_email: str
    core_link: str
    received_date: datetime
    processed_date: datetime
    notes: Optional[str] = None
    # Preview data fetched on-demand
    preview: Optional[LinkPreview] = None

    class Config:
        from_attributes = True

class FeedResponse(BaseModel):
    items: List[FeedItemResponse]
    total: int
    page: int
    limit: int
    has_more: bool

# Settings schemas
class UserEmailResponse(BaseModel):
    id: int
    email_address: str
    verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AddEmailRequest(BaseModel):
    email_address: EmailStr

class UpdateNotesRequest(BaseModel):
    notes: str

# Account management schemas
class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class RequestPasswordResetRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class DeleteAccountRequest(BaseModel):
    password: str

