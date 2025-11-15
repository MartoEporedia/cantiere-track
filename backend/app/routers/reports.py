"""
Reporting router for attendance analysis
"""
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, date
from io import StringIO
import csv
from ..core.database import get_db
from ..core.dependencies import get_current_active_user
from ..models.attendance import Attendance
from ..models.employee import Employee
from ..models.site import Site
from ..models.user import User

router = APIRouter()


def calculate_hours(timestamp_in: datetime, timestamp_out: Optional[datetime]) -> float:
    """Calculate hours worked"""
    if timestamp_out is None:
        # If still clocked in, calculate up to now
        timestamp_out = datetime.utcnow()
    delta = timestamp_out - timestamp_in
    return round(delta.total_seconds() / 3600, 2)


@router.get("/employee/{employee_id}")
async def employee_report(
    employee_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attendance report for a specific employee"""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return {"error": "Employee not found"}

    # Build query
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)

    # Filter by date range
    if date_from:
        query = query.filter(Attendance.timestamp_in >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Attendance.timestamp_in <= datetime.combine(date_to, datetime.max.time()))

    attendances = query.order_by(Attendance.timestamp_in.desc()).all()

    # Calculate totals
    total_hours = 0
    sites_visited = set()
    attendance_list = []

    for att in attendances:
        hours = calculate_hours(att.timestamp_in, att.timestamp_out)
        if att.timestamp_out:  # Only count completed attendances
            total_hours += hours

        sites_visited.add(att.site_id)

        # Get site info
        site = db.query(Site).filter(Site.id == att.site_id).first()

        attendance_list.append({
            "id": att.id,
            "site_name": site.name if site else "Unknown",
            "site_address": site.address if site else "Unknown",
            "timestamp_in": att.timestamp_in.isoformat(),
            "timestamp_out": att.timestamp_out.isoformat() if att.timestamp_out else None,
            "hours_worked": hours if att.timestamp_out else None,
            "status": "completed" if att.timestamp_out else "in_progress"
        })

    return {
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "surname": employee.surname,
            "badge_code": employee.badge_code,
            "role": employee.role
        },
        "summary": {
            "total_hours": round(total_hours, 2),
            "total_attendances": len(attendances),
            "sites_visited": len(sites_visited)
        },
        "attendances": attendance_list
    }


@router.get("/site/{site_id}")
async def site_report(
    site_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attendance report for a specific construction site"""
    # Verify site exists
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        return {"error": "Site not found"}

    # Build query
    query = db.query(Attendance).filter(Attendance.site_id == site_id)

    # Filter by date range
    if date_from:
        query = query.filter(Attendance.timestamp_in >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Attendance.timestamp_in <= datetime.combine(date_to, datetime.max.time()))

    attendances = query.order_by(Attendance.timestamp_in.desc()).all()

    # Calculate totals
    total_hours = 0
    employees_present = set()
    attendance_list = []

    for att in attendances:
        hours = calculate_hours(att.timestamp_in, att.timestamp_out)
        if att.timestamp_out:  # Only count completed attendances
            total_hours += hours

        employees_present.add(att.employee_id)

        # Get employee info
        employee = db.query(Employee).filter(Employee.id == att.employee_id).first()

        attendance_list.append({
            "id": att.id,
            "employee_name": f"{employee.name} {employee.surname}" if employee else "Unknown",
            "employee_badge": employee.badge_code if employee else "Unknown",
            "employee_role": employee.role if employee else "Unknown",
            "timestamp_in": att.timestamp_in.isoformat(),
            "timestamp_out": att.timestamp_out.isoformat() if att.timestamp_out else None,
            "hours_worked": hours if att.timestamp_out else None,
            "status": "completed" if att.timestamp_out else "in_progress"
        })

    return {
        "site": {
            "id": site.id,
            "name": site.name,
            "address": site.address,
            "status": site.status
        },
        "summary": {
            "total_hours": round(total_hours, 2),
            "total_attendances": len(attendances),
            "unique_employees": len(employees_present)
        },
        "attendances": attendance_list
    }


@router.get("/employee/{employee_id}/csv")
async def employee_report_csv(
    employee_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export employee attendance report as CSV"""
    # Get employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return Response(content="Employee not found", status_code=404)

    # Build query
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)

    if date_from:
        query = query.filter(Attendance.timestamp_in >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Attendance.timestamp_in <= datetime.combine(date_to, datetime.max.time()))

    attendances = query.order_by(Attendance.timestamp_in.desc()).all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Employee Name",
        "Badge Code",
        "Role",
        "Site Name",
        "Site Address",
        "Clock In",
        "Clock Out",
        "Hours Worked",
        "Status"
    ])

    # Write data
    for att in attendances:
        site = db.query(Site).filter(Site.id == att.site_id).first()
        hours = calculate_hours(att.timestamp_in, att.timestamp_out) if att.timestamp_out else ""

        writer.writerow([
            f"{employee.name} {employee.surname}",
            employee.badge_code,
            employee.role,
            site.name if site else "Unknown",
            site.address if site else "Unknown",
            att.timestamp_in.strftime("%Y-%m-%d %H:%M:%S"),
            att.timestamp_out.strftime("%Y-%m-%d %H:%M:%S") if att.timestamp_out else "",
            hours,
            "Completed" if att.timestamp_out else "In Progress"
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=employee_{employee_id}_attendance.csv"
        }
    )


@router.get("/site/{site_id}/csv")
async def site_report_csv(
    site_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export site attendance report as CSV"""
    # Get site
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        return Response(content="Site not found", status_code=404)

    # Build query
    query = db.query(Attendance).filter(Attendance.site_id == site_id)

    if date_from:
        query = query.filter(Attendance.timestamp_in >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(Attendance.timestamp_in <= datetime.combine(date_to, datetime.max.time()))

    attendances = query.order_by(Attendance.timestamp_in.desc()).all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Site Name",
        "Site Address",
        "Employee Name",
        "Badge Code",
        "Role",
        "Clock In",
        "Clock Out",
        "Hours Worked",
        "Status"
    ])

    # Write data
    for att in attendances:
        employee = db.query(Employee).filter(Employee.id == att.employee_id).first()
        hours = calculate_hours(att.timestamp_in, att.timestamp_out) if att.timestamp_out else ""

        writer.writerow([
            site.name,
            site.address,
            f"{employee.name} {employee.surname}" if employee else "Unknown",
            employee.badge_code if employee else "Unknown",
            employee.role if employee else "Unknown",
            att.timestamp_in.strftime("%Y-%m-%d %H:%M:%S"),
            att.timestamp_out.strftime("%Y-%m-%d %H:%M:%S") if att.timestamp_out else "",
            hours,
            "Completed" if att.timestamp_out else "In Progress"
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=site_{site_id}_attendance.csv"
        }
    )
