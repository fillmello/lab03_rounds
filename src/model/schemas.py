import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
# Senhas não passam por strip: o que o usuário digita no cadastro é o que digita no login.
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]


def _cpf_is_valid(digits: str) -> bool:
    for size in (9, 10):
        total = sum(int(d) * w for d, w in zip(digits[:size], range(size + 1, 1, -1)))
        if int(digits[size]) != (total * 10 % 11) % 10:
            return False
    return True


def _cnpj_is_valid(digits: str) -> bool:
    for size, weights in ((12, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]), (13, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])):
        total = sum(int(d) * w for d, w in zip(digits[:size], weights))
        rest = total % 11
        if int(digits[size]) != (0 if rest < 2 else 11 - rest):
            return False
    return True


def _document(value: str | None, field_name: str, length: int, checker) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\D", "", value)
    if len(normalized) != length or len(set(normalized)) == 1 or not checker(normalized):
        raise ValueError(f"{field_name} inválido.")
    return normalized


def _cpf(value: str | None) -> str | None:
    return _document(value, "CPF", 11, _cpf_is_valid)


def _cnpj(value: str | None) -> str | None:
    return _document(value, "CNPJ", 14, _cnpj_is_valid)


def _email(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        raise ValueError("E-mail inválido.")
    return value


class InstituicaoCreate(BaseModel):
    nome: NonEmptyString = Field(max_length=150)


class InstituicaoResponse(InstituicaoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AlunoCreate(BaseModel):
    nome: NonEmptyString = Field(max_length=120)
    email: str = Field(min_length=3, max_length=254)
    login: NonEmptyString = Field(max_length=150)
    senha: Password
    cpf: str
    rg: NonEmptyString = Field(max_length=20)
    endereco: NonEmptyString = Field(max_length=255)
    curso: NonEmptyString = Field(max_length=120)
    instituicao_id: int

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(_cpf)


class AlunoUpdate(BaseModel):
    nome: NonEmptyString | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    login: NonEmptyString | None = Field(default=None, max_length=150)
    # Aceito só para devolver uma mensagem clara; a senha muda em /me/senha.
    senha: str | None = None
    cpf: str | None = None
    rg: NonEmptyString | None = Field(default=None, max_length=20)
    endereco: NonEmptyString | None = Field(default=None, max_length=255)
    curso: NonEmptyString | None = Field(default=None, max_length=120)
    instituicao_id: int | None = None

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(_cpf)


class AlunoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    login: str
    cpf: str
    rg: str
    endereco: str
    curso: str
    instituicao_id: int
    saldo: int


class AlunoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    curso: str


class EmpresaCreate(BaseModel):
    nome: NonEmptyString = Field(max_length=120)
    email: str = Field(min_length=3, max_length=254)
    login: NonEmptyString = Field(max_length=150)
    senha: Password
    cnpj: str

    _validate_email = field_validator("email")(_email)
    _validate_cnpj = field_validator("cnpj")(_cnpj)


class EmpresaUpdate(BaseModel):
    nome: NonEmptyString | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    login: NonEmptyString | None = Field(default=None, max_length=150)
    senha: str | None = None
    cnpj: str | None = None

    _validate_email = field_validator("email")(_email)
    _validate_cnpj = field_validator("cnpj")(_cnpj)


class EmpresaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    login: str
    cnpj: str


class LoginRequest(BaseModel):
    login: str = Field(min_length=1)
    senha: str = Field(min_length=1)


class LoginResponse(BaseModel):
    id: int
    nome: str
    tipo: str


class PasswordChange(BaseModel):
    senha_atual: str = Field(min_length=1)
    nova_senha: Password
    confirmacao: str = Field(min_length=1)


class ProfessorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    login: str
    cpf: str
    departamento: str
    instituicao_id: int
    saldo: int


class ProfessorCreate(BaseModel):
    nome: NonEmptyString = Field(max_length=120)
    email: str = Field(min_length=3, max_length=254)
    login: NonEmptyString = Field(max_length=150)
    senha: Password
    cpf: str
    departamento: NonEmptyString = Field(max_length=120)
    instituicao_id: int

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(_cpf)


class ProfessorBulkCreate(BaseModel):
    professores: list[ProfessorCreate] = Field(min_length=1, max_length=500)


class ProfessorUpdate(BaseModel):
    nome: NonEmptyString | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    login: NonEmptyString | None = Field(default=None, max_length=150)
    cpf: str | None = None
    departamento: NonEmptyString | None = Field(default=None, max_length=120)
    instituicao_id: int | None = None

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(_cpf)


class EnvioMoedaCreate(BaseModel):
    aluno_id: int
    quantidade: int = Field(gt=0)
    motivo: NonEmptyString = Field(max_length=1000)


class EnvioMoedaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: datetime
    quantidade: int
    motivo: str
    professor_id: int
    professor_nome: str
    aluno_id: int
    aluno_nome: str


class TrocaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: datetime
    quantidade: int
    codigo: str
    aluno_id: int
    aluno_nome: str
    vantagem_id: int
    vantagem_descricao: str


class ExtratoResponse(BaseModel):
    saldo: int
    envios: list[EnvioMoedaResponse] = Field(default_factory=list)
    trocas: list[TrocaResponse] = Field(default_factory=list)


class VantagemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    descricao: str
    custo_em_moedas: int
    empresa_id: int
    empresa_nome: str
    foto_url: str | None


class ResgateResponse(BaseModel):
    codigo: str
    quantidade: int
    vantagem_id: int
    saldo_restante: int
