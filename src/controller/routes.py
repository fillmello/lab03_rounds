from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.model.entities import Aluno, EmpresaParceira, InstituicaoEnsino, Usuario
from src.model.schemas import (
    AlunoCreate,
    AlunoResponse,
    AlunoUpdate,
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    InstituicaoCreate,
    InstituicaoResponse,
    LoginRequest,
    LoginResponse,
)
from src.repository.repositories import (
    cnpj_in_use,
    cnpj_in_use_for_other,
    cpf_in_use,
    cpf_in_use_for_other,
    email_or_login_in_use,
    email_or_login_in_use_for_other,
    find_institution,
    find_user_by_credentials,
)
from src.service.auth import (
    create_session_token,
    hash_password,
    password_matches,
    read_session_token,
)

router = APIRouter()


def current_user(
    session: str | None = Cookie(default=None), db: Session = Depends(get_db)
) -> Usuario:
    if not session:
        raise HTTPException(status_code=401, detail="Faça login para continuar.")
    data = read_session_token(session)
    user = db.get(Usuario, data["id"]) if data else None
    if user is None:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")
    return user


def require_owner(user: Aluno | EmpresaParceira, resource_id: int) -> None:
    if user.id != resource_id:
        raise HTTPException(status_code=403, detail="Você só pode alterar seu próprio cadastro.")


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
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail, login ou CPF já cadastrado.") from exc
    db.refresh(student)
    return student


@router.get("/alunos", response_model=list[AlunoResponse])
def list_students(user: Aluno | EmpresaParceira = Depends(current_user)) -> list[Aluno]:
    if not isinstance(user, Aluno):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para alunos.")
    return [user]


@router.get("/alunos/{student_id}", response_model=AlunoResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: Aluno | EmpresaParceira = Depends(current_user),
) -> Aluno:
    if not isinstance(user, Aluno):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para alunos.")
    require_owner(user, student_id)
    student = db.get(Aluno, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    return student


@router.put("/alunos/{student_id}", response_model=AlunoResponse)
def update_student(
    student_id: int,
    payload: AlunoUpdate,
    db: Session = Depends(get_db),
    user: Aluno | EmpresaParceira = Depends(current_user),
) -> Aluno:
    if not isinstance(user, Aluno):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para alunos.")
    require_owner(user, student_id)
    student = db.get(Aluno, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return student
    if (
        ("email" in values or "login" in values)
        and email_or_login_in_use_for_other(
            db, values.get("email", student.email), values.get("login", student.login), student.id
        )
    ) or (
        "cpf" in values and cpf_in_use_for_other(db, values["cpf"], student.id)
    ):
        raise HTTPException(status_code=409, detail="E-mail, login ou CPF já cadastrado.")
    if "instituicao_id" in values and find_institution(db, values["instituicao_id"]) is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada.")
    if "senha" in values:
        values["senha_hash"] = hash_password(values.pop("senha"))
    for key, value in values.items():
        setattr(student, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Não foi possível atualizar o aluno.") from exc
    db.refresh(student)
    return student


@router.delete("/alunos/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: Aluno | EmpresaParceira = Depends(current_user),
) -> None:
    if not isinstance(user, Aluno):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para alunos.")
    require_owner(user, student_id)
    student = db.get(Aluno, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    db.delete(student)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Aluno possui registros vinculados e não pode ser removido."
        ) from exc


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
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail, login ou CNPJ já cadastrado.") from exc
    db.refresh(company)
    return company


@router.get("/empresas", response_model=list[EmpresaResponse])
def list_companies(user: Aluno | EmpresaParceira = Depends(current_user)) -> list[EmpresaParceira]:
    if not isinstance(user, EmpresaParceira):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para empresas parceiras.")
    return [user]


@router.get("/empresas/{company_id}", response_model=EmpresaResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    user: Aluno | EmpresaParceira = Depends(current_user),
) -> EmpresaParceira:
    if not isinstance(user, EmpresaParceira):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para empresas parceiras.")
    require_owner(user, company_id)
    company = db.get(EmpresaParceira, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa parceira não encontrada.")
    return company


@router.put("/empresas/{company_id}", response_model=EmpresaResponse)
def update_company(
    company_id: int,
    payload: EmpresaUpdate,
    db: Session = Depends(get_db),
    user: Aluno | EmpresaParceira = Depends(current_user),
) -> EmpresaParceira:
    if not isinstance(user, EmpresaParceira):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para empresas parceiras.")
    require_owner(user, company_id)
    company = db.get(EmpresaParceira, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa parceira não encontrada.")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return company
    if (
        ("email" in values or "login" in values)
        and email_or_login_in_use_for_other(
            db, values.get("email", company.email), values.get("login", company.login), company.id
        )
    ) or (
        "cnpj" in values and cnpj_in_use_for_other(db, values["cnpj"], company.id)
    ):
        raise HTTPException(status_code=409, detail="E-mail, login ou CNPJ já cadastrado.")
    if "senha" in values:
        values["senha_hash"] = hash_password(values.pop("senha"))
    for key, value in values.items():
        setattr(company, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Não foi possível atualizar a empresa.") from exc
    db.refresh(company)
    return company


@router.delete("/empresas/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    user: Aluno | EmpresaParceira = Depends(current_user),
) -> None:
    if not isinstance(user, EmpresaParceira):
        raise HTTPException(status_code=403, detail="Acesso permitido apenas para empresas parceiras.")
    require_owner(user, company_id)
    company = db.get(EmpresaParceira, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Empresa parceira não encontrada.")
    db.delete(company)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Empresa possui vantagens vinculadas e não pode ser removida."
        ) from exc


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> LoginResponse:
    user = find_user_by_credentials(db, payload.login)
    if user is None or not password_matches(payload.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    response.set_cookie(
        "session",
        create_session_token(user.id, user.tipo),
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60 * 60 * 8,
    )
    return LoginResponse(id=user.id, nome=user.nome, tipo=user.tipo)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie("session")
