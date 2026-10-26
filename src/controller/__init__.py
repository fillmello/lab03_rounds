from fastapi import APIRouter

from src.controller import admin, alunos, auth, empresas, moedas, professores, vantagens

router = APIRouter()
for module in (auth, alunos, empresas, professores, moedas, vantagens, admin):
    router.include_router(module.router)
