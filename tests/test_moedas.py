from sqlalchemy import update

from src.database import SessionLocal
from src.model.entities import Professor
from tests.conftest import PNG, login

SEND = "/api/moedas/enviar"


def advantage(client, company, cost=50, descricao="Desconto de 10%"):
    login(client, company)
    response = client.post(
        "/api/vantagens",
        data={"descricao": descricao, "custo_em_moedas": str(cost)},
        files={"foto": ("foto.png", PNG, "image/png")},
    )
    assert response.status_code == 201, response.text
    client.post("/api/logout")
    return response.json()


def test_envio_debita_professor_credita_aluno_e_avisa_por_email(client, outbox, make_student, make_professor):
    student, professor = make_student(), make_professor()
    login(client, professor)
    response = client.post(SEND, json={"aluno_id": student["id"], "quantidade": 100, "motivo": "Boa participação"})
    assert response.status_code == 201
    assert client.get("/api/extratos/professor").json()["saldo"] == 900
    assert len(outbox) == 1
    assert outbox[0]["To"] == student["email"]
    assert "100" in outbox[0]["Subject"]
    client.post("/api/logout")
    login(client, student)
    statement = client.get("/api/extratos/aluno").json()
    assert statement["saldo"] == 100
    assert statement["envios"][0]["professor_nome"] == professor["nome"]


def test_envio_com_saldo_insuficiente(client, outbox, make_student, make_professor):
    student, professor = make_student(), make_professor()
    login(client, professor)
    response = client.post(SEND, json={"aluno_id": student["id"], "quantidade": 1001, "motivo": "x"})
    assert response.status_code == 400
    assert "insuficiente" in response.json()["detail"]
    assert outbox == []


def test_envio_exige_motivo(client, make_student, make_professor):
    student, professor = make_student(), make_professor()
    login(client, professor)
    for motivo in ("", "   "):
        assert client.post(SEND, json={"aluno_id": student["id"], "quantidade": 10, "motivo": motivo}).status_code == 422


def test_envio_exige_quantidade_positiva(client, make_student, make_professor):
    student, professor = make_student(), make_professor()
    login(client, professor)
    assert client.post(SEND, json={"aluno_id": student["id"], "quantidade": 0, "motivo": "x"}).status_code == 422


def test_envio_para_aluno_de_outra_instituicao(client, make_student, make_professor):
    student, professor = make_student(instituicao_id=2), make_professor(instituicao_id=1)
    login(client, professor)
    assert client.post(SEND, json={"aluno_id": student["id"], "quantidade": 10, "motivo": "x"}).status_code == 403


def test_somente_professor_envia_moedas(client, make_student):
    student = make_student()
    login(client, student)
    assert client.post(SEND, json={"aluno_id": student["id"], "quantidade": 1, "motivo": "x"}).status_code == 403


def test_credito_semestral_acumula_o_saldo_restante(client, make_professor):
    professor = make_professor()
    login(client, professor)
    with SessionLocal() as db:
        db.execute(update(Professor).where(Professor.id == professor["id"]).values(
            saldo=250, ultimo_credito_semestre="2000-1"))
        db.commit()
    assert client.get("/api/extratos/professor").json()["saldo"] == 1250
    assert client.get("/api/extratos/professor").json()["saldo"] == 1250  # só credita uma vez por semestre


def test_professor_lista_apenas_alunos_da_propria_instituicao(client, make_student, make_professor):
    mine, other = make_student(instituicao_id=1), make_student(instituicao_id=2)
    login(client, make_professor(instituicao_id=1))
    ids = [item["id"] for item in client.get("/api/professores/me/alunos").json()]
    assert mine["id"] in ids and other["id"] not in ids


def test_resgate_desconta_saldo_e_envia_o_mesmo_codigo_ao_aluno_e_ao_parceiro(
    client, outbox, make_student, make_professor, make_company
):
    student, professor, company = make_student(), make_professor(), make_company()
    item = advantage(client, company, cost=50)
    login(client, professor)
    client.post(SEND, json={"aluno_id": student["id"], "quantidade": 80, "motivo": "x"})
    client.post("/api/logout")
    outbox.clear()

    login(client, student)
    response = client.post(f"/api/vantagens/{item['id']}/resgatar")
    assert response.status_code == 201
    body = response.json()
    assert body["saldo_restante"] == 30
    assert {m["To"] for m in outbox} == {student["email"], company["email"]}
    assert all(body["codigo"] in m.get_content() for m in outbox)
    assert client.get("/api/extratos/aluno").json()["trocas"][0]["codigo"] == body["codigo"]

    client.post("/api/logout")
    login(client, company)
    check = client.get(f"/api/trocas/{body['codigo'].lower()}")
    assert check.status_code == 200
    assert check.json()["aluno_nome"] == student["nome"]


