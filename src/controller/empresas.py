from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.controller.deps import current_company, require_owner
from src.database import get_db
from src.model.entities import EmpresaParceira
from src.model.schemas import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from src.service import usuarios

router = APIRouter()


@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def create_company(payload: EmpresaCreate, db: Session = Depends(get_db)) -> EmpresaParceira:
    return usuarios.register_company(db, payload)


@router.get("/empresas", response_model=list[EmpresaResponse])
def list_companies(company: EmpresaParceira = Depends(current_company)) -> list[EmpresaParceira]:
    return [company]


def _own_company(company_id: int, company: EmpresaParceira = Depends(current_company)) -> EmpresaParceira:
    require_owner(company, company_id)
    return company


@router.get("/empresas/{company_id}", response_model=EmpresaResponse)
def get_company(company: EmpresaParceira = Depends(_own_company)) -> EmpresaParceira:
    return company


@router.put("/empresas/{company_id}", response_model=EmpresaResponse)
def update_company(
    payload: EmpresaUpdate,
    company: EmpresaParceira = Depends(_own_company),
    db: Session = Depends(get_db),
) -> EmpresaParceira:
    values = payload.model_dump(exclude_unset=True)
    if values:
        usuarios.update_profile(db, company, values)
    return company


@router.delete("/empresas/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company: EmpresaParceira = Depends(_own_company), db: Session = Depends(get_db)) -> None:
    usuarios.delete_user(db, company, "Empresa possui vantagens vinculadas e não pode ser removida.")
