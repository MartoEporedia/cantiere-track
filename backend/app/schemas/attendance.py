"""
Attendance schemas
"""
from pydantic import BaseModel, Field
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


class AttendanceClockIn(BaseModel):
    """Schema for clock-in"""
    employee_id: int = Field(..., gt=0)
    site_id: int = Field(..., gt=0)
    notes: Optional[str] = None


class AttendanceClockOut(BaseModel):
    """Schema for clock-out"""
    notes: Optional[str] = None


class AttendanceUpdate(BaseModel):
    """Schema for updating an attendance record"""
    timestamp_in: Optional[datetime] = None
    timestamp_out: Optional[datetime] = None
    notes: Optional[str] = None


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
