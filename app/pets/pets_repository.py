from sqlalchemy.orm import Session
from app.pets.pets_model import PetModel

class PetsRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all_by_student(self, student_id: str):
        return self.db.query(PetModel).filter(PetModel.studentId == student_id).all()

    def find_by_id(self, pet_id: str):
        return self.db.query(PetModel).filter(PetModel.id == pet_id).first()

    def find_by_student_and_name(self, student_id: str, name: str):
        return self.db.query(PetModel).filter(
            PetModel.studentId == student_id,
            PetModel.name == name
        ).first()

    def save(self, pet_model: PetModel):
        self.db.add(pet_model)
        self.db.commit()
        self.db.refresh(pet_model)
        return pet_model

    def delete(self, pet_id: str):
        pet = self.find_by_id(pet_id)
        if pet:
            self.db.delete(pet)
            self.db.commit()

    def delete_by_student(self, student_id: str):
        self.db.query(PetModel).filter(PetModel.studentId == student_id).delete()
        self.db.commit()