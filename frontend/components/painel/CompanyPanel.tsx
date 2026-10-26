"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { apiOrigin, apiRequest, errorText } from "../../lib/api";
import { Field } from "./Field";
import { PasswordDialog } from "./PasswordDialog";
import { Advantage, Company, Notify, Redemption, User } from "./types";

export function CompanyPanel({ user, notify }: { user: User; notify: Notify }) {
  const [company, setCompany] = useState<Company | null>(null);
  const [advantages, setAdvantages] = useState<Advantage[]>([]);
  const [editing, setEditing] = useState<Advantage | null>(null);
  const [code, setCode] = useState("");
  const [checked, setChecked] = useState<Redemption | null>(null);
  const [busy, setBusy] = useState(true);

  const load = useCallback(async () => {
    try {
      const [profile, items] = await Promise.all([
        apiRequest<Company>(`/empresas/${user.id}`),
        apiRequest<Advantage[]>("/vantagens"),
      ]);
      setCompany(profile);
      setAdvantages(items.filter((item) => item.empresa_id === user.id));
    } catch (reason) {
      notify(errorText(reason, "Não foi possível carregar seus dados."), true);
    } finally {
      setBusy(false);
    }
  }, [notify, user.id]);
  useEffect(() => { void load(); }, [load]);

  async function updateCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const payload = Object.fromEntries(Object.entries(data).filter(([, value]) => String(value).trim()));
    try {
      await apiRequest(`/empresas/${user.id}`, { method: "PUT", body: JSON.stringify(payload) });
      notify("Cadastro atualizado com sucesso.");
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível atualizar o cadastro."), true);
    }
  }

  async function saveAdvantage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; // currentTarget vira null depois de um await
    const body = new FormData(form);
    const photo = body.get("foto");
    if (photo instanceof File && photo.size === 0) body.delete("foto"); // mantém a foto atual na edição
    const wasEditing = editing;
    try {
      await apiRequest(wasEditing ? `/vantagens/${wasEditing.id}` : "/vantagens", { method: wasEditing ? "PUT" : "POST", body });
      notify(wasEditing ? "Vantagem atualizada." : "Vantagem criada.");
      setEditing(null);
      form.reset();
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível salvar a vantagem."), true);
    }
  }

  async function remove(id: number) {
    if (!window.confirm("Remover esta vantagem?")) return;
    try {
      await apiRequest(`/vantagens/${id}`, { method: "DELETE" });
      notify("Vantagem removida.");
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível remover a vantagem."), true);
    }
  }

  async function check(event: FormEvent) {
    event.preventDefault();
    try {
      setChecked(await apiRequest<Redemption>(`/trocas/${encodeURIComponent(code.trim())}`));
      notify("Código conferido.");
    } catch (reason) {
      setChecked(null);
      notify(errorText(reason, "Código não encontrado."), true);
    }
  }

  if (busy || !company) return <p className="loading-state">Carregando seus dados…</p>;
  return (
    <div className="profile-sections">
      <section className="panel">
        <h2>Meu cadastro</h2>
        <p className="muted">Atualize os dados da empresa parceira.</p>
        <form className="form-grid" onSubmit={updateCompany}>
          <Field label="Nome" name="nome" defaultValue={company.nome} />
          <Field label="E-mail" name="email" type="email" defaultValue={company.email} />
          <Field label="Login" name="login" defaultValue={company.login} />
          <Field label="CNPJ" name="cnpj" defaultValue={company.cnpj} />
          <button type="submit" className="full-width-submit">Salvar cadastro</button>
        </form>
      </section>
      <PasswordDialog notify={notify} />
      <section className="panel">
        <h2>{editing ? "Editar vantagem" : "Nova vantagem"}</h2>
        <p className="muted">{editing ? "Envie uma nova foto apenas se quiser trocá-la." : "Descrição, custo em moedas e foto do produto."}</p>
        <form className="form-grid" key={editing?.id ?? "new"} onSubmit={saveAdvantage}>
          <Field label="Descrição" name="descricao" defaultValue={editing?.descricao} maxLength={2000} wide />
          <Field label="Custo em moedas" name="custo_em_moedas" type="number" min={1} step={1} defaultValue={editing?.custo_em_moedas} />
          <Field label="Foto (JPG ou PNG, até 2 MB)" name="foto" type="file" accept="image/png,image/jpeg" required={!editing} />
          <button type="submit" className="full-width-submit">{editing ? "Salvar alteração" : "Criar vantagem"}</button>
          {editing && <button type="button" className="secondary-button full-width-submit" onClick={() => setEditing(null)}>Cancelar</button>}
        </form>
      </section>
      <section className="panel">
        <h2>Minhas vantagens</h2>
        <div className="record-list">
          {advantages.map((item) => (
            <article className="record-card" key={item.id}>
              <div className="record-media">
                {item.foto_url && <img className="thumb" src={`${apiOrigin()}${item.foto_url}`} alt={item.descricao} />}
                <div>
                  <span className="record-id">Oferta #{item.id}</span>
                  <h3>{item.descricao}</h3>
                  <p>{item.custo_em_moedas} moedas</p>
                </div>
              </div>
              <div className="record-actions">
                <button type="button" className="secondary-button" onClick={() => setEditing(item)}>Editar</button>
                <button type="button" className="danger-button" onClick={() => void remove(item.id)}>Remover</button>
              </div>
            </article>
          ))}
          {advantages.length === 0 && <p className="empty-state">Você ainda não cadastrou vantagens.</p>}
        </div>
      </section>
      <section className="panel">
        <h2>Conferir código de troca</h2>
        <p className="muted">O mesmo código foi enviado por e-mail ao aluno e à empresa.</p>
        <form className="inline-form" onSubmit={check}>
          <input aria-label="Código de troca" value={code} onChange={(event) => setCode(event.target.value)} placeholder="Ex.: ABCDE-23456" required />
          <button type="submit">Conferir</button>
        </form>
        {checked && <p className="success-box">Código válido: {checked.vantagem_descricao} · {checked.quantidade} moedas · {checked.aluno_nome}.</p>}
      </section>
    </div>
  );
}
