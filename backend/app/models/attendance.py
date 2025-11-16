"""
Attendance tracking model
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index, Text, func as sql_func
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Attendance(Base):
    """Attendance tracking model"""
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_in = Column(DateTime(timezone=True), nullable=False, index=True)
    timestamp_out = Column(DateTime(timezone=True), nullable=True, index=True)
    notes = Column(Text, nullable=True)  # Optional notes about the attendance
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="attendances")
    site = relationship("Site", back_populates="attendances")

    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_attendances_employee_date', 'employee_id', 'timestamp_in'),
        Index('ix_attendances_site_date', 'site_id', 'timestamp_in'),
        Index('ix_attendances_date_range', 'timestamp_in', 'timestamp_out'),
    )
