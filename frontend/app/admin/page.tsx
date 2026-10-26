"use client";

import { FormEvent, useCallback, useState } from "react";
import { Field } from "../../components/painel/Field";
import { Institution, Professor } from "../../components/painel/types";
import { apiRequest, errorText } from "../../lib/api";

const CSV_COLUMNS = ["nome", "email", "login", "senha", "cpf", "departamento"] as const;

function parseProfessors(text: string, institutionId: number) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      const cells = line.split(";").map((cell) => cell.trim());
      if (cells.length !== CSV_COLUMNS.length) {
        throw new Error(`Linha ${index + 1}: use ${CSV_COLUMNS.join(";")}.`);
      }
      return { ...Object.fromEntries(CSV_COLUMNS.map((column, i) => [column, cells[i]])), instituicao_id: institutionId };
    });
}

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [unlocked, setUnlocked] = useState(false);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [editing, setEditing] = useState<Professor | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  const notify = (text: string, isError = false) => { setMessage(text); setError(isError); };
  const admin = useCallback((path: string, options: RequestInit = {}) =>
    apiRequest<never>(`/admin${path}`, { ...options, headers: { "X-Admin-Token": token } }), [token]);

  const load = useCallback(async () => {
    const [list, items] = await Promise.all([admin("/professores") as Promise<Professor[]>, apiRequest<Institution[]>("/instituicoes")]);
    setProfessors(list);
    setInstitutions(items);
  }, [admin]);

  async function unlock(event: FormEvent) {
    event.preventDefault();
    try {
      await load();
      setUnlocked(true);
      notify("");
    } catch (reason) {
      notify(errorText(reason, "Não foi possível acessar a área administrativa."), true);
    }
  }

  async function run(action: () => Promise<unknown>, success: string, form?: HTMLFormElement) {
    try {
      await action();
      notify(success);
      form?.reset();
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível concluir a operação."), true);
    }
  }

  function createInstitution(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const nome = String(new FormData(form).get("nome"));
    void run(() => admin("/instituicoes", { method: "POST", body: JSON.stringify({ nome }) }), "Instituição cadastrada.", form);
  }

  function createProfessor(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    void run(
      () => admin("/professores", { method: "POST", body: JSON.stringify({ ...data, instituicao_id: Number(data.instituicao_id) }) }),
      "Professor cadastrado com 1.000 moedas. Ele já pode acessar o sistema.",
      form,
    );
  }

  function importProfessors(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    let professores;
    try {
      professores = parseProfessors(String(data.lista), Number(data.instituicao_id));
    } catch (reason) {
      return notify(errorText(reason, "Lista inválida."), true);
    }
    void run(
      () => admin("/professores/lote", { method: "POST", body: JSON.stringify({ professores }) }),
      `${professores.length} professor(es) importado(s).`,
      form,
    );
  }

  function saveProfessor(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editing) return;
    const data = Object.fromEntries(new FormData(event.currentTarget));
    void run(
      () => admin(`/professores/${editing.id}`, { method: "PUT", body: JSON.stringify({ ...data, instituicao_id: Number(data.instituicao_id) }) }),
      "Professor atualizado.",
    ).then(() => setEditing(null));
  }

  const institutionSelect = (defaultValue = "") => (
    <label>
      Instituição de ensino
      <select name="instituicao_id" required defaultValue={defaultValue}>
        <option value="" disabled>Selecione uma instituição</option>
        {institutions.map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}
      </select>
    </label>
  );

  return (
    <div className="dashboard">
      <div className="dashboard-top">
        <div>
          <span className="eyebrow">Administração</span>
          <h1>Instituições e professores.</h1>
          <p>Cadastre as instituições parceiras e os professores enviados por elas. Cada professor recebe 1.000 moedas por semestre.</p>
        </div>
      </div>
      {message && <p className={`form-message ${error ? "error" : ""}`} role={error ? "alert" : "status"}>{message}</p>}
      {!unlocked ? (
        <section className="panel">
          <h2>Acesso administrativo</h2>
          <p className="muted">Informe o ADMIN_TOKEN configurado no servidor.</p>
          <form className="inline-form" onSubmit={unlock}>
            <input type="password" aria-label="Token administrativo" value={token} onChange={(event) => setToken(event.target.value)} autoComplete="off" required />
            <button type="submit">Entrar</button>
          </form>
        </section>
      ) : (
        <div className="profile-sections">
          <section className="panel">
            <h2>Nova instituição</h2>
            <form className="inline-form" onSubmit={createInstitution}>
              <input name="nome" aria-label="Nome da instituição" placeholder="Nome da instituição" maxLength={150} required />
              <button type="submit">Cadastrar</button>
            </form>
          </section>
          <section className="panel">
            <h2>Cadastrar professor</h2>
            <p className="muted">O professor usa a senha provisória no primeiro acesso e pode trocá-la em &quot;Mudar senha&quot;.</p>
            <form className="form-grid" onSubmit={createProfessor}>
              <Field label="Nome" name="nome" />
              <Field label="E-mail" name="email" type="email" />
              <Field label="Login" name="login" />
              <Field label="Senha provisória (mínimo 8 caracteres)" name="senha" type="password" minLength={8} autoComplete="new-password" />
              <Field label="CPF" name="cpf" />
              <Field label="Departamento" name="departamento" />
              {institutionSelect()}
              <button type="submit" className="full-width-submit">Cadastrar professor</button>
            </form>
          </section>
          <section className="panel">
            <h2>Importar lista da instituição</h2>
            <p className="muted">Uma linha por professor: {CSV_COLUMNS.join(";")}. Se uma linha falhar, nenhum professor é importado.</p>
            <form className="form-stack" onSubmit={importProfessors}>
              {institutionSelect()}
              <label>
                Lista
                <textarea name="lista" rows={6} required placeholder="Maria Souza;maria@escola.edu;msouza;senha-provisoria;52998224725;Matemática" />
              </label>
              <button type="submit">Importar professores</button>
            </form>
          </section>
          <section className="panel">
            <h2>Professores cadastrados</h2>
            <div className="record-list">
              {professors.map((item) => (
                <article className="record-card" key={item.id}>
                  <div>
                    <span className="record-id">Professor #{item.id}</span>
                    <h3>{item.nome}</h3>
                    <p>{item.email} · {item.departamento} · {institutions.find((i) => i.id === item.instituicao_id)?.nome ?? "—"} · {item.saldo} moedas</p>
                  </div>
                  <button type="button" className="secondary-button" onClick={() => setEditing(item)}>Editar</button>
                </article>
              ))}
              {professors.length === 0 && <p className="empty-state">Nenhum professor cadastrado.</p>}
            </div>
            {editing && (
              <form className="form-grid edit-form" key={editing.id} onSubmit={saveProfessor}>
                <h3>Editar professor #{editing.id}</h3>
                <Field label="Nome" name="nome" defaultValue={editing.nome} />
                <Field label="E-mail" name="email" type="email" defaultValue={editing.email} />
                <Field label="Login" name="login" defaultValue={editing.login} />
                <Field label="CPF" name="cpf" defaultValue={editing.cpf} />
                <Field label="Departamento" name="departamento" defaultValue={editing.departamento} />
                {institutionSelect(String(editing.instituicao_id))}
                <button type="submit" className="full-width-submit">Salvar alterações</button>
                <button type="button" className="secondary-button full-width-submit" onClick={() => setEditing(null)}>Cancelar</button>
              </form>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
