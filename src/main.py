from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controller.routes import router
from src.database import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield


app = FastAPI(title="Sistema de Moeda Estudantil", version="1.0.0", lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