def test_resgate_com_saldo_insuficiente(client, outbox, make_student, make_company):
    student, company = make_student(), make_company()
    item = advantage(client, company, cost=50)
    login(client, student)
    response = client.post(f"/api/vantagens/{item['id']}/resgatar")
    assert response.status_code == 400
    assert outbox == []


def test_codigos_de_cupom_sao_unicos(client, make_student, make_professor, make_company):
    student, professor, company = make_student(), make_professor(), make_company()
    item = advantage(client, company, cost=10)
    login(client, professor)
    client.post(SEND, json={"aluno_id": student["id"], "quantidade": 100, "motivo": "x"})
    client.post("/api/logout")
    login(client, student)
    codes = {client.post(f"/api/vantagens/{item['id']}/resgatar").json()["codigo"] for _ in range(5)}
    assert len(codes) == 5


def test_empresa_so_confere_codigo_das_proprias_vantagens(client, make_student, make_professor, make_company):
    student, professor, owner, other = make_student(), make_professor(), make_company(), make_company()
    item = advantage(client, owner, cost=10)
    login(client, professor)
    client.post(SEND, json={"aluno_id": student["id"], "quantidade": 10, "motivo": "x"})
    client.post("/api/logout")
    login(client, student)
    code = client.post(f"/api/vantagens/{item['id']}/resgatar").json()["codigo"]
    client.post("/api/logout")
    login(client, other)
    assert client.get(f"/api/trocas/{code}").status_code == 404


def test_vantagem_exige_foto_valida(client, make_company):
    login(client, make_company())
    data = {"descricao": "Desconto", "custo_em_moedas": "10"}
    assert client.post("/api/vantagens", data=data).status_code == 422
    not_image = client.post("/api/vantagens", data=data, files={"foto": ("a.png", b"texto", "image/png")})
    assert not_image.status_code == 400


def test_vantagem_rejeita_foto_grande(client, monkeypatch, make_company):
    from src.settings import settings
    monkeypatch.setattr(settings, "max_upload_bytes", 16)
    login(client, make_company())
    response = client.post(
        "/api/vantagens",
        data={"descricao": "Desconto", "custo_em_moedas": "10"},
        files={"foto": ("a.png", PNG, "image/png")},
    )
    assert response.status_code == 413


def test_foto_da_vantagem_e_servida_e_removida_com_ela(client, make_company):
    company = make_company()
    item = advantage(client, company)
    assert item["foto_url"].startswith("/uploads/")
    assert client.get(item["foto_url"]).content == PNG
    login(client, company)
    assert client.delete(f"/api/vantagens/{item['id']}").status_code == 204
    assert client.get(item["foto_url"]).status_code == 404


def test_atualizar_vantagem_sem_nova_foto_mantem_a_foto(client, make_company):
    company = make_company()
    item = advantage(client, company)
    login(client, company)
    response = client.put(f"/api/vantagens/{item['id']}", data={"descricao": "Novo texto", "custo_em_moedas": "70"})
    assert response.status_code == 200
    assert response.json()["foto_url"] == item["foto_url"]
    assert response.json()["custo_em_moedas"] == 70


def test_vantagem_com_resgate_nao_pode_ser_removida(client, make_student, make_professor, make_company):
    student, professor, company = make_student(), make_professor(), make_company()
    item = advantage(client, company, cost=10)
    login(client, professor)
    client.post(SEND, json={"aluno_id": student["id"], "quantidade": 10, "motivo": "x"})
    client.post("/api/logout")
    login(client, student)
    client.post(f"/api/vantagens/{item['id']}/resgatar")
    client.post("/api/logout")
    login(client, company)
    assert client.delete(f"/api/vantagens/{item['id']}").status_code == 409
