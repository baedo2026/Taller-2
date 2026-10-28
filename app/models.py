from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.shared.datetimes import utc_now


class StudentModel(Base):
    __tablename__ = "students"
    __table_args__ = (UniqueConstraint("username", name="uq_students_username"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username = Column(String(30), nullable=False)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    createdAt = Column(
        "created_at", DateTime(timezone=True), default=utc_now, nullable=False
    )
    updatedAt = Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    pets = relationship(
        "PetModel", back_populates="owner", cascade="all, delete-orphan"
    )


class PetModel(Base):
    __tablename__ = "pets"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_pets_owner_id_name"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    species = Column(String(50), nullable=False)
    age = Column(Integer, nullable=True)
    owner_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    createdAt = Column(
        "created_at", DateTime(timezone=True), default=utc_now, nullable=False
    )
    updatedAt = Column(
        "updated_at",
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    owner = relationship("StudentModel", back_populates="pets")

    @property
    def studentId(self) -> str:
        return str(self.owner_id)
