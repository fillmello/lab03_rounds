import os
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="moeda-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp, 'test.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(Path(_tmp, "uploads"))
os.environ["ADMIN_TOKEN"] = "token-de-teste"
os.environ["PASSWORD_ITERATIONS"] = "1000"
os.environ["MAIL_HOST"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.database import Base, engine  # noqa: E402
from src.main import app  # noqa: E402
from src.service import notificacao, throttle  # noqa: E402

ADMIN = {"X-Admin-Token": "token-de-teste"}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def _check_digit(digits: list[int], weights: list[int]) -> int:
    rest = sum(d * w for d, w in zip(digits, weights)) % 11
    return 0 if rest < 2 else 11 - rest


def make_cpf(seed: int) -> str:
    digits = [int(c) for c in f"{seed:09d}"]
    for size in (9, 10):
        total = sum(d * w for d, w in zip(digits, range(size + 1, 1, -1)))
        digits.append((total * 10 % 11) % 10)
    return "".join(map(str, digits))


def make_cnpj(seed: int) -> str:
    digits = [int(c) for c in f"{seed:08d}0001"]
    digits.append(_check_digit(digits, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]))
    digits.append(_check_digit(digits, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]))
    return "".join(map(str, digits))


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(notificacao, "send_email", sent.append)
    return sent


@pytest.fixture
def client(outbox):
    Base.metadata.drop_all(bind=engine)
    throttle.clear_all()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def new_client(client):
    """Cliente extra, com cookies próprios (outra sessão)."""
    return lambda: TestClient(app)


_counter = iter(range(1, 10_000))


@pytest.fixture
def make_student(client):
    def _make(**overrides):
        n = next(_counter)
        payload = {
            "nome": f"Aluno {n}", "email": f"aluno{n}@mail.com", "login": f"aluno{n}",
            "senha": "senha-forte-1", "cpf": make_cpf(100_000 + n), "rg": "MG123",
            "endereco": "Rua A, 1", "curso": "Engenharia", "instituicao_id": 1,
        } | overrides
        response = client.post("/api/alunos", json=payload)
        assert response.status_code == 201, response.text
        return payload | response.json()
    return _make


@pytest.fixture
def make_company(client):
    def _make(**overrides):
        n = next(_counter)
        payload = {
            "nome": f"Empresa {n}", "email": f"empresa{n}@mail.com", "login": f"empresa{n}",
            "senha": "senha-forte-1", "cnpj": make_cnpj(10_000 + n),
        } | overrides
        response = client.post("/api/empresas", json=payload)
        assert response.status_code == 201, response.text
        return payload | response.json()
    return _make


@pytest.fixture
def make_professor(client):
    def _make(**overrides):
        n = next(_counter)
        payload = {
            "nome": f"Professor {n}", "email": f"prof{n}@mail.com", "login": f"prof{n}",
            "senha": "senha-forte-1", "cpf": make_cpf(500_000 + n),
            "departamento": "Computação", "instituicao_id": 1,
        } | overrides
        response = client.post("/api/admin/professores", json=payload, headers=ADMIN)
        assert response.status_code == 201, response.text
        return payload | response.json()
    return _make


def login(client, user, password=None):
    response = client.post("/api/login", json={"login": user["login"], "senha": password or user["senha"]})
    assert response.status_code == 200, response.text
    return client
