from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.model.entities import Aluno, EmpresaParceira, InstituicaoEnsino
from src.model.schemas import (
    AlunoCreate,
    AlunoResponse,
    EmpresaCreate,
    EmpresaResponse,
    InstituicaoCreate,
    InstituicaoResponse,
    LoginRequest,
    LoginResponse,
)
from src.repository.repositories import (
    cnpj_in_use,
    cpf_in_use,
    email_or_login_in_use,
    find_institution,
    find_user_by_credentials,
)
from src.service.auth import hash_password, password_matches

router = APIRouter()


@router.post("/instituicoes", response_model=InstituicaoResponse, status_code=status.HTTP_201_CREATED)
def create_institution(payload: InstituicaoCreate, db: Session = Depends(get_db)) -> InstituicaoEnsino:
    institution = InstituicaoEnsino(nome=payload.nome)
    db.add(institution)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Instituição já cadastrada.") from exc
    db.refresh(institution)
    return institution


@router.get("/instituicoes", response_model=list[InstituicaoResponse])
def list_institutions(db: Session = Depends(get_db)) -> list[InstituicaoEnsino]:
    return list(db.query(InstituicaoEnsino).order_by(InstituicaoEnsino.nome).all())


@router.post("/alunos", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: AlunoCreate, db: Session = Depends(get_db)) -> Aluno:
    if email_or_login_in_use(db, payload.email, payload.login) or cpf_in_use(db, payload.cpf):
        raise HTTPException(status_code=409, detail="E-mail, login ou CPF já cadastrado.")
    if find_institution(db, payload.instituicao_id) is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada.")

    student = Aluno(
        nome=payload.nome,
        email=payload.email,
        login=payload.login,
        senha_hash=hash_password(payload.senha),
        cpf=payload.cpf,
        rg=payload.rg,
        endereco=payload.endereco,
        curso=payload.curso,
        instituicao_id=payload.instituicao_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/alunos/{student_id}", response_model=AlunoResponse)
def get_student(student_id: int, db: Session = Depends(get_db)) -> Aluno:
    student = db.get(Aluno, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    return student


@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def create_company(payload: EmpresaCreate, db: Session = Depends(get_db)) -> EmpresaParceira:
    if email_or_login_in_use(db, payload.email, payload.login) or cnpj_in_use(db, payload.cnpj):
        raise HTTPException(status_code=409, detail="E-mail, login ou CNPJ já cadastrado.")

    company = EmpresaParceira(
        nome=payload.nome,
        email=payload.email,
        login=payload.login,
        senha_hash=hash_password(payload.senha),
        cnpj=payload.cnpj,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/empresas/{company_id}", response_model=EmpresaResponse)
def get_company(company_id: int, db: Session = Depends(get_db)) -> EmpresaParceira:
    company = db.get(EmpresaParceira, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa parceira não encontrada.")
    return company


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = find_user_by_credentials(db, payload.login)
    if user is None or not password_matches(payload.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    return LoginResponse(id=user.id, nome=user.nome, tipo=user.tipo)
