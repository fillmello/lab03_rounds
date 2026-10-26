import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _digits(value: str | None, field_name: str, length: int) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"\D", "", value)
    if len(normalized) != length or len(set(normalized)) == 1:
        raise ValueError(f"{field_name} deve conter {length} dígitos válidos.")
    return normalized


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
    senha: NonEmptyString
    cpf: str
    rg: NonEmptyString = Field(max_length=20)
    endereco: NonEmptyString = Field(max_length=255)
    curso: NonEmptyString = Field(max_length=120)
    instituicao_id: int

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(
        lambda value: _digits(value, "CPF", 11)
    )


class AlunoUpdate(BaseModel):
    nome: NonEmptyString | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    login: NonEmptyString | None = Field(default=None, max_length=150)
    senha: NonEmptyString | None = None
    cpf: str | None = None
    rg: NonEmptyString | None = Field(default=None, max_length=20)
    endereco: NonEmptyString | None = Field(default=None, max_length=255)
    curso: NonEmptyString | None = Field(default=None, max_length=120)
    instituicao_id: int | None = None

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(
        lambda value: _digits(value, "CPF", 11)
    )


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


class EmpresaCreate(BaseModel):
    nome: NonEmptyString = Field(max_length=120)
    email: str = Field(min_length=3, max_length=254)
    login: NonEmptyString = Field(max_length=150)
    senha: NonEmptyString
    cnpj: str

    _validate_email = field_validator("email")(_email)
    _validate_cnpj = field_validator("cnpj")(
        lambda value: _digits(value, "CNPJ", 14)
    )


class EmpresaUpdate(BaseModel):
    nome: NonEmptyString | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    login: NonEmptyString | None = Field(default=None, max_length=150)
    senha: NonEmptyString | None = None
    cnpj: str | None = None

    _validate_email = field_validator("email")(_email)
    _validate_cnpj = field_validator("cnpj")(
        lambda value: _digits(value, "CNPJ", 14)
    )


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
    senha_atual: NonEmptyString
    nova_senha: NonEmptyString
    confirmacao: NonEmptyString


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
    senha: NonEmptyString
    cpf: str
    departamento: NonEmptyString = Field(max_length=120)
    instituicao_id: int

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(
        lambda value: _digits(value, "CPF", 11)
    )


class ProfessorUpdate(BaseModel):
    nome: NonEmptyString | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    login: NonEmptyString | None = Field(default=None, max_length=150)
    cpf: str | None = None
    departamento: NonEmptyString | None = Field(default=None, max_length=120)
    instituicao_id: int | None = None

    _validate_email = field_validator("email")(_email)
    _validate_cpf = field_validator("cpf")(
        lambda value: _digits(value, "CPF", 11)
    )


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
    aluno_id: int


class ExtratoResponse(BaseModel):
    saldo: int
    envios: list[EnvioMoedaResponse] = Field(default_factory=list)
    trocas: list["TrocaResponse"] = Field(default_factory=list)


class VantagemCreate(BaseModel):
    descricao: NonEmptyString = Field(max_length=2000)
    custo_em_moedas: int = Field(gt=0)


class VantagemResponse(VantagemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa_id: int


class TrocaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: datetime
    quantidade: int
    codigo: str
    aluno_id: int
    vantagem_id: int


class ResgateResponse(BaseModel):
    codigo: str
    quantidade: int
    vantagem_id: int
    saldo_restante: int
