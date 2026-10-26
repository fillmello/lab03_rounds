from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from src.controller.deps import current_professor, current_student
from src.database import get_db
from src.model.entities import Aluno, EnvioMoeda, Professor
from src.model.schemas import EnvioMoedaCreate, EnvioMoedaResponse, ExtratoResponse
from src.repository.repositories import list_received_coins, list_redemptions, list_sent_coins
from src.service import moedas, notificacao, semestre

router = APIRouter()


@router.post("/moedas/enviar", response_model=EnvioMoedaResponse, status_code=201)
@router.post("/envios", response_model=EnvioMoedaResponse, status_code=201, include_in_schema=False)
def send_coins(
    payload: EnvioMoedaCreate,
    background: BackgroundTasks,
    professor: Professor = Depends(current_professor),
    db: Session = Depends(get_db),
) -> EnvioMoeda:
    shipment, student = moedas.send_coins(db, professor, payload.aluno_id, payload.quantidade, payload.motivo)
    background.add_task(
        notificacao.send_email,
        notificacao.moeda_recebida(student.email, student.nome, professor.nome, shipment.quantidade, shipment.motivo),
    )
    return shipment


@router.get("/extratos/professor", response_model=ExtratoResponse)
@router.get("/extrato/professor", response_model=ExtratoResponse, include_in_schema=False)
def professor_statement(
    professor: Professor = Depends(current_professor), db: Session = Depends(get_db)
) -> ExtratoResponse:
    semestre.ensure_credited(db, professor)
    return ExtratoResponse(saldo=professor.saldo, envios=list_sent_coins(db, professor.id))


@router.get("/extratos/aluno", response_model=ExtratoResponse)
@router.get("/extrato/aluno", response_model=ExtratoResponse, include_in_schema=False)
def student_statement(
    student: Aluno = Depends(current_student), db: Session = Depends(get_db)
) -> ExtratoResponse:
    return ExtratoResponse(
        saldo=student.saldo,
        envios=list_received_coins(db, student.id),
        trocas=list_redemptions(db, student.id),
    )
