import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class PetModel(Base):
    __tablename__ = "pets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    studentId = Column(String, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    species = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)
    
    createdAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("StudentModel", back_populates="pets")