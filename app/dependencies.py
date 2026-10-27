from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.pets.pets_repository import PetsRepository
from app.pets.pets_service import PetsService
from app.students.students_repository import StudentsRepository
from app.students.students_service import StudentsService


def get_students_service(session: Session = Depends(get_db)) -> StudentsService:
    students = StudentsRepository(session)
    pets = PetsRepository(session)
    return StudentsService(students, pets)


def get_pets_service(session: Session = Depends(get_db)) -> PetsService:
    students_repository = StudentsRepository(session)
    pets_repository = PetsRepository(session)
    students_service = StudentsService(students_repository, pets_repository)
    return PetsService(pets_repository, students_service)
