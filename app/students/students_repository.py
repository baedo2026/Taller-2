from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.students.students_model import StudentModel
from app.pets.pets_model import PetModel

class StudentsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self):
        return self.db.query(StudentModel).all()

    def find_by_id(self, student_id: str):
        return self.db.query(StudentModel).filter(StudentModel.id == student_id).first()

    def find_by_email(self, email: str):
        return self.db.query(StudentModel).filter(StudentModel.email == email).first()

    def find_by_username(self, username: str):
        return self.db.query(StudentModel).filter(StudentModel.username == username).first()

    def save(self, student_model: StudentModel):
        try:
            self.db.add(student_model)
            self.db.commit()
            self.db.refresh(student_model)
            return student_model
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Error al guardar el estudiante.")

    def delete(self, student_id: str) -> None:
        student = self.find_by_id(student_id)
        if student:
            try:
                self.db.delete(student)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise HTTPException(status_code=400, detail="Error al eliminar el estudiante.")

    def create_student_with_pets(self, student_data: StudentModel, pets_data: list[PetModel]):
        try:
            self.db.add(student_data)
            
            for pet in pets_data:
                self.db.add(pet)
                
            self.db.commit()
            self.db.refresh(student_data)
            return student_data
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Error en la transacción, se han revertido los cambios: {str(e)}")