from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import StudentORM
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import CreateStudentDto, UpdateStudentDto


class StudentsService:
    def __init__(self):
        self.repository = StudentsRepository()

    def find_all(self, db: Session) -> list[StudentORM]:
        return self.repository.find_all(db)

    def find_by_id(self, db: Session, student_id: str) -> StudentORM:
        student = self.repository.find_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado"
            )
        return student

    def create(self, db: Session, dto: CreateStudentDto) -> StudentORM:
        if self.repository.find_by_email(db, dto.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        try:
            student = StudentORM(**dto.model_dump())
            created_student = self.repository.save(db, student)
            db.commit()
            db.refresh(created_student)
            return created_student
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear el estudiante: {str(e)}"
            )

    def update(self, db: Session, student_id: str, dto: UpdateStudentDto) -> StudentORM:
        student = self.find_by_id(db, student_id)
        update_data = dto.model_dump(exclude_unset=True)

        try:
            for key, value in update_data.items():
                setattr(student, key, value)
            
            db.commit()
            db.refresh(student)
            return student
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar el estudiante: {str(e)}"
            )

    def delete(self, db: Session, student_id: str) -> None:
        student = self.find_by_id(db, student_id)
        try:
            self.repository.delete(db, student.id)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar el estudiante: {str(e)}"
            )