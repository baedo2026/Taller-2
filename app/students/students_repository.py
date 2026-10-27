from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import StudentORM


class StudentsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_all(self) -> list[StudentORM]:
        return list(self.session.scalars(select(StudentORM)).all())

    def find_by_id(self, student_id: str) -> StudentORM | None:
        return self.session.get(StudentORM, student_id)

    def find_by_email(self, email: str) -> StudentORM | None:
        return self.session.scalar(select(StudentORM).where(StudentORM.email == email))

    def find_by_username(self, username: str) -> StudentORM | None:
        return self.session.scalar(select(StudentORM).where(StudentORM.username == username))

    def save(self, student: StudentORM) -> StudentORM:
        self.session.add(student)
        self.session.flush()
        return student

    def delete(self, student: StudentORM) -> None:
        self.session.delete(student)
