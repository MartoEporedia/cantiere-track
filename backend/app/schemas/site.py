"""
Construction site schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SiteBase(BaseModel):
    """Base site schema"""
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None


class SiteCreate(SiteBase):
    """Schema for creating a site"""
    status: str = Field(default="open", pattern="^(open|closed)$")


class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, pattern="^(open|closed)$")
    description: Optional[str] = None


class Site(SiteBase):
    """Schema for site response"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SiteList(BaseModel):
    """Schema for site list response"""
    total: int
    sites: list[Site]
