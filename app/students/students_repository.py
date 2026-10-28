from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import StudentORM


class StudentsRepository:
    def find_all(self, db: Session) -> list[StudentORM]:
        return list(db.scalars(select(StudentORM)).all())

    def find_by_id(self, db: Session, student_id: str) -> StudentORM | None:
        return db.scalar(select(StudentORM).where(StudentORM.id == student_id))

    def find_by_email(self, db: Session, email: str) -> StudentORM | None:
        return db.scalar(select(StudentORM).where(StudentORM.email == email))

    def find_by_username(self, db: Session, username: str) -> StudentORM | None:
        return db.scalar(select(StudentORM).where(StudentORM.username == username))

    def save(self, db: Session, student: StudentORM) -> StudentORM:
        db.add(student)
        return student

    def delete(self, db: Session, student_id: str) -> None:
        student = self.find_by_id(db, student_id)
        if student:
            db.delete(student)