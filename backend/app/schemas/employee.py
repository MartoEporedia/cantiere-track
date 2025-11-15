"""
Employee schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    """Base employee schema"""
    name: str = Field(..., min_length=1, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)
    badge_code: str = Field(..., min_length=1, max_length=50)
    role: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)


class EmployeeCreate(EmployeeBase):
    """Schema for creating an employee"""
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    surname: Optional[str] = Field(None, min_length=1, max_length=100)
    badge_code: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)


class Employee(EmployeeBase):
    """Schema for employee response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    """Schema for employee list response"""
    total: int
    employees: list[Employee]
