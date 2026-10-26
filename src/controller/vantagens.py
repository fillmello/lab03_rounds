from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.controller.deps import current_company, current_student, current_user
from src.database import get_db
from src.model.entities import Aluno, EmpresaParceira, TrocaVantagem, Usuario, Vantagem
from src.model.schemas import ResgateResponse, TrocaResponse, VantagemResponse
from src.repository.repositories import (
    advantage_has_redemptions,
    find_advantage,
    find_redemption_of_company,
    list_advantages,
)
from src.service import fotos, moedas, notificacao
from src.service.errors import ServiceError

router = APIRouter()

Description = Form(min_length=1, max_length=2000)
Cost = Form(gt=0)


def _clean_description(value: str) -> str:
    value = value.strip()
    if not value:
        raise ServiceError(422, "A descrição é obrigatória.")
    return value


def _own_advantage(db: Session, advantage_id: int, company: EmpresaParceira, detail: str) -> Vantagem:
    advantage = find_advantage(db, advantage_id)
    if advantage is None:
        raise HTTPException(status_code=404, detail="Vantagem não encontrada.")
    if advantage.empresa_id != company.id:
        raise HTTPException(status_code=403, detail=detail)
    return advantage


@router.post("/vantagens", response_model=VantagemResponse, status_code=201)
def create_advantage(
    descricao: str = Description,
    custo_em_moedas: int = Cost,
    foto: UploadFile = File(),
    company: EmpresaParceira = Depends(current_company),
    db: Session = Depends(get_db),
) -> Vantagem:
    advantage = Vantagem(
        descricao=_clean_description(descricao),
        custo_em_moedas=custo_em_moedas,
        foto=fotos.save_photo(foto),
        empresa_id=company.id,
    )
    db.add(advantage)
    db.commit()
    db.refresh(advantage)
    return advantage


@router.get("/vantagens", response_model=list[VantagemResponse])
def get_advantages(
    user: Usuario = Depends(current_user), db: Session = Depends(get_db)
) -> list[Vantagem]:
    if not isinstance(user, (Aluno, EmpresaParceira)):
        raise HTTPException(status_code=403, detail="Perfil sem permissão para esta operação.")
    return list_advantages(db)


@router.get("/vantagens/{advantage_id}", response_model=VantagemResponse)
def get_advantage(
    advantage_id: int, user: Usuario = Depends(current_user), db: Session = Depends(get_db)
) -> Vantagem:
    if not isinstance(user, (Aluno, EmpresaParceira)):
        raise HTTPException(status_code=403, detail="Perfil sem permissão para esta operação.")
    advantage = find_advantage(db, advantage_id)
    if advantage is None:
        raise HTTPException(status_code=404, detail="Vantagem não encontrada.")
    return advantage


@router.put("/vantagens/{advantage_id}", response_model=VantagemResponse)
def update_advantage(
    advantage_id: int,
    descricao: str = Description,
    custo_em_moedas: int = Cost,
    foto: UploadFile | None = File(default=None),
    company: EmpresaParceira = Depends(current_company),
    db: Session = Depends(get_db),
) -> Vantagem:
    advantage = _own_advantage(db, advantage_id, company, "Você só pode alterar suas vantagens.")
    advantage.descricao = _clean_description(descricao)
    advantage.custo_em_moedas = custo_em_moedas
    old_photo = advantage.foto
    if foto is not None and foto.filename:
        advantage.foto = fotos.save_photo(foto)
    db.commit()
    if advantage.foto != old_photo:
        fotos.delete_photo(old_photo)
    db.refresh(advantage)
    return advantage


@router.delete("/vantagens/{advantage_id}", status_code=204)
def delete_advantage(
    advantage_id: int,
    company: EmpresaParceira = Depends(current_company),
    db: Session = Depends(get_db),
) -> None:
    advantage = _own_advantage(db, advantage_id, company, "Você só pode remover suas vantagens.")
    if advantage_has_redemptions(db, advantage_id):
        raise HTTPException(status_code=409, detail="Vantagem já possui resgates.")
    photo = advantage.foto
    db.delete(advantage)
    db.commit()
    fotos.delete_photo(photo)


@router.post("/vantagens/{advantage_id}/resgatar", response_model=ResgateResponse, status_code=201)
@router.post("/vantagens/{advantage_id}/trocar", response_model=ResgateResponse,
             status_code=201, include_in_schema=False)
def redeem_advantage(
    advantage_id: int,
    background: BackgroundTasks,
    student: Aluno = Depends(current_student),
    db: Session = Depends(get_db),
) -> ResgateResponse:
    redemption, advantage = moedas.redeem_advantage(db, student, advantage_id)
    company = advantage.empresa
    # Mesmo código nos dois e-mails, para facilitar a conferência presencial.
    background.add_task(
        notificacao.send_email,
        notificacao.cupom_aluno(student.email, student.nome, advantage.descricao, company.nome, redemption.codigo),
    )
    background.add_task(
        notificacao.send_email,
        notificacao.cupom_parceiro(company.email, company.nome, advantage.descricao, student.nome, redemption.codigo),
    )
    return ResgateResponse(
        codigo=redemption.codigo,
        quantidade=redemption.quantidade,
        vantagem_id=redemption.vantagem_id,
        saldo_restante=student.saldo,
    )


@router.get("/trocas/{codigo}", response_model=TrocaResponse)
def check_redemption(
    codigo: str, company: EmpresaParceira = Depends(current_company), db: Session = Depends(get_db)
) -> TrocaVantagem:
    redemption = find_redemption_of_company(db, codigo.strip().upper(), company.id)
    if redemption is None:
        raise HTTPException(status_code=404, detail="Cupom não encontrado.")
    return redemption
