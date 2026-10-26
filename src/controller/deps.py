import hmac

from fastapi import Cookie, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.model.entities import Aluno, EmpresaParceira, Professor, Usuario
from src.service.auth import create_session_token, password_fingerprint, read_session_token
from src.settings import settings

SESSION_COOKIE = "session"


def set_session_cookie(response: Response, user: Usuario) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user.id, user.tipo, user.senha_hash),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
        max_age=settings.session_hours * 3600,
    )


def current_user(
    session: str | None = Cookie(default=None), db: Session = Depends(get_db)
) -> Usuario:
    if not session:
        raise HTTPException(status_code=401, detail="Faça login para continuar.")
    data = read_session_token(session)
    user = db.get(Usuario, data["id"]) if data else None
    # O fingerprint muda quando a senha muda, derrubando as sessões emitidas antes da troca.
    if user is None or data.get("pv") != password_fingerprint(user.senha_hash):
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")
    return user


def _require(user: Usuario, expected: type, detail: str):
    if not isinstance(user, expected):
        raise HTTPException(status_code=403, detail=detail)
    return user


def current_student(user: Usuario = Depends(current_user)) -> Aluno:
    return _require(user, Aluno, "Acesso permitido apenas para alunos.")


def current_professor(user: Usuario = Depends(current_user)) -> Professor:
    return _require(user, Professor, "Acesso permitido apenas para professores.")


def current_company(user: Usuario = Depends(current_user)) -> EmpresaParceira:
    return _require(user, EmpresaParceira, "Acesso permitido apenas para empresas parceiras.")


def require_owner(user: Usuario, resource_id: int) -> None:
    if user.id != resource_id:
        raise HTTPException(status_code=403, detail="Você só pode acessar o seu próprio cadastro.")


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not settings.admin_token:
        raise HTTPException(status_code=403, detail="Área administrativa desativada (defina ADMIN_TOKEN).")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(status_code=403, detail="Token administrativo inválido.")
