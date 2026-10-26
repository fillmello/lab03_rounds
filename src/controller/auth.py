from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.controller.deps import SESSION_COOKIE, current_user, set_session_cookie
from src.database import get_db
from src.model.entities import Usuario
from src.model.schemas import InstituicaoResponse, LoginRequest, LoginResponse, PasswordChange
from src.repository.repositories import list_institutions
from src.service import usuarios

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    user = usuarios.authenticate(db, payload.login, payload.senha)
    set_session_cookie(response, user)
    return LoginResponse(id=user.id, nome=user.nome, tipo=user.tipo)


@router.get("/me", response_model=LoginResponse)
def get_current_user(user: Usuario = Depends(current_user)) -> LoginResponse:
    return LoginResponse(id=user.id, nome=user.nome, tipo=user.tipo)


@router.post("/me/senha", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: PasswordChange,
    response: Response,
    user: Usuario = Depends(current_user),
    db: Session = Depends(get_db),
) -> None:
    usuarios.change_password(db, user, payload)
    # A sessão atual segue válida com o novo fingerprint; as demais são derrubadas.
    set_session_cookie(response, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/instituicoes", response_model=list[InstituicaoResponse])
def get_institutions(db: Session = Depends(get_db)):
    return list_institutions(db)
