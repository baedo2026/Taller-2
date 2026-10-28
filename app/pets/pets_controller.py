from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.pets.pets_schemas import (
    CreatePetDto,
    Pet,
    PetList,
    PetWithStudent,
    UpdatePetDto,
)
from app.pets.pets_service import pets_service

all_pets_router = APIRouter(prefix="/api/pets", tags=["Pets"])
router = APIRouter(prefix="/api/students/{student_id}/pets", tags=["Pets"])


@all_pets_router.get("")
def find_all(db: Session = Depends(get_db)) -> list[PetWithStudent]:
    return pets_service.find_all(db)


@router.get("", response_model=PetList)
def find_all_for_student(student_id: int, db: Session = Depends(get_db)) -> PetList:
    return pets_service.find_all_for_student(db, student_id)


@router.post("", response_model=Pet, status_code=status.HTTP_201_CREATED)
def create(student_id: int, data: CreatePetDto, db: Session = Depends(get_db)) -> Pet:
    return pets_service.create(db, student_id, data)


@router.patch("/{pet_id}", response_model=Pet)
def update(
    student_id: int,
    pet_id: int,
    data: UpdatePetDto,
    db: Session = Depends(get_db),
) -> Pet:
    return pets_service.update(db, student_id, pet_id, data)


@router.delete("/{pet_id}", response_model=Pet)
def delete(student_id: int, pet_id: int, db: Session = Depends(get_db)) -> Pet:
    return pets_service.delete(db, student_id, pet_id)
