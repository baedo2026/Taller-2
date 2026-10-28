from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.students.students_schemas import Student, CreateStudentDto, UpdateStudentDto
from app.students.students_service import StudentsService

router = APIRouter(prefix="/students", tags=["Students"])
service = StudentsService()


@router.get("", response_model=list[Student])
def get_all_students(db: Session = Depends(get_db)):
    return service.find_all(db)


@router.get("/{student_id}", response_model=Student)
def get_student_by_id(student_id: str, db: Session = Depends(get_db)):
    return service.find_by_id(db, student_id)


@router.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(dto: CreateStudentDto, db: Session = Depends(get_db)):
    return service.create(db, dto)


@router.patch("/{student_id}", response_model=Student)
def update_student(student_id: str, dto: UpdateStudentDto, db: Session = Depends(get_db)):
    return service.update(db, student_id, dto)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: str, db: Session = Depends(get_db)):
    service.delete(db, student_id)