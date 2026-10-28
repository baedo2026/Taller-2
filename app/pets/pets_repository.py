from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PetORM


class PetsRepository:
    def find_all(self, db: Session) -> list[PetORM]:
        return list(db.scalars(select(PetORM)).all())

    def find_by_id(self, db: Session, pet_id: str) -> PetORM | None:
        return db.scalar(select(PetORM).where(PetORM.id == pet_id))

    def find_by_student_id(self, db: Session, student_id: str) -> list[PetORM]:
        return list(db.scalars(select(PetORM).where(PetORM.studentId == student_id)).all())

    def save(self, db: Session, pet: PetORM) -> PetORM:
        db.add(pet)
        return pet

    def delete(self, db: Session, pet_id: str) -> None:
        pet = self.find_by_id(db, pet_id)
        if pet:
            db.delete(pet)