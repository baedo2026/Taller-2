import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    
    createdAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    pets = relationship("PetModel", back_populates="student", cascade="all, delete-orphan")