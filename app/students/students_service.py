from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import PetModel, StudentModel
from app.shared.exceptions import conflict
from app.shared.types import FieldErrors
from app.students.students_repository import StudentsRepository, students_repository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)


class StudentsService:
    def __init__(self, repository: StudentsRepository) -> None:
        self.repository = repository

    def find_all(self, db: Session) -> StudentList:
        students = sorted(
            self.repository.find_all(db),
            key=lambda student: student.createdAt,
            reverse=True,
        )
        return StudentList(
            total=len(students),
            items=[Student.model_validate(student) for student in students],
        )

    def find_by_id(self, db: Session, student_id: int) -> Student:
        student = self.repository.find_by_id(db, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )
        return Student.model_validate(student)

    def create(self, db: Session, data: CreateStudentDto) -> Student:
        self.assert_no_conflicts(db, data)
        student = StudentModel(
            name=data.name,
            username=data.username,
            email=str(data.email),
            age=data.age,
        )
        pet_names: set[str] = set()
        pets: list[PetModel] = []

        for pet_data in data.pets:
            if pet_data.name in pet_names:
                raise conflict(
                    {"name": {"message": "Ya tienes una mascota con ese nombre"}}
                )
            pet_names.add(pet_data.name)
            pets.append(
                PetModel(
                    name=pet_data.name,
                    species=pet_data.species,
                    age=pet_data.age,
                )
            )

        student.pets = pets
        try:
            self.repository.save(db, student)
            db.commit()
            db.refresh(student)
        except IntegrityError as exc:
            db.rollback()
            raise conflict(
                {"email": {"message": "El correo o nombre de usuario ya está en uso"}}
            ) from exc

        return Student.model_validate(student)

    def update(self, db: Session, student_id: int, data: UpdateStudentDto) -> Student:
        student = self._get_model(db, student_id)
        self.assert_no_conflicts(db, data, except_id=student_id)
        for field, value in data.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(student, field, str(value) if field == "email" else value)

        try:
            db.commit()
            db.refresh(student)
        except IntegrityError as exc:
            db.rollback()
            raise conflict(
                {"email": {"message": "El correo o nombre de usuario ya está en uso"}}
            ) from exc

        return Student.model_validate(student)

    def delete(self, db: Session, student_id: int) -> Student:
        student = self._get_model(db, student_id)
        result = Student.model_validate(student)
        self.repository.delete(db, student)
        db.commit()
        return result

    def assert_no_conflicts(
        self,
        db: Session,
        data: CreateStudentDto | UpdateStudentDto,
        except_id: int | None = None,
    ) -> None:
        errors: FieldErrors = {}
        if data.email:
            existing = self.repository.find_by_email(db, str(data.email))
            if existing and existing.id != except_id:
                errors["email"] = {"message": "El correo electrónico ya está en uso"}

        if data.username:
            existing = self.repository.find_by_username(db, data.username)
            if existing and existing.id != except_id:
                errors["username"] = {"message": "El nombre de usuario ya está en uso"}

        if errors:
            raise conflict(errors)

    def _get_model(self, db: Session, student_id: int) -> StudentModel:
        student = self.repository.find_by_id(db, student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado",
            )
        return student


students_service = StudentsService(students_repository)
