from sqlalchemy import select
from sqlalchemy.orm import Session

from src.model.entities import Aluno, EmpresaParceira, InstituicaoEnsino, Professor, Usuario


def find_user_by_credentials(db: Session, login: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.login == login))


def find_institution(db: Session, institution_id: int) -> InstituicaoEnsino | None:
    return db.get(InstituicaoEnsino, institution_id)


def email_or_login_in_use(db: Session, email: str, login: str) -> bool:
    return db.scalar(select(Usuario.id).where((Usuario.email == email) | (Usuario.login == login))) is not None


def cpf_in_use(db: Session, cpf: str) -> bool:
    return db.scalar(select(Aluno.id).where(Aluno.cpf == cpf)) is not None or db.scalar(
        select(Professor.id).where(Professor.cpf == cpf)
    ) is not None


def cnpj_in_use(db: Session, cnpj: str) -> bool:
    return db.scalar(select(EmpresaParceira.id).where(EmpresaParceira.cnpj == cnpj)) is not None


def email_or_login_in_use_for_other(
    db: Session, email: str, login: str, user_id: int
) -> bool:
    return db.scalar(
        select(Usuario.id).where(
            Usuario.id != user_id,
            ((Usuario.email == email) | (Usuario.login == login)),
        )
    ) is not None


def cpf_in_use_for_other(db: Session, cpf: str, student_id: int) -> bool:
    return (
        db.scalar(select(Aluno.id).where(Aluno.cpf == cpf, Aluno.id != student_id)) is not None
        or db.scalar(select(Professor.id).where(Professor.cpf == cpf, Professor.id != student_id)) is not None
    )


def cnpj_in_use_for_other(db: Session, cnpj: str, company_id: int) -> bool:
    return db.scalar(
        select(EmpresaParceira.id).where(
            EmpresaParceira.cnpj == cnpj, EmpresaParceira.id != company_id
        )
    ) is not None
