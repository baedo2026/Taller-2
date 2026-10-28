from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.pets.pets_schemas import Pet, CreatePetDto, UpdatePetDto
from app.pets.pets_service import PetsService

router = APIRouter(prefix="/pets", tags=["Pets"])
service = PetsService()


@router.get("", response_model=list[Pet])
def get_all_pets(db: Session = Depends(get_db)):
    return service.find_all(db)


@router.get("/{pet_id}", response_model=Pet)
def get_pet_by_id(pet_id: str, db: Session = Depends(get_db)):
    return service.find_by_id(db, pet_id)


@router.post("", response_model=Pet, status_code=status.HTTP_201_CREATED)
def create_pet(dto: CreatePetDto, db: Session = Depends(get_db)):
    return service.create(db, dto)


@router.patch("/{pet_id}", response_model=Pet)
def update_pet(pet_id: str, dto: UpdatePetDto, db: Session = Depends(get_db)):
    return service.update(db, pet_id, dto)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: str, db: Session = Depends(get_db)):
    service.delete(db, pet_id)