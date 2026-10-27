from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PetORM


class PetsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_all_by_student(self, student_id: str) -> list[PetORM]:
        statement = select(PetORM).where(PetORM.student_id == student_id)
        return list(self.session.scalars(statement).all())

    def find_by_id(self, pet_id: str) -> PetORM | None:
        return self.session.get(PetORM, pet_id)

    def find_by_student_and_name(self, student_id: str, name: str) -> PetORM | None:
        statement = select(PetORM).where(
            PetORM.student_id == student_id,
            PetORM.name == name,
        )
        return self.session.scalar(statement)

    def save(self, pet: PetORM) -> PetORM:
        self.session.add(pet)
        self.session.flush()
        return pet

    def delete(self, pet: PetORM) -> None:
        self.session.delete(pet)
