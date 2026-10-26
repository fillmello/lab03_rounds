import secrets
from datetime import datetime
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.model.entities import (
    Aluno, EmpresaParceira, EnvioMoeda, InstituicaoEnsino, Professor, TrocaVantagem,
    Usuario, Vantagem,
)
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
    EnvioMoedaCreate, EnvioMoedaResponse, ExtratoResponse, ProfessorResponse,
    PasswordChange, ProfessorCreate, ProfessorUpdate, ResgateResponse, TrocaResponse, VantagemCreate,
    VantagemResponse,
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
    if "senha" in values:
        raise HTTPException(status_code=400, detail="Use a opção 'Mudar senha' para alterar sua senha.")
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
    if "senha" in values:
        raise HTTPException(status_code=400, detail="Use a opção 'Mudar senha' para alterar sua senha.")
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


@router.get("/me", response_model=LoginResponse)
def get_current_user(user: Usuario = Depends(current_user)) -> LoginResponse:
    return LoginResponse(id=user.id, nome=user.nome, tipo=user.tipo)


@router.post("/me/senha", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    user: Usuario = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    if not password_matches(payload.senha_atual, user.senha_hash):
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")
    if payload.nova_senha != payload.confirmacao:
        raise HTTPException(status_code=400, detail="A confirmação da nova senha não confere.")
    if password_matches(payload.nova_senha, user.senha_hash):
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual.")
    user.senha_hash = hash_password(payload.nova_senha)
    db.commit()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie("session")


def require_type(user: Usuario, expected: type) -> None:
    if not isinstance(user, expected):
        raise HTTPException(status_code=403, detail="Perfil sem permissão para esta operação.")


@router.get("/professores/{professor_id}", response_model=ProfessorResponse)
def get_professor(professor_id: int, db: Session = Depends(get_db),
                  user: Usuario = Depends(current_user)) -> Professor:
    require_type(user, Professor)
    if user.id != professor_id:
        raise HTTPException(status_code=403, detail="Você só pode consultar seu próprio perfil.")
    professor = db.get(Professor, professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")
    return professor


@router.post("/professores", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def create_professor(
    payload: ProfessorCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Professor:
    require_type(user, EmpresaParceira)
    if email_or_login_in_use(db, payload.email, payload.login) or cpf_in_use(db, payload.cpf):
        raise HTTPException(status_code=409, detail="E-mail, login ou CPF já cadastrado.")
    if find_institution(db, payload.instituicao_id) is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada.")
    semester = f"{datetime.utcnow().year}-{'1' if datetime.utcnow().month <= 6 else '2'}"
    professor = Professor(
        nome=payload.nome,
        email=payload.email,
        login=payload.login,
        senha_hash=hash_password(payload.senha),
        cpf=payload.cpf,
        departamento=payload.departamento,
        instituicao_id=payload.instituicao_id,
        saldo=1000,
        ultimo_credito_semestre=semester,
    )
    db.add(professor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail, login ou CPF já cadastrado.") from exc
    db.refresh(professor)
    return professor


@router.get("/professores", response_model=list[ProfessorResponse])
def list_professors(
    db: Session = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> list[Professor]:
    require_type(user, EmpresaParceira)
    return list(db.query(Professor).order_by(Professor.nome).all())


@router.put("/professores/{professor_id}", response_model=ProfessorResponse)
def update_professor(
    professor_id: int,
    payload: ProfessorUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Professor:
    require_type(user, EmpresaParceira)
    professor = db.get(Professor, professor_id)
    if professor is None:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        return professor
    if (
        ("email" in values or "login" in values)
        and email_or_login_in_use_for_other(
            db, values.get("email", professor.email), values.get("login", professor.login), professor.id
        )
    ) or ("cpf" in values and cpf_in_use_for_other(db, values["cpf"], professor.id)):
        raise HTTPException(status_code=409, detail="E-mail, login ou CPF já cadastrado.")
    if "instituicao_id" in values and find_institution(db, values["instituicao_id"]) is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada.")
    for key, value in values.items():
        setattr(professor, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Não foi possível atualizar o professor.") from exc
    db.refresh(professor)
    return professor


@router.post("/moedas/enviar", response_model=EnvioMoedaResponse, status_code=201)
@router.post("/envios", response_model=EnvioMoedaResponse, status_code=201, include_in_schema=False)
def send_coins(payload: EnvioMoedaCreate, db: Session = Depends(get_db),
               user: Usuario = Depends(current_user)) -> EnvioMoeda:
    require_type(user, Professor)
    professor = db.get(Professor, user.id)
    aluno = db.get(Aluno, payload.aluno_id)
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno não encontrado.")
    if professor.instituicao_id != aluno.instituicao_id:
        raise HTTPException(status_code=403, detail="Professor e aluno devem pertencer à mesma instituição.")
    if professor.saldo < payload.quantidade:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")
    professor.saldo -= payload.quantidade
    aluno.saldo += payload.quantidade
    envio = EnvioMoeda(quantidade=payload.quantidade, motivo=payload.motivo,
                        professor_id=professor.id, aluno_id=aluno.id)
    db.add(envio)
    db.commit()
    db.refresh(envio)
    return envio


@router.get("/extratos/professor", response_model=ExtratoResponse)
@router.get("/extrato/professor", response_model=ExtratoResponse, include_in_schema=False)
def professor_statement(db: Session = Depends(get_db),
                        user: Usuario = Depends(current_user)) -> ExtratoResponse:
    require_type(user, Professor)
    professor = db.get(Professor, user.id)
    envios = list(db.query(EnvioMoeda).filter_by(professor_id=user.id)
                  .order_by(EnvioMoeda.data.desc()).all())
    return ExtratoResponse(saldo=professor.saldo, envios=envios, trocas=[])


@router.get("/extratos/aluno", response_model=ExtratoResponse)
@router.get("/extrato/aluno", response_model=ExtratoResponse, include_in_schema=False)
def student_statement(db: Session = Depends(get_db),
                      user: Usuario = Depends(current_user)) -> ExtratoResponse:
    require_type(user, Aluno)
    aluno = db.get(Aluno, user.id)
    envios = list(db.query(EnvioMoeda).filter_by(aluno_id=user.id)
                  .order_by(EnvioMoeda.data.desc()).all())
    trocas = list(db.query(TrocaVantagem).filter_by(aluno_id=user.id)
                  .order_by(TrocaVantagem.data.desc()).all())
    return ExtratoResponse(saldo=aluno.saldo, envios=envios, trocas=trocas)


@router.post("/vantagens", response_model=VantagemResponse, status_code=201)
def create_advantage(payload: VantagemCreate, db: Session = Depends(get_db),
                     user: Usuario = Depends(current_user)) -> Vantagem:
    require_type(user, EmpresaParceira)
    advantage = Vantagem(**payload.model_dump(), empresa_id=user.id)
    db.add(advantage)
    db.commit()
    db.refresh(advantage)
    return advantage


@router.get("/vantagens", response_model=list[VantagemResponse])
def list_advantages(db: Session = Depends(get_db),
                     user: Usuario = Depends(current_user)) -> list[Vantagem]:
    require_type(user, (Aluno, EmpresaParceira))
    return list(db.query(Vantagem).order_by(Vantagem.id).all())


@router.get("/vantagens/{advantage_id}", response_model=VantagemResponse)
def get_advantage(advantage_id: int, db: Session = Depends(get_db),
                  user: Usuario = Depends(current_user)) -> Vantagem:
    require_type(user, (Aluno, EmpresaParceira))
    advantage = db.get(Vantagem, advantage_id)
    if advantage is None:
        raise HTTPException(status_code=404, detail="Vantagem não encontrada.")
    return advantage


@router.put("/vantagens/{advantage_id}", response_model=VantagemResponse)
def update_advantage(advantage_id: int, payload: VantagemCreate, db: Session = Depends(get_db),
                     user: Usuario = Depends(current_user)) -> Vantagem:
    require_type(user, EmpresaParceira)
    advantage = db.get(Vantagem, advantage_id)
    if advantage is None:
        raise HTTPException(status_code=404, detail="Vantagem não encontrada.")
    if advantage.empresa_id != user.id:
        raise HTTPException(status_code=403, detail="Você só pode alterar suas vantagens.")
    for key, value in payload.model_dump().items():
        setattr(advantage, key, value)
    db.commit()
    db.refresh(advantage)
    return advantage


@router.delete("/vantagens/{advantage_id}", status_code=204)
def delete_advantage(advantage_id: int, db: Session = Depends(get_db),
                     user: Usuario = Depends(current_user)) -> None:
    require_type(user, EmpresaParceira)
    advantage = db.get(Vantagem, advantage_id)
    if advantage is None:
        raise HTTPException(status_code=404, detail="Vantagem não encontrada.")
    if advantage.empresa_id != user.id:
        raise HTTPException(status_code=403, detail="Você só pode remover suas vantagens.")
    if db.query(TrocaVantagem).filter_by(vantagem_id=advantage_id).first():
        raise HTTPException(status_code=409, detail="Vantagem já possui resgates.")
    db.delete(advantage)
    db.commit()


@router.post("/vantagens/{advantage_id}/resgatar", response_model=ResgateResponse, status_code=201)
@router.post("/vantagens/{advantage_id}/trocar", response_model=ResgateResponse,
             status_code=201, include_in_schema=False)
def redeem_advantage(advantage_id: int, db: Session = Depends(get_db),
                     user: Usuario = Depends(current_user)) -> ResgateResponse:
    require_type(user, Aluno)
    aluno = db.get(Aluno, user.id)
    advantage = db.get(Vantagem, advantage_id)
    if advantage is None:
        raise HTTPException(status_code=404, detail="Vantagem não encontrada.")
    if aluno.saldo < advantage.custo_em_moedas:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")
    aluno.saldo -= advantage.custo_em_moedas
    troca = TrocaVantagem(quantidade=advantage.custo_em_moedas,
                          codigo=secrets.token_urlsafe(16),
                          aluno_id=aluno.id, vantagem_id=advantage.id)
    db.add(troca)
    db.commit()
    return ResgateResponse(codigo=troca.codigo, quantidade=troca.quantidade,
                           vantagem_id=troca.vantagem_id, saldo_restante=aluno.saldo)


@router.get("/trocas/{codigo}", response_model=TrocaResponse)
def check_redemption(codigo: str, db: Session = Depends(get_db),
                      user: Usuario = Depends(current_user)) -> TrocaVantagem:
    require_type(user, EmpresaParceira)
    troca = db.query(TrocaVantagem).join(Vantagem).filter(
        TrocaVantagem.codigo == codigo, Vantagem.empresa_id == user.id
    ).first()
    if troca is None:
        raise HTTPException(status_code=404, detail="Cupom não encontrado.")
    return troca
