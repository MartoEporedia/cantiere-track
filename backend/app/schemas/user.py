"""
User schemas for authentication
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole
import re


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength based on security requirements"""
        from ..core.config import settings

        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f'Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long')

        if settings.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if settings.REQUIRE_DIGIT and not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')

        if settings.REQUIRE_SPECIAL_CHAR and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')

        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')

        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if password is being updated"""
        if v is None:
            return v
        # Use same validation as UserCreate
        return UserCreate.validate_password_strength(v)


class User(UserBase):
    """Schema for user response"""
    id: int
    role: UserRole
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
