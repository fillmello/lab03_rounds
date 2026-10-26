from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.model.entities import (
    Aluno,
    EmpresaParceira,
    EnvioMoeda,
    InstituicaoEnsino,
    Professor,
    TrocaVantagem,
    Usuario,
    Vantagem,
)


def find_user_by_credentials(db: Session, login: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.login == login))


def find_institution(db: Session, institution_id: int) -> InstituicaoEnsino | None:
    return db.get(InstituicaoEnsino, institution_id)


def list_institutions(db: Session) -> list[InstituicaoEnsino]:
    return list(db.scalars(select(InstituicaoEnsino).order_by(InstituicaoEnsino.nome)))


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


def cpf_in_use_for_other(db: Session, cpf: str, user_id: int) -> bool:
    return (
        db.scalar(select(Aluno.id).where(Aluno.cpf == cpf, Aluno.id != user_id)) is not None
        or db.scalar(select(Professor.id).where(Professor.cpf == cpf, Professor.id != user_id)) is not None
    )


def cnpj_in_use_for_other(db: Session, cnpj: str, company_id: int) -> bool:
    return db.scalar(
        select(EmpresaParceira.id).where(
            EmpresaParceira.cnpj == cnpj, EmpresaParceira.id != company_id
        )
    ) is not None


def list_students_of_institution(db: Session, institution_id: int) -> list[Aluno]:
    return list(
        db.scalars(select(Aluno).where(Aluno.instituicao_id == institution_id).order_by(Aluno.nome))
    )


def list_professors(db: Session) -> list[Professor]:
    return list(db.scalars(select(Professor).order_by(Professor.nome)))


def list_sent_coins(db: Session, professor_id: int) -> list[EnvioMoeda]:
    return list(
        db.scalars(
            select(EnvioMoeda)
            .where(EnvioMoeda.professor_id == professor_id)
            .options(joinedload(EnvioMoeda.professor), joinedload(EnvioMoeda.aluno))
            .order_by(EnvioMoeda.data.desc(), EnvioMoeda.id.desc())
        )
    )


def list_received_coins(db: Session, student_id: int) -> list[EnvioMoeda]:
    return list(
        db.scalars(
            select(EnvioMoeda)
            .where(EnvioMoeda.aluno_id == student_id)
            .options(joinedload(EnvioMoeda.professor), joinedload(EnvioMoeda.aluno))
            .order_by(EnvioMoeda.data.desc(), EnvioMoeda.id.desc())
        )
    )


def list_redemptions(db: Session, student_id: int) -> list[TrocaVantagem]:
    return list(
        db.scalars(
            select(TrocaVantagem)
            .where(TrocaVantagem.aluno_id == student_id)
            .options(joinedload(TrocaVantagem.aluno), joinedload(TrocaVantagem.vantagem))
            .order_by(TrocaVantagem.data.desc(), TrocaVantagem.id.desc())
        )
    )


def list_advantages(db: Session) -> list[Vantagem]:
    return list(
        db.scalars(select(Vantagem).options(joinedload(Vantagem.empresa)).order_by(Vantagem.id))
    )


def find_advantage(db: Session, advantage_id: int) -> Vantagem | None:
    return db.get(Vantagem, advantage_id)


def advantage_has_redemptions(db: Session, advantage_id: int) -> bool:
    return (
        db.scalar(select(TrocaVantagem.id).where(TrocaVantagem.vantagem_id == advantage_id).limit(1))
        is not None
    )


def find_redemption_of_company(db: Session, code: str, company_id: int) -> TrocaVantagem | None:
    return db.scalar(
        select(TrocaVantagem)
        .join(Vantagem)
        .where(TrocaVantagem.codigo == code, Vantagem.empresa_id == company_id)
        .options(joinedload(TrocaVantagem.aluno), joinedload(TrocaVantagem.vantagem))
    )
