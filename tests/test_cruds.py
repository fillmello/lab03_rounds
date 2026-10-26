from tests.conftest import ADMIN, login, make_cnpj, make_cpf


def test_cadastro_de_aluno_nao_expoe_senha(client, make_student):
    student = make_student()
    assert "senha" not in client.post("/api/login", json={"login": student["login"], "senha": student["senha"]}).text
    login(client, student)
    body = client.get(f"/api/alunos/{student['id']}").json()
    assert "senha" not in body and "senha_hash" not in body
    assert body["saldo"] == 0


def test_cadastro_duplicado_de_aluno(client, make_student):
    student = make_student()
    payload = {k: student[k] for k in ("nome", "email", "login", "senha", "cpf", "rg", "endereco", "curso", "instituicao_id")}
    assert client.post("/api/alunos", json=payload).status_code == 409


def test_cpf_com_digito_verificador_invalido(client):
    payload = {"nome": "A", "email": "a@mail.com", "login": "a", "senha": "senha-forte-1",
               "cpf": "11111111112", "rg": "1", "endereco": "r", "curso": "c", "instituicao_id": 1}
    assert client.post("/api/alunos", json=payload).status_code == 422
    valid = make_cpf(42)
    payload["cpf"] = f"{valid[:3]}.{valid[3:6]}.{valid[6:9]}-{valid[9:]}"  # válido, com máscara
    assert client.post("/api/alunos", json=payload).status_code == 201


def test_email_invalido_e_instituicao_inexistente(client):
    base = {"nome": "A", "email": "a@mail.com", "login": "a", "senha": "senha-forte-1",
            "cpf": make_cpf(1), "rg": "1", "endereco": "r", "curso": "c", "instituicao_id": 1}
    assert client.post("/api/alunos", json=base | {"email": "sem-arroba"}).status_code == 422
    assert client.post("/api/alunos", json=base | {"instituicao_id": 999}).status_code == 404


def test_edicao_de_aluno(client, make_student):
    student = make_student()
    login(client, student)
    response = client.put(f"/api/alunos/{student['id']}", json={"curso": "Medicina", "nome": "Novo Nome"})
    assert response.status_code == 200
    assert response.json()["curso"] == "Medicina"


def test_edicao_nao_aceita_senha_nem_dados_duplicados(client, make_student):
    first, second = make_student(), make_student()
    login(client, second)
    assert client.put(f"/api/alunos/{second['id']}", json={"senha": "outra-senha-1"}).status_code == 400
    assert client.put(f"/api/alunos/{second['id']}", json={"email": first["email"]}).status_code == 409


def test_aluno_nao_acessa_nem_altera_outro_aluno(client, make_student):
    first, second = make_student(), make_student()
    login(client, second)
    assert client.get(f"/api/alunos/{first['id']}").status_code == 403
    assert client.put(f"/api/alunos/{first['id']}", json={"curso": "x"}).status_code == 403
    assert client.delete(f"/api/alunos/{first['id']}").status_code == 403


def test_empresa_nao_acessa_rotas_de_aluno(client, make_company, make_student):
    student, company = make_student(), make_company()
    login(client, company)
    assert client.get(f"/api/alunos/{student['id']}").status_code == 403


def test_remocao_de_aluno(client, make_student):
    student = make_student()
    login(client, student)
    assert client.delete(f"/api/alunos/{student['id']}").status_code == 204
    assert client.get("/api/me").status_code == 401


def test_aluno_com_moedas_recebidas_nao_pode_ser_removido(client, make_student, make_professor):
    student, professor = make_student(), make_professor()
    login(client, professor)
    client.post("/api/moedas/enviar", json={"aluno_id": student["id"], "quantidade": 5, "motivo": "x"})
    client.post("/api/logout")
    login(client, student)
    response = client.delete(f"/api/alunos/{student['id']}")
    assert response.status_code == 409
    assert client.get("/api/extratos/aluno").json()["saldo"] == 5


