"""
Audit log model for tracking critical user actions
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class AuditLog(Base):
    """Audit log model for tracking user actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "login", "create_employee", "delete_site"
    resource_type = Column(String(50), nullable=True)  # e.g., "employee", "site", "attendance"
    resource_id = Column(Integer, nullable=True)  # ID of affected resource
    details = Column(JSON, nullable=True)  # Additional context as JSON
    ip_address = Column(String(45), nullable=True)  # Support IPv4 and IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client info
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationship
    user = relationship("User", backref="audit_logs")
