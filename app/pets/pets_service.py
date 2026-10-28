from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import PetORM
from app.pets.pets_repository import PetsRepository
from app.pets.pets_schemas import CreatePetDto, UpdatePetDto


class PetsService:
    def __init__(self):
        self.repository = PetsRepository()

    def find_all(self, db: Session) -> list[PetORM]:
        return self.repository.find_all(db)

    def find_by_id(self, db: Session, pet_id: str) -> PetORM:
        pet = self.repository.find_by_id(db, pet_id)
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mascota no encontrada"
            )
        return pet

    def create(self, db: Session, dto: CreatePetDto) -> PetORM:
        try:
            pet = PetORM(**dto.model_dump())
            created_pet = self.repository.save(db, pet)
            db.commit()
            db.refresh(created_pet)
            return created_pet
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear la mascota: {str(e)}"
            )

    def update(self, db: Session, pet_id: str, dto: UpdatePetDto) -> PetORM:
        pet = self.find_by_id(db, pet_id)
        update_data = dto.model_dump(exclude_unset=True)

        try:
            for key, value in update_data.items():
                setattr(pet, key, value)
            
            db.commit()
            db.refresh(pet)
            return pet
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al actualizar la mascota: {str(e)}"
            )

    def delete(self, db: Session, pet_id: str) -> None:
        pet = self.find_by_id(db, pet_id)
        try:
            self.repository.delete(db, pet.id)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al eliminar la mascota: {str(e)}"
            )