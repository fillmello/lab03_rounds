from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.controller.deps import current_professor, require_owner
from src.database import get_db
from src.model.entities import Aluno, Professor
from src.model.schemas import AlunoResumo, ProfessorResponse
from src.repository.repositories import list_students_of_institution
from src.service import semestre

router = APIRouter()


@router.get("/professores/me/alunos", response_model=list[AlunoResumo])
def list_my_students(
    professor: Professor = Depends(current_professor), db: Session = Depends(get_db)
) -> list[Aluno]:
    return list_students_of_institution(db, professor.instituicao_id)


@router.get("/professores/{professor_id}", response_model=ProfessorResponse)
def get_professor(
    professor_id: int,
    professor: Professor = Depends(current_professor),
    db: Session = Depends(get_db),
) -> Professor:
    require_owner(professor, professor_id)
    semestre.ensure_credited(db, professor)
    return professor
