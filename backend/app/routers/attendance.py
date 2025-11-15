"""
Attendance tracking router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import datetime, date
from ..core.database import get_db
from ..core.dependencies import get_current_active_user
from ..models.attendance import Attendance
from ..models.employee import Employee
from ..models.site import Site
from ..models.user import User
from ..schemas.attendance import (
    AttendanceCreate, AttendanceUpdate, AttendanceClockIn, AttendanceClockOut,
    Attendance as AttendanceSchema, AttendanceWithHours
)

router = APIRouter()


def calculate_hours(timestamp_in: datetime, timestamp_out: Optional[datetime]) -> Optional[float]:
    """Calculate hours worked"""
    if timestamp_out is None:
        return None
    delta = timestamp_out - timestamp_in
    return round(delta.total_seconds() / 3600, 2)


@router.post("/clock-in", response_model=AttendanceSchema, status_code=status.HTTP_201_CREATED)
async def clock_in(
    clock_in_data: AttendanceClockIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Clock in an employee at a construction site"""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == clock_in_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Verify site exists
    site = db.query(Site).filter(Site.id == clock_in_data.site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Check if employee already clocked in (no clock out)
    existing = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == clock_in_data.employee_id,
            Attendance.timestamp_out.is_(None)
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already clocked in. Please clock out first."
        )

    # Create attendance record
    attendance = Attendance(
        employee_id=clock_in_data.employee_id,
        site_id=clock_in_data.site_id,
        timestamp_in=datetime.utcnow(),
        notes=clock_in_data.notes
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


@router.put("/{attendance_id}/clock-out", response_model=AttendanceSchema)
async def clock_out(
    attendance_id: int,
    clock_out_data: AttendanceClockOut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Clock out an employee"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    if attendance.timestamp_out is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already clocked out"
        )

    # Update clock out time
    attendance.timestamp_out = datetime.utcnow()
    if clock_out_data.notes:
        attendance.notes = clock_out_data.notes

    db.commit()
    db.refresh(attendance)

    return attendance


@router.post("/", response_model=AttendanceSchema, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create an attendance record manually (with both in and out times)"""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == attendance_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Verify site exists
    site = db.query(Site).filter(Site.id == attendance_data.site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Create attendance record
    attendance = Attendance(**attendance_data.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


@router.get("/", response_model=list[AttendanceSchema])
async def list_attendances(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[int] = None,
    site_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List attendance records with optional filtering"""
    query = db.query(Attendance)

    # Filter by employee
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)

    # Filter by site
    if site_id:
        query = query.filter(Attendance.site_id == site_id)

    # Filter by date range
    if date_from:
        query = query.filter(Attendance.timestamp_in >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Attendance.timestamp_in <= datetime.combine(date_to, datetime.max.time()))

    attendances = query.order_by(Attendance.timestamp_in.desc()).offset(skip).limit(limit).all()

    return attendances


@router.get("/{attendance_id}", response_model=AttendanceSchema)
async def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attendance record by ID"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceSchema)
async def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    # Update fields
    update_data = attendance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)

    db.commit()
    db.refresh(attendance)

    return attendance


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete attendance record"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    db.delete(attendance)
    db.commit()

    return None


@router.get("/employee/{employee_id}/active", response_model=Optional[AttendanceSchema])
async def get_active_attendance(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get active attendance (not clocked out) for an employee"""
    attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == employee_id,
            Attendance.timestamp_out.is_(None)
        )
    ).first()

    return attendance
