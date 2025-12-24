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

class FeedItemResponse(BaseModel):
    id: int
    sender_email: str
    core_link: str
    received_date: datetime
    processed_date: datetime
    # Preview data fetched on-demand
    preview: Optional[Dict[str, Optional[str]]] = None
    
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

