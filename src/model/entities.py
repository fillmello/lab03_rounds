from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    login: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)

    __mapper_args__ = {"polymorphic_on": tipo, "polymorphic_identity": "usuario"}


class InstituicaoEnsino(Base):
    __tablename__ = "instituicao_ensino"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    alunos: Mapped[list["Aluno"]] = relationship(back_populates="instituicao")
    professores: Mapped[list["Professor"]] = relationship(back_populates="instituicao")


class Aluno(Usuario):
    __tablename__ = "aluno"

    id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), primary_key=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    rg: Mapped[str] = mapped_column(String(20), nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    curso: Mapped[str] = mapped_column(String(120), nullable=False)
    saldo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    instituicao_id: Mapped[int] = mapped_column(ForeignKey("instituicao_ensino.id"), nullable=False)

    instituicao: Mapped[InstituicaoEnsino] = relationship(back_populates="alunos")
    __mapper_args__ = {"polymorphic_identity": "aluno"}


class Professor(Usuario):
    __tablename__ = "professor"

    id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), primary_key=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    departamento: Mapped[str] = mapped_column(String(120), nullable=False)
    saldo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    instituicao_id: Mapped[int] = mapped_column(ForeignKey("instituicao_ensino.id"), nullable=False)

    instituicao: Mapped[InstituicaoEnsino] = relationship(back_populates="professores")
    __mapper_args__ = {"polymorphic_identity": "professor"}

    def creditar_semestre(self) -> None:
        self.saldo += 1000


class EmpresaParceira(Usuario):
    __tablename__ = "empresa_parceira"

    id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)

    vantagens: Mapped[list["Vantagem"]] = relationship(back_populates="empresa")
    __mapper_args__ = {"polymorphic_identity": "empresa_parceira"}


class Vantagem(Base):
    __tablename__ = "vantagem"

    id: Mapped[int] = mapped_column(primary_key=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    foto: Mapped[str] = mapped_column(String(255), nullable=False)
    custo_em_moedas: Mapped[int] = mapped_column(Integer, nullable=False)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa_parceira.id"), nullable=False)

    empresa: Mapped[EmpresaParceira] = relationship(back_populates="vantagens")


class EnvioMoeda(Base):
    __tablename__ = "envio_moeda"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    professor_id: Mapped[int] = mapped_column(ForeignKey("professor.id"), nullable=False)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("aluno.id"), nullable=False)


class TrocaVantagem(Base):
    __tablename__ = "troca_vantagem"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    codigo: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("aluno.id"), nullable=False)
    vantagem_id: Mapped[int] = mapped_column(ForeignKey("vantagem.id"), nullable=False)
