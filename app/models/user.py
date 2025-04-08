# app/user.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from pydantic import EmailStr


class UserBase(SQLModel):
    """Shared fields between DB and input/output models."""
    email: EmailStr


class UserCreate(UserBase):
    """Used for user registration input validation."""
    password: str  # Plain text password from user


class User(UserBase, table=True):
    """Database model for storing users."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
