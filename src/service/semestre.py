from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.model.entities import Professor

CREDITO_SEMESTRAL = 1000


def current_semester() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year}-{'1' if now.month <= 6 else '2'}"


def credit_if_due(professor: Professor) -> bool:
    """Soma as 1.000 moedas do semestre uma única vez, acumulando o saldo restante."""
    semester = current_semester()
    if professor.ultimo_credito_semestre == semester:
        return False
    professor.saldo += CREDITO_SEMESTRAL
    professor.ultimo_credito_semestre = semester
    return True


def credit_all_due(db: Session) -> None:
    for professor in db.query(Professor).all():
        credit_if_due(professor)
    db.commit()


def ensure_credited(db: Session, professor: Professor) -> None:
    if credit_if_due(professor):
        db.commit()
