"""
Employee model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Employee(Base):
    """Employee model"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    badge_code = Column(String(50), unique=True, index=True, nullable=False)
    role = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    phone = Column(String(20))
    email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    attendances = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
