import hashlib

from sqlalchemy import update

from src.database import SessionLocal
from src.model.entities import Usuario
from src.service import throttle
from tests.conftest import login

CHANGE = "/api/me/senha"


def body(atual="senha-forte-1", nova="nova-senha-2", confirmacao=None):
    return {"senha_atual": atual, "nova_senha": nova, "confirmacao": confirmacao or nova}


def test_troca_com_sucesso_devolve_204_e_permite_login_com_a_nova_senha(client, make_student):
    student = make_student()
    login(client, student)
    response = client.post(CHANGE, json=body())
    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/api/me").status_code == 200  # a sessão atual continua válida
    client.post("/api/logout")
    assert client.post("/api/login", json={"login": student["login"], "senha": "senha-forte-1"}).status_code == 401
    assert client.post("/api/login", json={"login": student["login"], "senha": "nova-senha-2"}).status_code == 200


def test_senha_atual_incorreta(client, make_student):
    login(client, make_student())
    response = client.post(CHANGE, json=body(atual="errada-errada"))
    assert response.status_code == 400
    assert "atual" in response.json()["detail"]


def test_confirmacao_divergente(client, make_student):
    login(client, make_student())
    response = client.post(CHANGE, json=body(confirmacao="outra-coisa-9"))
    assert response.status_code == 400
    assert "confirmação" in response.json()["detail"]


def test_nova_senha_igual_a_atual(client, make_student):
    login(client, make_student())
    response = client.post(CHANGE, json=body(nova="senha-forte-1"))
    assert response.status_code == 400
    assert "diferente" in response.json()["detail"]


def test_nova_senha_fraca(client, make_student):
    login(client, make_student())
    assert client.post(CHANGE, json=body(nova="curta")).status_code == 422


def test_cadastro_exige_senha_com_8_caracteres(client):
    response = client.post("/api/alunos", json={
        "nome": "X", "email": "x@mail.com", "login": "x", "senha": "1234567", "cpf": "52998224725",
        "rg": "1", "endereco": "r", "curso": "c", "instituicao_id": 1,
    })
    assert response.status_code == 422


def test_troca_exige_login(client):
    assert client.post(CHANGE, json=body()).status_code == 401


def test_outra_sessao_e_invalidada_apos_a_troca(client, new_client, make_student):
    student = make_student()
    login(client, student)
    other = login(new_client(), student)
    assert other.get("/api/me").status_code == 200
    assert client.post(CHANGE, json=body()).status_code == 204
    assert other.get("/api/me").status_code == 401


def test_hash_legado_sha256_e_migrado_no_login(client, make_student):
    student = make_student()
    legacy = hashlib.sha256(student["senha"].encode()).hexdigest()
    with SessionLocal() as db:
        db.execute(update(Usuario).where(Usuario.id == student["id"]).values(senha_hash=legacy))
        db.commit()
    login(client, student)
    with SessionLocal() as db:
        assert db.get(Usuario, student["id"]).senha_hash.startswith("pbkdf2_sha256$")


def test_senha_nao_e_guardada_em_texto_nem_sha256_puro(client, make_student):
    student = make_student()
    with SessionLocal() as db:
        stored = db.get(Usuario, student["id"]).senha_hash
    assert student["senha"] not in stored
    assert stored != hashlib.sha256(student["senha"].encode()).hexdigest()


def test_bloqueio_apos_tentativas_erradas_na_troca(client, make_student):
    login(client, make_student())
    for _ in range(throttle.MAX_FAILURES):
        assert client.post(CHANGE, json=body(atual="errada-errada")).status_code == 400
    assert client.post(CHANGE, json=body(atual="errada-errada")).status_code == 429
    assert client.post(CHANGE, json=body()).status_code == 429  # nem a senha certa passa durante o bloqueio


def test_bloqueio_apos_tentativas_erradas_no_login(client, make_student):
    student = make_student()
    for _ in range(throttle.MAX_FAILURES):
        assert client.post("/api/login", json={"login": student["login"], "senha": "errada"}).status_code == 401
    assert client.post("/api/login", json={"login": student["login"], "senha": student["senha"]}).status_code == 429


def test_cookie_adulterado_e_recusado(client, make_student):
    login(client, make_student())
    token = client.cookies["session"]
    client.cookies.set("session", token[:-2] + "ab")
    assert client.get("/api/me").status_code == 401


def test_erros_de_validacao_vem_em_portugues(client, make_student):
    login(client, make_student())
    detail = client.post(CHANGE, json=body(nova="curta")).json()["detail"]
    assert detail == "Nova senha deve ter no mínimo 8 caracteres."
