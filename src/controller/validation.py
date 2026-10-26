from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

LABELS = {
    "nome": "Nome", "email": "E-mail", "login": "Login", "senha": "Senha",
    "senha_atual": "Senha atual", "nova_senha": "Nova senha", "confirmacao": "Confirmação da nova senha",
    "cpf": "CPF", "cnpj": "CNPJ", "rg": "RG", "endereco": "Endereço", "curso": "Curso",
    "instituicao_id": "Instituição", "aluno_id": "Aluno", "quantidade": "Quantidade",
    "motivo": "Motivo", "descricao": "Descrição", "custo_em_moedas": "Custo em moedas",
    "foto": "Foto", "departamento": "Departamento", "professores": "Lista de professores",
}


def _label(loc: tuple) -> str:
    field = next((str(part) for part in reversed(loc) if isinstance(part, str) and part in LABELS), None)
    return LABELS.get(field, "Campo")


def _message(error: dict) -> str:
    label, ctx = _label(error["loc"]), error.get("ctx", {})
    match error["type"]:
        case "missing":
            return f"{label} é obrigatório."
        case "string_too_short" if ctx.get("min_length", 1) > 1:
            return f"{label} deve ter no mínimo {ctx['min_length']} caracteres."
        case "string_too_short":
            return f"{label} é obrigatório."
        case "string_too_long":
            return f"{label} deve ter no máximo {ctx['max_length']} caracteres."
        case "greater_than":
            return f"{label} deve ser maior que {ctx['gt']}."
        case "too_short":
            return f"{label} deve ter ao menos {ctx['min_length']} item(ns)."
        case "too_long":
            return f"{label} deve ter no máximo {ctx['max_length']} itens."
        case "value_error":
            return str(error["msg"]).removeprefix("Value error, ")
        case "int_parsing" | "int_type" | "float_parsing" | "bool_parsing":
            return f"{label} inválido."
        case _:
            return f"{label}: {error['msg']}"


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    messages = list(dict.fromkeys(_message(error) for error in exc.errors()))
    return JSONResponse(status_code=422, content={"detail": " ".join(messages)})
