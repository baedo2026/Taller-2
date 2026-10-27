from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.pets.pets_repository import PetsRepository
from app.pets.pets_model import PetModel
from app.pets.pets_schemas import CreatePetDto, UpdatePetDto
from app.shared.datetimes import utc_now
from app.shared.exceptions import conflict
from app.students.students_service import StudentsService


class PetsService:
    def find_all_for_student(self, student_id: str, db: Session):
        students_service = StudentsService()
        students_service.find_by_id(student_id, db)

        repo = PetsRepository(db)
        pets = sorted(
            repo.find_all_by_student(student_id),
            key=lambda pet: pet.createdAt,
            reverse=True,
        )

        return {"total": len(pets), "items": pets}

    def create(self, student_id: str, data: CreatePetDto, db: Session):
        students_service = StudentsService()
        students_service.find_by_id(student_id, db)
        
        repo = PetsRepository(db)
        self.assert_no_conflicts(student_id, data, repo)

        pet_data = PetModel(
            id=str(uuid4()),
            studentId=student_id,
            name=data.name,
            species=data.species,
            age=data.age,
        )

        return repo.save(pet_data)

    def update(self, student_id: str, pet_id: str, data: UpdatePetDto, db: Session):
        existing = self.find_owned(student_id, pet_id, db)
        repo = PetsRepository(db)
        self.assert_no_conflicts(student_id, data, repo, except_id=pet_id)

        if data.name is not None:
            existing.name = data.name
        if data.species is not None:
            existing.species = data.species
        if data.age is not None:
            existing.age = data.age
        
        existing.updatedAt = utc_now()

        return repo.save(existing)

    def delete(self, student_id: str, pet_id: str, db: Session):
        existing = self.find_owned(student_id, pet_id, db)
        repo = PetsRepository(db)
        repo.delete(pet_id)

        return existing

    def find_owned(self, student_id: str, pet_id: str, db: Session):
        students_service = StudentsService()
        students_service.find_by_id(student_id, db)

        repo = PetsRepository(db)
        pet = repo.find_by_id(pet_id)

        if pet is None or pet.studentId != student_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada",
            )

        return pet

    def assert_no_conflicts(
        self,
        student_id: str,
        data: CreatePetDto | UpdatePetDto,
        repo: PetsRepository,
        except_id: str | None = None,
    ) -> None:
        if not data.name:
            return

        existing = repo.find_by_student_and_name(student_id, data.name)

        if existing and existing.id != except_id:
            raise conflict(
                {"name": {"message": "Ya tienes una mascota con ese nombre"}}
            )


pets_service = PetsService()