"""
Construction site model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Site(Base):
    """Construction site model"""
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100))
    postal_code = Column(String(20))
    status = Column(String(20), default="open", nullable=False, index=True)  # open, closed
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    attendances = relationship("Attendance", back_populates="site", cascade="all, delete-orphan")
