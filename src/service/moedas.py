import secrets

from sqlalchemy.orm import Session

from src.model.entities import Aluno, EnvioMoeda, Professor, TrocaVantagem, Vantagem
from src.repository.repositories import find_advantage
from src.service import semestre
from src.service.errors import ServiceError

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _new_code() -> str:
    raw = "".join(secrets.choice(_CODE_ALPHABET) for _ in range(10))
    return f"{raw[:5]}-{raw[5:]}"


def send_coins(
    db: Session, professor: Professor, student_id: int, amount: int, reason: str
) -> tuple[EnvioMoeda, Aluno]:
    semestre.ensure_credited(db, professor)
    student = db.get(Aluno, student_id)
    if student is None:
        raise ServiceError(404, "Aluno não encontrado.")
    if professor.instituicao_id != student.instituicao_id:
        raise ServiceError(403, "Professor e aluno devem pertencer à mesma instituição.")
    if professor.saldo < amount:
        raise ServiceError(400, "Saldo insuficiente.")
    professor.saldo -= amount
    student.saldo += amount
    shipment = EnvioMoeda(quantidade=amount, motivo=reason, professor_id=professor.id, aluno_id=student.id)
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment, student


def redeem_advantage(db: Session, student: Aluno, advantage_id: int) -> tuple[TrocaVantagem, Vantagem]:
    advantage = find_advantage(db, advantage_id)
    if advantage is None:
        raise ServiceError(404, "Vantagem não encontrada.")
    if student.saldo < advantage.custo_em_moedas:
        raise ServiceError(400, "Saldo insuficiente.")
    student.saldo -= advantage.custo_em_moedas
    redemption = TrocaVantagem(
        quantidade=advantage.custo_em_moedas,
        codigo=_new_code(),
        aluno_id=student.id,
        vantagem_id=advantage.id,
    )
    db.add(redemption)
    db.commit()
    return redemption, advantage
