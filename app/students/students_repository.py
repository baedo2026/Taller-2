from sqlalchemy.orm import Session

from app.models import StudentModel


class StudentsRepository:
    def find_all(self, db: Session) -> list[StudentModel]:
        return db.query(StudentModel).all()

    def find_by_id(self, db: Session, student_id: int) -> StudentModel | None:
        return db.query(StudentModel).filter(StudentModel.id == student_id).first()

    def find_by_email(self, db: Session, email: str) -> StudentModel | None:
        return db.query(StudentModel).filter(StudentModel.email == email).first()

    def find_by_username(self, db: Session, username: str) -> StudentModel | None:
        return db.query(StudentModel).filter(StudentModel.username == username).first()

    def save(self, db: Session, student: StudentModel) -> StudentModel:
        db.add(student)
        return student

    def delete(self, db: Session, student: StudentModel) -> None:
        db.delete(student)


students_repository = StudentsRepository()
