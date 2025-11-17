"""
Audit logging utilities
"""
from sqlalchemy.orm import Session
from fastapi import Request
from typing import Optional, Dict, Any
from ..models.audit_log import AuditLog
from ..models.user import User


def log_action(
    db: Session,
    action: str,
    user: Optional[User] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """
    Log a user action to the audit log

    Args:
        db: Database session
        action: Action name (e.g., "login", "create_employee", "delete_site")
        user: User performing the action (if authenticated)
        resource_type: Type of resource affected (e.g., "employee", "site")
        resource_id: ID of the affected resource
        details: Additional context as dictionary
        request: FastAPI Request object (to extract IP and user agent)

    Returns:
        Created AuditLog instance
    """
    ip_address = None
    user_agent = None

    if request:
        # Extract IP address (handle proxy headers)
        ip_address = request.client.host if request.client else None
        if "x-forwarded-for" in request.headers:
            ip_address = request.headers["x-forwarded-for"].split(",")[0].strip()

        # Extract user agent
        user_agent = request.headers.get("user-agent")

    audit_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)

    return audit_entry


# Common audit actions
class AuditAction:
    """Predefined audit action names"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"

    # Employee management
    CREATE_EMPLOYEE = "create_employee"
    UPDATE_EMPLOYEE = "update_employee"
    DELETE_EMPLOYEE = "delete_employee"

    # Site management
    CREATE_SITE = "create_site"
    UPDATE_SITE = "update_site"
    DELETE_SITE = "delete_site"

    # Attendance
    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"
    ADD_MANUAL_HOURS = "add_manual_hours"
    UPDATE_ATTENDANCE = "update_attendance"
    DELETE_ATTENDANCE = "delete_attendance"

    # Reports
    EXPORT_REPORT = "export_report"
    VIEW_REPORT = "view_report"
