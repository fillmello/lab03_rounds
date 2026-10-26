from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.model.entities import Aluno, EmpresaParceira, Professor, Usuario
from src.model.schemas import (
    AlunoCreate,
    EmpresaCreate,
    PasswordChange,
    ProfessorCreate,
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
from src.service import semestre, throttle
from src.service.auth import hash_password, needs_rehash, password_matches
from src.service.errors import ServiceError

DUPLICATE_PERSON = "E-mail, login ou CPF já cadastrado."
DUPLICATE_COMPANY = "E-mail, login ou CNPJ já cadastrado."


def _commit(db: Session, conflict_detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ServiceError(409, conflict_detail) from exc


def authenticate(db: Session, login: str, password: str) -> Usuario:
    key = f"login:{login.strip().lower()}"
    throttle.ensure_allowed(key)
    user = find_user_by_credentials(db, login)
    if user is None or not password_matches(password, user.senha_hash):
        throttle.register_failure(key)
        raise ServiceError(401, "Credenciais inválidas.")
    throttle.reset(key)
    if needs_rehash(user.senha_hash):
        user.senha_hash = hash_password(password)
        db.commit()
    return user


def change_password(db: Session, user: Usuario, payload: PasswordChange) -> None:
    key = f"senha:{user.id}"
    throttle.ensure_allowed(key)
    if not password_matches(payload.senha_atual, user.senha_hash):
        throttle.register_failure(key)
        raise ServiceError(400, "A senha atual está incorreta.")
    if payload.nova_senha != payload.confirmacao:
        raise ServiceError(400, "A confirmação da nova senha não confere.")
    if password_matches(payload.nova_senha, user.senha_hash):
        raise ServiceError(400, "A nova senha deve ser diferente da atual.")
    user.senha_hash = hash_password(payload.nova_senha)
    db.commit()
    throttle.reset(key)


def register_student(db: Session, payload: AlunoCreate) -> Aluno:
    if email_or_login_in_use(db, payload.email, payload.login) or cpf_in_use(db, payload.cpf):
        raise ServiceError(409, DUPLICATE_PERSON)
    if find_institution(db, payload.instituicao_id) is None:
        raise ServiceError(404, "Instituição não encontrada.")
    data = payload.model_dump(exclude={"senha"})
    student = Aluno(**data, senha_hash=hash_password(payload.senha))
    db.add(student)
    _commit(db, DUPLICATE_PERSON)
    db.refresh(student)
    return student


def register_company(db: Session, payload: EmpresaCreate) -> EmpresaParceira:
    if email_or_login_in_use(db, payload.email, payload.login) or cnpj_in_use(db, payload.cnpj):
        raise ServiceError(409, DUPLICATE_COMPANY)
    data = payload.model_dump(exclude={"senha"})
    company = EmpresaParceira(**data, senha_hash=hash_password(payload.senha))
    db.add(company)
    _commit(db, DUPLICATE_COMPANY)
    db.refresh(company)
    return company


def build_professor(db: Session, payload: ProfessorCreate) -> Professor:
    """Valida e monta o professor sem commitar (usado também na importação em lote)."""
    if email_or_login_in_use(db, payload.email, payload.login) or cpf_in_use(db, payload.cpf):
        raise ServiceError(409, f"{DUPLICATE_PERSON} ({payload.login})")
    if find_institution(db, payload.instituicao_id) is None:
        raise ServiceError(404, "Instituição não encontrada.")
    data = payload.model_dump(exclude={"senha"})
    professor = Professor(**data, senha_hash=hash_password(payload.senha), saldo=0)
    semestre.credit_if_due(professor)
    return professor


def register_professor(db: Session, payload: ProfessorCreate) -> Professor:
    professor = build_professor(db, payload)
    db.add(professor)
    _commit(db, DUPLICATE_PERSON)
    db.refresh(professor)
    return professor


def register_professors(db: Session, payloads: list[ProfessorCreate]) -> list[Professor]:
    """Tudo ou nada: um registro inválido ou duplicado cancela o lote inteiro."""
    seen_logins: set[str] = set()
    seen_emails: set[str] = set()
    seen_cpfs: set[str] = set()
    professors = []
    for payload in payloads:
        if payload.login in seen_logins or payload.email in seen_emails or payload.cpf in seen_cpfs:
            raise ServiceError(409, f"{DUPLICATE_PERSON} ({payload.login}, repetido na lista)")
        seen_logins.add(payload.login)
        seen_emails.add(payload.email)
        seen_cpfs.add(payload.cpf)
        professors.append(build_professor(db, payload))
    db.add_all(professors)
    _commit(db, DUPLICATE_PERSON)
    return professors


def update_profile(db: Session, user: Usuario, values: dict) -> None:
    """Atualiza um perfil (aluno, empresa ou professor) validando unicidade e instituição."""
    if "senha" in values:
        raise ServiceError(400, "Use a opção 'Mudar senha' para alterar sua senha.")
    if ("email" in values or "login" in values) and email_or_login_in_use_for_other(
        db, values.get("email", user.email), values.get("login", user.login), user.id
    ):
        raise ServiceError(409, DUPLICATE_COMPANY if isinstance(user, EmpresaParceira) else DUPLICATE_PERSON)
    if "cpf" in values and cpf_in_use_for_other(db, values["cpf"], user.id):
        raise ServiceError(409, DUPLICATE_PERSON)
    if "cnpj" in values and cnpj_in_use_for_other(db, values["cnpj"], user.id):
        raise ServiceError(409, DUPLICATE_COMPANY)
    if "instituicao_id" in values and find_institution(db, values["instituicao_id"]) is None:
        raise ServiceError(404, "Instituição não encontrada.")
    for key, value in values.items():
        setattr(user, key, value)
    _commit(db, "Não foi possível atualizar o cadastro.")
    db.refresh(user)


def delete_user(db: Session, user: Usuario, conflict_detail: str) -> None:
    db.delete(user)
    _commit(db, conflict_detail)
