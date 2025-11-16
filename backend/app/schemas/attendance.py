"""
Attendance schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class AttendanceBase(BaseModel):
    """Base attendance schema"""
    employee_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)


class AttendanceCreate(AttendanceBase):
    """Schema for creating an attendance record"""
    timestamp_in: datetime
    timestamp_out: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator('notes')
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        if v is not None and v.strip() == '':
            return None
        return v


class AttendanceClockIn(BaseModel):
    """Schema for clock-in"""
    employee_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    notes: Optional[str] = None

    @field_validator('notes')
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        if v is not None and v.strip() == '':
            return None
        return v


class AttendanceClockOut(BaseModel):
    """Schema for clock-out"""
    notes: Optional[str] = None

    @field_validator('notes')
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        if v is not None and v.strip() == '':
            return None
        return v


class AttendanceUpdate(BaseModel):
    """Schema for updating an attendance record"""
    timestamp_in: Optional[datetime] = None
    timestamp_out: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator('notes')
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        """Convert empty strings to None"""
        if v is not None and v.strip() == '':
            return None
        return v


class EmployeeInfo(BaseModel):
    """Embedded employee info"""
    id: int
    name: str
    surname: str
    badge_code: str
    role: str

    class Config:
        from_attributes = True


class SiteInfo(BaseModel):
    """Embedded site info"""
    id: int
    name: str
    address: str
    status: str

    class Config:
        from_attributes = True


class Attendance(AttendanceBase):
    """Schema for attendance response"""
    id: int
    timestamp_in: datetime
    timestamp_out: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    employee: Optional[EmployeeInfo] = None
    site: Optional[SiteInfo] = None

    class Config:
        from_attributes = True


class AttendanceWithHours(Attendance):
    """Attendance with calculated hours"""
    hours_worked: Optional[float] = None
