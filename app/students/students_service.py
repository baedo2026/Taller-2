from typing import NoReturn
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.db.models import PetORM, StudentORM
from app.pets.pets_repository import PetsRepository
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.shared.types import FieldErrors
from app.students.students_repository import StudentsRepository
from app.students.students_schemas import (
    CreateStudentDto,
    Student,
    StudentList,
    UpdateStudentDto,
)


class StudentsService:
    def __init__(self, repository: StudentsRepository, pets: PetsRepository) -> None:
        self.repository = repository
        self.pets_repository = pets

    def find_all(self) -> StudentList:
        students = sorted(
            self.repository.find_all(),
            key=lambda student: student.created_at,
            reverse=True,
        )
        return StudentList(total=len(students), items=[Student.model_validate(s) for s in students])

    def _find_model_by_id(self, student_id: str) -> StudentORM:
        student = self.repository.find_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado")
        return student

    def find_by_id(self, student_id: str) -> Student:
        return Student.model_validate(self._find_model_by_id(student_id))

    def create(self, data: CreateStudentDto) -> Student:
        try:
            with self.repository.session.begin():
                self.assert_no_conflicts(data)
                now = utc_now()
                student = StudentORM(
                    id=str(uuid4()), name=data.name, username=data.username,
                    email=str(data.email), age=data.age, created_at=now, updated_at=now,
                )
                self.repository.save(student)
                for pet_data in data.pets:
                    if self.pets_repository.find_by_student_and_name(student.id, pet_data.name):
                        raise conflict({"name": {"message": "Ya tienes una mascota con ese nombre"}})
                    pet_now = utc_now()
                    self.pets_repository.save(PetORM(
                        id=str(uuid4()), student_id=student.id, name=pet_data.name,
                        species=pet_data.species, age=pet_data.age,
                        created_at=pet_now, updated_at=pet_now,
                    ))
                result = Student.model_validate(student)
            return result
        except IntegrityError as exc:
            _raise_student_integrity_conflict(exc)

    def update(self, student_id: str, data: UpdateStudentDto) -> Student:
        try:
            with self.repository.session.begin():
                existing = self._find_model_by_id(student_id)
                self.assert_no_conflicts(data, except_id=student_id)
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(existing, field, value)
                existing.updated_at = utc_now()
                self.repository.session.flush()
                result = Student.model_validate(existing)
            return result
        except IntegrityError as exc:
            _raise_student_integrity_conflict(exc)

    def delete(self, student_id: str) -> Student:
        with self.repository.session.begin():
            existing = self._find_model_by_id(student_id)
            result = Student.model_validate(existing)
            self.repository.delete(existing)
        return result

    def assert_no_conflicts(self, data: CreateStudentDto | UpdateStudentDto, except_id: str | None = None) -> None:
        errors: FieldErrors = {}
        if data.email:
            existing = self.repository.find_by_email(str(data.email))
            if existing and existing.id != except_id:
                errors["email"] = {"message": "El correo electrónico ya está en uso"}
        if data.username:
            existing = self.repository.find_by_username(data.username)
            if existing and existing.id != except_id:
                errors["username"] = {"message": "El nombre de usuario ya está en uso"}
        if errors:
            raise conflict(errors)


def _raise_student_integrity_conflict(exc: IntegrityError) -> NoReturn:
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    if constraint == "uq_students_email":
        raise conflict({"email": {"message": "El correo electrónico ya está en uso"}}) from exc
    if constraint == "uq_students_username":
        raise conflict({"username": {"message": "El nombre de usuario ya está en uso"}}) from exc
    raise exc
