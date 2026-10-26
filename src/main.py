from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.controller import router
from src.controller.validation import validation_error_handler
from src.database import SessionLocal, create_tables
from src.model.entities import InstituicaoEnsino, Professor
from src.service import fotos, semestre
from src.service.auth import hash_password
from src.service.errors import ServiceError
from src.settings import settings


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
        # Professor de demonstração, criado uma única vez (o saldo acumula entre reinícios).
        if db.query(Professor).count() == 0:
            institution = db.query(InstituicaoEnsino).order_by(InstituicaoEnsino.id).first()
            professor = Professor(
                nome="Professor Institucional",
                email="professor@moeda.local",
                login="professor",
                senha_hash=hash_password("professor123"),
                cpf="52998224725",
                departamento="Geral",
                instituicao_id=institution.id,
                saldo=0,
            )
            semestre.credit_if_due(professor)
            db.add(professor)
            db.commit()
        else:
            semestre.credit_all_due(db)
    yield


app = FastAPI(title="Sistema de Moeda Estudantil", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(router, prefix="/api")
app.mount("/uploads", StaticFiles(directory=fotos.upload_dir()), name="uploads")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
