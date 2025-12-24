"""Database models"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.utils.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    email_verified = Column(Boolean, default=False)
    
    # Relationships
    linked_emails = relationship("UserEmail", back_populates="user", cascade="all, delete-orphan")
    feed_items = relationship("FeedItem", back_populates="user")

class UserEmail(Base):
    __tablename__ = "user_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email_address = Column(String, nullable=False, index=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="linked_emails")

class FeedItem(Base):
    __tablename__ = "feed_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_email = Column(String, nullable=False, index=True)
    core_link = Column(String, nullable=False)
    received_date = Column(DateTime, nullable=False)
    processed_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # User association (nullable for backward compatibility)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="feed_items")

