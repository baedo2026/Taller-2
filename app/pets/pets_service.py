from typing import NoReturn
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.db.models import PetORM
from app.pets.pets_repository import PetsRepository
from app.pets.pets_schemas import CreatePetDto, Pet, PetList, UpdatePetDto
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.students.students_service import StudentsService


class PetsService:
    def __init__(self, repository: PetsRepository, students: StudentsService) -> None:
        self.repository = repository
        self.students_service = students

    def find_all_for_student(self, student_id: str) -> PetList:
        self.students_service.find_by_id(student_id)
        pets = sorted(self.repository.find_all_by_student(student_id), key=lambda pet: pet.created_at, reverse=True)
        return PetList(total=len(pets), items=[Pet.model_validate(pet) for pet in pets])

    def create(self, student_id: str, data: CreatePetDto) -> Pet:
        try:
            with self.repository.session.begin():
                self.students_service.find_by_id(student_id)
                self.assert_no_conflicts(student_id, data)
                now = utc_now()
                pet = PetORM(
                    id=str(uuid4()), student_id=student_id, name=data.name,
                    species=data.species, age=data.age, created_at=now, updated_at=now,
                )
                self.repository.save(pet)
                result = Pet.model_validate(pet)
            return result
        except IntegrityError as exc:
            _raise_pet_integrity_conflict(exc)

    def update(self, student_id: str, pet_id: str, data: UpdatePetDto) -> Pet:
        try:
            with self.repository.session.begin():
                existing = self.find_owned(student_id, pet_id)
                self.assert_no_conflicts(student_id, data, except_id=pet_id)
                for field, value in data.model_dump(exclude_none=True).items():
                    setattr(existing, field, value)
                existing.updated_at = utc_now()
                self.repository.session.flush()
                result = Pet.model_validate(existing)
            return result
        except IntegrityError as exc:
            _raise_pet_integrity_conflict(exc)

    def delete(self, student_id: str, pet_id: str) -> Pet:
        with self.repository.session.begin():
            existing = self.find_owned(student_id, pet_id)
            result = Pet.model_validate(existing)
            self.repository.delete(existing)
        return result

    def find_owned(self, student_id: str, pet_id: str) -> PetORM:
        self.students_service.find_by_id(student_id)
        pet = self.repository.find_by_id(pet_id)
        if pet is None or pet.student_id != student_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada")
        return pet

    def assert_no_conflicts(self, student_id: str, data: CreatePetDto | UpdatePetDto, except_id: str | None = None) -> None:
        if not data.name:
            return
        existing = self.repository.find_by_student_and_name(student_id, data.name)
        if existing and existing.id != except_id:
            raise conflict({"name": {"message": "Ya tienes una mascota con ese nombre"}})


def _raise_pet_integrity_conflict(exc: IntegrityError) -> NoReturn:
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    if constraint == "uq_pets_student_name":
        raise conflict({"name": {"message": "Ya tienes una mascota con ese nombre"}}) from exc
    raise exc