def test_cadastro_edicao_e_remocao_de_empresa(client, make_company):
    company = make_company()
    login(client, company)
    assert client.put(f"/api/empresas/{company['id']}", json={"nome": "Nova Empresa"}).json()["nome"] == "Nova Empresa"
    assert client.delete(f"/api/empresas/{company['id']}").status_code == 204


def test_cnpj_invalido_ou_duplicado(client, make_company):
    company = make_company()
    base = {"nome": "E", "email": "e@mail.com", "login": "e", "senha": "senha-forte-1", "cnpj": make_cnpj(7)}
    assert client.post("/api/empresas", json=base | {"cnpj": "12345678000100"}).status_code == 422
    assert client.post("/api/empresas", json=base | {"cnpj": company["cnpj"]}).status_code == 409


def test_empresa_com_vantagens_nao_pode_ser_removida(client, make_company):
    company = make_company()
    login(client, company)
    client.post("/api/vantagens", data={"descricao": "x", "custo_em_moedas": "5"},
                files={"foto": ("a.png", b"\x89PNG\r\n\x1a\n00", "image/png")})
    assert client.delete(f"/api/empresas/{company['id']}").status_code == 409


def test_listagens_nao_vazam_outros_usuarios(client, make_student, make_company):
    make_student(), make_student()
    student = make_student()
    login(client, student)
    assert [item["id"] for item in client.get("/api/alunos").json()] == [student["id"]]


def test_rotas_protegidas_exigem_login(client):
    for path in ("/api/me", "/api/alunos", "/api/empresas", "/api/vantagens", "/api/extratos/aluno"):
        assert client.get(path).status_code == 401


# --- área administrativa (instituições e professores pré-cadastrados) ---

def test_admin_exige_token(client):
    assert client.post("/api/admin/instituicoes", json={"nome": "X"}).status_code == 403
    assert client.post("/api/admin/instituicoes", json={"nome": "X"}, headers={"X-Admin-Token": "errado"}).status_code == 403
    assert client.get("/api/admin/professores").status_code == 403


def test_admin_cadastra_instituicao_e_rejeita_duplicada(client):
    response = client.post("/api/admin/instituicoes", json={"nome": "PUC Minas"}, headers=ADMIN)
    assert response.status_code == 201
    assert client.post("/api/admin/instituicoes", json={"nome": "PUC Minas"}, headers=ADMIN).status_code == 409
    assert "PUC Minas" in [item["nome"] for item in client.get("/api/instituicoes").json()]


def test_professor_pre_cadastrado_nasce_com_1000_moedas_e_consegue_entrar(client, make_professor):
    professor = make_professor()
    assert professor["saldo"] == 1000
    login(client, professor)
    assert client.get("/api/me").json()["tipo"] == "professor"


def test_empresa_nao_cadastra_professor(client, make_company):
    login(client, make_company())
    assert client.post("/api/admin/professores", json={}).status_code == 403


def test_importacao_em_lote_e_tudo_ou_nada(client):
    def row(n, **extra):
        return {"nome": f"Prof {n}", "email": f"p{n}@mail.com", "login": f"p{n}", "senha": "senha-forte-1",
                "cpf": make_cpf(900 + n), "departamento": "Dep", "instituicao_id": 1} | extra

    ok = client.post("/api/admin/professores/lote", json={"professores": [row(1), row(2)]}, headers=ADMIN)
    assert ok.status_code == 201 and len(ok.json()) == 2

    repetido = client.post("/api/admin/professores/lote", json={"professores": [row(3), row(3)]}, headers=ADMIN)
    assert repetido.status_code == 409
    ja_existente = client.post("/api/admin/professores/lote", json={"professores": [row(4), row(1)]}, headers=ADMIN)
    assert ja_existente.status_code == 409
    logins = [p["login"] for p in client.get("/api/admin/professores", headers=ADMIN).json()]
    assert "p4" not in logins and "p3" not in logins


def test_admin_edita_professor(client, make_professor):
    professor = make_professor()
    response = client.put(f"/api/admin/professores/{professor['id']}", json={"departamento": "Física"}, headers=ADMIN)
    assert response.json()["departamento"] == "Física"
