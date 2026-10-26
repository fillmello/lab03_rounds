from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.controller.deps import current_student, require_owner
from src.database import get_db
from src.model.entities import Aluno
from src.model.schemas import AlunoCreate, AlunoResponse, AlunoUpdate
from src.service import usuarios

router = APIRouter()


@router.post("/alunos", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: AlunoCreate, db: Session = Depends(get_db)) -> Aluno:
    return usuarios.register_student(db, payload)


@router.get("/alunos", response_model=list[AlunoResponse])
def list_students(student: Aluno = Depends(current_student)) -> list[Aluno]:
    return [student]


def _own_student(student_id: int, student: Aluno = Depends(current_student)) -> Aluno:
    require_owner(student, student_id)
    return student


@router.get("/alunos/{student_id}", response_model=AlunoResponse)
def get_student(student: Aluno = Depends(_own_student)) -> Aluno:
    return student


@router.put("/alunos/{student_id}", response_model=AlunoResponse)
def update_student(
    payload: AlunoUpdate,
    student: Aluno = Depends(_own_student),
    db: Session = Depends(get_db),
) -> Aluno:
    values = payload.model_dump(exclude_unset=True)
    if values:
        usuarios.update_profile(db, student, values)
    return student


@router.delete("/alunos/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student: Aluno = Depends(_own_student), db: Session = Depends(get_db)) -> None:
    usuarios.delete_user(db, student, "Aluno possui registros vinculados e não pode ser removido.")
