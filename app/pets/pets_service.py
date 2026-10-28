from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import PetModel
from app.pets.pets_repository import PetsRepository, pets_repository
from app.pets.pets_schemas import (
    CreatePetDto,
    Pet,
    PetList,
    PetWithStudent,
    UpdatePetDto,
)
from app.shared.exceptions import conflict
from app.students.students_repository import StudentsRepository, students_repository
from app.students.students_service import StudentsService, students_service


class PetsService:
    def __init__(
        self,
        repository: PetsRepository,
        students_repository: StudentsRepository,
        students: StudentsService,
    ) -> None:
        self.repository = repository
        self.students_repository = students_repository
        self.students_service = students

    def find_all(self, db: Session) -> list[PetWithStudent]:
        pets = sorted(
            self.repository.find_all(db),
            key=lambda pet: pet.createdAt,
            reverse=True,
        )
        return [
            PetWithStudent(
                **Pet.model_validate(pet).model_dump(),
                studentName=pet.owner.name,
                studentUsername=pet.owner.username,
            )
            for pet in pets
        ]

    def find_all_for_student(self, db: Session, student_id: int) -> PetList:
        self.students_service.find_by_id(db, student_id)
        pets = sorted(
            self.repository.find_all_by_student(db, student_id),
            key=lambda pet: pet.createdAt,
            reverse=True,
        )
        return PetList(
            total=len(pets),
            items=[Pet.model_validate(pet) for pet in pets],
        )

    def create(self, db: Session, student_id: int, data: CreatePetDto) -> Pet:
        self.students_service.find_by_id(db, student_id)
        self.assert_no_conflicts(db, student_id, data)
        pet = PetModel(
            owner_id=student_id,
            name=data.name,
            species=data.species,
            age=data.age,
        )
        try:
            self.repository.save(db, pet)
            db.commit()
            db.refresh(pet)
        except IntegrityError as exc:
            db.rollback()
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            ) from exc
        return Pet.model_validate(pet)

    def update(
        self, db: Session, student_id: int, pet_id: int, data: UpdatePetDto
    ) -> Pet:
        pet = self._find_owned(db, student_id, pet_id)
        self.assert_no_conflicts(db, student_id, data, except_id=pet_id)
        for field, value in data.model_dump(
            exclude_unset=True, exclude_none=True
        ).items():
            setattr(pet, field, value)
        try:
            db.commit()
            db.refresh(pet)
        except IntegrityError as exc:
            db.rollback()
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            ) from exc
        return Pet.model_validate(pet)

    def delete(self, db: Session, student_id: int, pet_id: int) -> Pet:
        pet = self._find_owned(db, student_id, pet_id)
        result = Pet.model_validate(pet)
        self.repository.delete(db, pet)
        db.commit()
        return result

    def assert_no_conflicts(
        self,
        db: Session,
        student_id: int,
        data: CreatePetDto | UpdatePetDto,
        except_id: int | None = None,
    ) -> None:
        if not data.name:
            return
        existing = self.repository.find_by_student_and_name(db, student_id, data.name)
        if existing and existing.id != except_id:
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            )

    def _find_owned(self, db: Session, student_id: int, pet_id: int) -> PetModel:
        self.students_service.find_by_id(db, student_id)
        pet = self.repository.find_by_id(db, pet_id)
        if pet is None or pet.owner_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )
        return pet


pets_service = PetsService(pets_repository, students_repository, students_service)
