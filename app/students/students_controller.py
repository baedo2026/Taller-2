from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)
from app.students.students_service import students_service

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("", response_model=StudentList)
def find_all(db: Session = Depends(get_db)) -> StudentList:
    return students_service.find_all(db)


@router.get("/{student_id}", response_model=Student)
def find_by_id(student_id: int, db: Session = Depends(get_db)) -> Student:
    return students_service.find_by_id(db, student_id)


@router.post("", response_model=Student, status_code=status.HTTP_201_CREATED)
def create(data: CreateStudentDto, db: Session = Depends(get_db)) -> Student:
    return students_service.create(db, data)


@router.patch("/{student_id}", response_model=Student)
def update(
    student_id: int, data: UpdateStudentDto, db: Session = Depends(get_db)
) -> Student:
    return students_service.update(db, student_id, data)


@router.delete("/{student_id}", response_model=Student)
def delete(student_id: int, db: Session = Depends(get_db)) -> Student:
    return students_service.delete(db, student_id)
