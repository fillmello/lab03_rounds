from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.controller.deps import require_admin
from src.database import get_db
from src.model.entities import InstituicaoEnsino, Professor
from src.model.schemas import (
    InstituicaoCreate,
    InstituicaoResponse,
    ProfessorBulkCreate,
    ProfessorCreate,
    ProfessorResponse,
    ProfessorUpdate,
)
from src.repository.repositories import list_professors
from src.service import usuarios
from src.service.errors import ServiceError

# Cadastro de instituições e dos professores enviados por elas (pré-cadastro).
router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])


@router.post("/instituicoes", response_model=InstituicaoResponse, status_code=status.HTTP_201_CREATED)
def create_institution(payload: InstituicaoCreate, db: Session = Depends(get_db)) -> InstituicaoEnsino:
    institution = InstituicaoEnsino(nome=payload.nome)
    db.add(institution)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ServiceError(409, "Instituição já cadastrada.") from exc
    db.refresh(institution)
    return institution


@router.get("/professores", response_model=list[ProfessorResponse])
def get_professors(db: Session = Depends(get_db)) -> list[Professor]:
    return list_professors(db)


@router.post("/professores", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def create_professor(payload: ProfessorCreate, db: Session = Depends(get_db)) -> Professor:
    return usuarios.register_professor(db, payload)


@router.post("/professores/lote", response_model=list[ProfessorResponse], status_code=status.HTTP_201_CREATED)
def create_professors(payload: ProfessorBulkCreate, db: Session = Depends(get_db)) -> list[Professor]:
    return usuarios.register_professors(db, payload.professores)


@router.put("/professores/{professor_id}", response_model=ProfessorResponse)
def update_professor(professor_id: int, payload: ProfessorUpdate, db: Session = Depends(get_db)) -> Professor:
    professor = db.get(Professor, professor_id)
    if professor is None:
        raise ServiceError(404, "Professor não encontrado.")
    values = payload.model_dump(exclude_unset=True)
    if values:
        usuarios.update_profile(db, professor, values)
    return professor
