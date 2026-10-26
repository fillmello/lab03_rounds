from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.routes import router
from src.database import SessionLocal, create_tables
from src.model.entities import InstituicaoEnsino
from src.model.entities import Professor
from src.service.auth import hash_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    with SessionLocal() as db:
        if db.query(InstituicaoEnsino).count() == 0:
            db.add_all(
                [
                    InstituicaoEnsino(nome="Universidade Federal de Minas Gerais"),
                    InstituicaoEnsino(nome="Universidade Federal de São Paulo"),
                    InstituicaoEnsino(nome="Instituto Federal de Educação"),
                ]
            )
            db.commit()
        # A conta institucional é criada uma única vez e mantém o saldo
        # acumulável entre reinícios da aplicação.
        if db.query(Professor).count() == 0:
            institution = db.query(InstituicaoEnsino).order_by(InstituicaoEnsino.id).first()
            db.add(
                Professor(
                    nome="Professor Institucional",
                    email="professor@moeda.local",
                    login="professor",
                    senha_hash=hash_password("professor123"),
                    cpf="11111111112",
                    departamento="Geral",
                    instituicao_id=institution.id,
                    saldo=1000,
                    ultimo_credito_semestre=f"{datetime.utcnow().year}-{'1' if datetime.utcnow().month <= 6 else '2'}",
                )
            )
            db.commit()
        else:
            semester = f"{datetime.utcnow().year}-{'1' if datetime.utcnow().month <= 6 else '2'}"
            for professor in db.query(Professor).all():
                if professor.ultimo_credito_semestre != semester:
                    professor.saldo += 1000
                    professor.ultimo_credito_semestre = semester
            db.commit()
    yield


app = FastAPI(title="Sistema de Moeda Estudantil", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
