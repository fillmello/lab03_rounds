from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.routes import router
from src.database import SessionLocal, create_tables
from src.model.entities import InstituicaoEnsino


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
