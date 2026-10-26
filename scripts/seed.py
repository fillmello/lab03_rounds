"""Popula o banco com dados de demonstração (idempotente). Uso: python scripts/seed.py"""
import struct
import sys
import uuid
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import SessionLocal, create_tables  # noqa: E402
from src.model.entities import Aluno, InstituicaoEnsino, Usuario, Vantagem  # noqa: E402
from src.model.schemas import AlunoCreate, EmpresaCreate, ProfessorCreate  # noqa: E402
from src.service import fotos, moedas, usuarios  # noqa: E402

SENHA = "senha1234"


def cpf(seed: int) -> str:
    digits = [int(c) for c in f"{seed:09d}"]
    for size in (9, 10):
        total = sum(d * w for d, w in zip(digits, range(size + 1, 1, -1)))
        digits.append((total * 10 % 11) % 10)
    return "".join(map(str, digits))


def cnpj(seed: int) -> str:
    digits = [int(c) for c in f"{seed:08d}0001"]
    for weights in ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]):
        rest = sum(d * w for d, w in zip(digits, weights)) % 11
        digits.append(0 if rest < 2 else 11 - rest)
    return "".join(map(str, digits))


def png(color: tuple[int, int, int], size: int = 240) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    row = b"\x00" + bytes(color) * size
    raw = zlib.compress(row * size)
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")


def exists(db, login: str) -> bool:
    return db.query(Usuario).filter_by(login=login).first() is not None


def main() -> None:
    create_tables()
    with SessionLocal() as db:
        if db.query(InstituicaoEnsino).count() == 0:
            print("Inicie a API uma vez para criar as instituições e rode o seed de novo.")
            return
        ufmg, unifesp = [i.id for i in db.query(InstituicaoEnsino).order_by(InstituicaoEnsino.id).limit(2)]

        for n, (nome, login, dep, inst) in enumerate([
            ("Ana Beatriz Lima", "prof.ana", "Computação", ufmg),
            ("Carlos Eduardo Rocha", "prof.carlos", "Matemática", ufmg),
            ("Helena Duarte", "prof.helena", "Física", unifesp),
        ], start=1):
            if not exists(db, login):
                usuarios.register_professor(db, ProfessorCreate(
                    nome=nome, email=f"{login}@moeda.local", login=login, senha=SENHA,
                    cpf=cpf(700 + n), departamento=dep, instituicao_id=inst))

        for n, (nome, login, curso, inst) in enumerate([
            ("Lucas Martins", "lucas", "Engenharia de Software", ufmg),
            ("Mariana Costa", "mariana", "Ciência da Computação", ufmg),
            ("Pedro Henrique Alves", "pedro", "Sistemas de Informação", ufmg),
            ("Julia Fernandes", "julia", "Matemática", ufmg),
            ("Rafael Nogueira", "rafael", "Física", unifesp),
        ], start=1):
            if not exists(db, login):
                usuarios.register_student(db, AlunoCreate(
                    nome=nome, email=f"{login}@moeda.local", login=login, senha=SENHA, cpf=cpf(800 + n),
                    rg=f"MG-1{n}.234.567", endereco=f"Rua das Flores, {100 + n}", curso=curso, instituicao_id=inst))

        for n, (nome, login) in enumerate([("Restaurante Sabor Mineiro", "sabor"), ("Livraria Página Viva", "livraria")], start=1):
            if not exists(db, login):
                usuarios.register_company(db, EmpresaCreate(
                    nome=nome, email=f"{login}@moeda.local", login=login, senha=SENHA, cnpj=cnpj(900 + n)))

        companies = {u.login: u for u in db.query(Usuario).filter(Usuario.login.in_(["sabor", "livraria"]))}
        offers = [
            ("sabor", "Desconto de 15% no almoço", 60, (214, 120, 60)),
            ("sabor", "Sobremesa grátis", 30, (200, 80, 110)),
            ("livraria", "Caderno universitário", 40, (60, 110, 170)),
            ("livraria", "20% em livros técnicos", 120, (55, 107, 76)),
        ]
        for login, descricao, custo, color in offers:
            company = companies.get(login)
            if company and not db.query(Vantagem).filter_by(empresa_id=company.id, descricao=descricao).first():
                name = f"{uuid.uuid4().hex}.png"
                (fotos.upload_dir() / name).write_bytes(png(color))
                db.add(Vantagem(descricao=descricao, custo_em_moedas=custo, foto=name, empresa_id=company.id))
        db.commit()

        # Movimentações só na primeira execução (alunos ainda sem saldo nem histórico).
        ana = db.query(Usuario).filter_by(login="prof.ana").first()
        carlos = db.query(Usuario).filter_by(login="prof.carlos").first()
        students = {a.login: a for a in db.query(Aluno)}
        if ana and carlos and students["lucas"].saldo == 0 and not moedas_sent(db):
            for prof, login, qtd, motivo in [
                (ana, "lucas", 150, "Excelente participação nas aulas de Engenharia de Software"),
                (ana, "mariana", 100, "Ajudou os colegas no laboratório"),
                (carlos, "lucas", 80, "Melhor nota da prova de Cálculo"),
                (carlos, "pedro", 50, "Entregou todos os exercícios no prazo"),
            ]:
                moedas.send_coins(db, prof, students[login].id, qtd, motivo)
            advantage = db.query(Vantagem).filter_by(descricao="Sobremesa grátis").first()
            moedas.redeem_advantage(db, students["lucas"], advantage.id)
    print("Seed concluído.")


def moedas_sent(db) -> bool:
    from src.model.entities import EnvioMoeda
    return db.query(EnvioMoeda).first() is not None


if __name__ == "__main__":
    main()
