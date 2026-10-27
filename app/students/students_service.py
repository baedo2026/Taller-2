from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.students.students_repository import StudentsRepository
from app.students.students_model import StudentModel
from app.pets.pets_model import PetModel
from app.students.students_schemas import CreateStudentDto, UpdateStudentDto

class StudentsService:
    def find_all(self, db: Session):
        repo = StudentsRepository(db)
        students = repo.find_all()
        return {"total": len(students), "items": students}

    def find_by_id(self, student_id: str, db: Session):
        repo = StudentsRepository(db)
        student = repo.find_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student

    def create(self, body: CreateStudentDto, db: Session):
        repo = StudentsRepository(db)
        
        if repo.find_by_email(body.email):
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        if repo.find_by_username(body.username):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

        student_data = StudentModel(
            name=body.name,
            username=body.username,
            email=body.email,
            age=body.age
        )

        pets_data = [
            PetModel(name=pet.name, species=pet.species, age=pet.age) 
            for pet in body.pets
        ]

        return repo.create_student_with_pets(student_data, pets_data)

    def update(self, student_id: str, body: UpdateStudentDto, db: Session):
        repo = StudentsRepository(db)
        student = repo.find_by_id(student_id)
        
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")

        if body.name is not None:
            student.name = body.name
        if body.username is not None:
            if repo.find_by_username(body.username) and student.username != body.username:
                raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
            student.username = body.username
        if body.email is not None:
            if repo.find_by_email(body.email) and student.email != body.email:
                raise HTTPException(status_code=400, detail="El correo ya está en uso")
            student.email = body.email
        if body.age is not None:
            student.age = body.age

        return repo.save(student)

    def delete(self, student_id: str, db: Session):
        repo = StudentsRepository(db)
        student = repo.find_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        repo.delete(student_id)
        return student

students_service = StudentsService()