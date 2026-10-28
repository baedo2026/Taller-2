from sqlalchemy.orm import Session

from app.models import PetModel, StudentModel


class PetsRepository:
    def find_all(self, db: Session) -> list[PetModel]:
        return (
            db.query(PetModel)
            .join(StudentModel, PetModel.owner_id == StudentModel.id)
            .all()
        )

    def find_all_by_student(self, db: Session, student_id: int) -> list[PetModel]:
        return db.query(PetModel).filter(PetModel.owner_id == student_id).all()

    def find_by_id(self, db: Session, pet_id: int) -> PetModel | None:
        return db.query(PetModel).filter(PetModel.id == pet_id).first()

    def find_by_student_and_name(
        self, db: Session, student_id: int, name: str
    ) -> PetModel | None:
        return (
            db.query(PetModel)
            .filter(PetModel.owner_id == student_id, PetModel.name == name)
            .first()
        )

    def save(self, db: Session, pet: PetModel) -> PetModel:
        db.add(pet)
        return pet

    def delete(self, db: Session, pet: PetModel) -> None:
        db.delete(pet)


pets_repository = PetsRepository()
