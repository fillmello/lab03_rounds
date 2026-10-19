from pydantic import BaseModel, ConfigDict, Field


class InstituicaoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=150)


class InstituicaoResponse(InstituicaoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AlunoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    login: str = Field(min_length=1, max_length=150)
    senha: str = Field(min_length=1)
    cpf: str = Field(min_length=11, max_length=11)
    rg: str = Field(min_length=1, max_length=20)
    endereco: str = Field(min_length=1, max_length=255)
    curso: str = Field(min_length=1, max_length=120)
    instituicao_id: int


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
    nome: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    login: str = Field(min_length=1, max_length=150)
    senha: str = Field(min_length=1)
    cnpj: str = Field(min_length=14, max_length=14)


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
