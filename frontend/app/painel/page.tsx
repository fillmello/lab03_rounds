"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { apiRequest } from "../../lib/api";

type User = { id: number; nome: string; tipo: "aluno" | "professor" | "empresa_parceira" };
type Student = { id: number; nome: string; email: string; login: string; cpf: string; rg: string; endereco: string; curso: string; instituicao_id: number; saldo: number };
type Professor = { id: number; nome: string; email: string; login: string; cpf: string; departamento: string; instituicao_id: number; saldo: number };
type Company = { id: number; nome: string; email: string; login: string; cnpj: string };
type Advantage = { id: number; descricao: string; foto: string; custo_em_moedas: number; empresa_id: number };
type Statement = { saldo: number; envios: { id: number; data: string; quantidade: number; motivo: string; aluno_id: number; professor_id: number }[]; trocas: { id: number; data: string; quantidade: number; codigo: string; aluno_id: number; vantagem_id: number }[] };
type Redemption = { codigo: string; quantidade: number; vantagem_id: number; saldo_restante: number };

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  const notify = useCallback((text: string, isError = false) => { setMessage(text); setError(isError); }, []);
  const reload = useCallback(async () => {
    try { setLoading(true); const me = await apiRequest<User>("/me"); setUser(me); }
    catch { window.location.href = "/login"; }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void reload(); }, [reload]);

  async function signOut() {
    await apiRequest("/logout", { method: "POST" }).catch(() => undefined);
    window.location.href = "/login";
  }
  if (loading) return <div className="dashboard"><p className="loading-state">Carregando seu painel…</p></div>;
  if (!user) return null;
  const profile = user.tipo === "aluno" ? "Aluno" : user.tipo === "professor" ? "Professor" : "Empresa parceira";
  return (
    <div className="dashboard">
      <div className="dashboard-top">
        <div><span className="eyebrow">{profile}</span><h1>Olá, {user.nome}.</h1><p>Gerencie sua conta e acompanhe suas movimentações.</p></div>
        <button type="button" className="secondary-button" onClick={signOut}>Sair</button>
      </div>
      {message && <p className={`form-message ${error ? "error" : ""}`}>{message}</p>}
      {user.tipo === "aluno" && <StudentPanel user={user} notify={notify} />}
      {user.tipo === "professor" && <ProfessorPanel user={user} notify={notify} />}
      {user.tipo === "empresa_parceira" && <CompanyPanel user={user} notify={notify} />}
    </div>
  );
}

function StudentPanel({ user, notify }: { user: User; notify: (message: string, error?: boolean) => void }) {
  const [student, setStudent] = useState<Student | null>(null);
  const [statement, setStatement] = useState<Statement | null>(null);
  const [advantages, setAdvantages] = useState<Advantage[]>([]);
  const [busy, setBusy] = useState(true);
  const load = useCallback(async () => {
    try { setBusy(true); const [profile, extract, items] = await Promise.all([apiRequest<Student>(`/alunos/${user.id}`), apiRequest<Statement>("/extratos/aluno"), apiRequest<Advantage[]>("/vantagens")]); setStudent(profile); setStatement(extract); setAdvantages(items); }
    catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível carregar seus dados.", true); }
    finally { setBusy(false); }
  }, [notify, user.id]);
  useEffect(() => { void load(); }, [load]);
  async function update(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); const payload = Object.fromEntries(Object.entries(data).filter(([, value]) => String(value).trim()));
    try { await apiRequest(`/alunos/${user.id}`, { method: "PUT", body: JSON.stringify(payload) }); notify("Cadastro atualizado com sucesso."); await load(); }
    catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível atualizar o cadastro.", true); }
  }
  async function redeem(id: number) {
    if (!window.confirm("Confirmar resgate desta vantagem?")) return;
    try { const result = await apiRequest<Redemption>(`/vantagens/${id}/resgatar`, { method: "POST" }); notify(`Resgate realizado. Código: ${result.codigo}`); await load(); }
    catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível resgatar a vantagem.", true); }
  }
  if (busy || !student || !statement) return <p className="loading-state">Carregando seus dados…</p>;
  return <div className="profile-sections">
    <section className="panel"><div className="section-heading"><div><h2>Meu cadastro</h2><p className="muted">Mantenha seus dados atualizados.</p></div><strong className="balance">{statement.saldo} moedas</strong></div>
      <form className="form-grid" onSubmit={update}><Field label="Nome" name="nome" defaultValue={student.nome}/><Field label="E-mail" name="email" type="email" defaultValue={student.email}/><Field label="Login" name="login" defaultValue={student.login}/><Field label="Curso" name="curso" defaultValue={student.curso}/><Field label="RG" name="rg" defaultValue={student.rg}/><Field label="Endereço" name="endereco" defaultValue={student.endereco} wide/><Field label="Nova senha (opcional)" name="senha" type="password"/><button type="submit">Salvar cadastro</button></form>
    </section>
    <section className="panel"><h2>Vantagens disponíveis</h2><p className="muted">Use suas moedas para resgatar benefícios.</p><div className="record-list">{advantages.map(item => <article className="record-card" key={item.id}><div><span className="record-id">Oferta #{item.id}</span><h3>{item.descricao}</h3><p>{item.custo_em_moedas} moedas · {item.foto}</p></div><button type="button" onClick={() => void redeem(item.id)} disabled={statement.saldo < item.custo_em_moedas}>Resgatar</button></article>)}{advantages.length === 0 && <p className="empty-state">Nenhuma vantagem disponível.</p>}</div></section>
    <StatementPanel statement={statement}/>
  </div>;
}

function ProfessorPanel({ user, notify }: { user: User; notify: (message: string, error?: boolean) => void }) {
  const [professor, setProfessor] = useState<Professor | null>(null); const [statement, setStatement] = useState<Statement | null>(null); const [busy, setBusy] = useState(true);
  const load = useCallback(async () => { try { setBusy(true); const [profile, extract] = await Promise.all([apiRequest<Professor>(`/professores/${user.id}`), apiRequest<Statement>("/extratos/professor")]); setProfessor(profile); setStatement(extract); } catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível carregar seus dados.", true); } finally { setBusy(false); } }, [notify, user.id]);
  useEffect(() => { void load(); }, [load]);
  async function send(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); try { await apiRequest("/moedas/enviar", { method: "POST", body: JSON.stringify({ aluno_id: Number(data.aluno_id), quantidade: Number(data.quantidade), motivo: data.motivo }) }); notify("Moedas enviadas com sucesso."); event.currentTarget.reset(); await load(); } catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível enviar moedas.", true); } }
  if (busy || !professor || !statement) return <p className="loading-state">Carregando seus dados…</p>;
  return <div className="profile-sections"><section className="panel"><div className="section-heading"><div><h2>Saldo do professor</h2><p className="muted">Reconheça um aluno da sua instituição.</p></div><strong className="balance">{statement.saldo} moedas</strong></div><form className="form-grid" onSubmit={send}><Field label="ID do aluno" name="aluno_id" type="number"/><Field label="Quantidade" name="quantidade" type="number"/><Field label="Motivo" name="motivo" wide/><button type="submit">Enviar moedas</button></form></section><StatementPanel statement={statement} outgoing/></div>;
}

function CompanyPanel({ user, notify }: { user: User; notify: (message: string, error?: boolean) => void }) {
  const [company, setCompany] = useState<Company | null>(null); const [advantages, setAdvantages] = useState<Advantage[]>([]); const [code, setCode] = useState(""); const [checked, setChecked] = useState<{ codigo: string; quantidade: number; aluno_id: number } | null>(null); const [editing, setEditing] = useState<Advantage | null>(null); const [busy, setBusy] = useState(true);
  const load = useCallback(async () => { try { setBusy(true); const [profile, items] = await Promise.all([apiRequest<Company>(`/empresas/${user.id}`), apiRequest<Advantage[]>("/vantagens")]); setCompany(profile); setAdvantages(items.filter(item => item.empresa_id === user.id)); } catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível carregar seus dados.", true); } finally { setBusy(false); } }, [notify, user.id]);
  useEffect(() => { void load(); }, [load]);
  async function updateCompany(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); const payload = Object.fromEntries(Object.entries(data).filter(([, value]) => String(value).trim())); try { await apiRequest(`/empresas/${user.id}`, { method: "PUT", body: JSON.stringify(payload) }); notify("Cadastro atualizado com sucesso."); await load(); } catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível atualizar o cadastro.", true); } }
  async function saveAdvantage(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); try { await apiRequest(editing ? `/vantagens/${editing.id}` : "/vantagens", { method: editing ? "PUT" : "POST", body: JSON.stringify({ descricao: data.descricao, foto: data.foto, custo_em_moedas: Number(data.custo_em_moedas) }) }); notify(editing ? "Vantagem atualizada." : "Vantagem criada."); setEditing(null); event.currentTarget.reset(); await load(); } catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível salvar a vantagem.", true); } }
  async function remove(id: number) { if (!window.confirm("Remover esta vantagem?")) return; try { await apiRequest(`/vantagens/${id}`, { method: "DELETE" }); notify("Vantagem removida."); await load(); } catch (reason) { notify(reason instanceof Error ? reason.message : "Não foi possível remover a vantagem.", true); } }
  async function check(event: FormEvent) { event.preventDefault(); try { setChecked(await apiRequest<{ codigo: string; quantidade: number; aluno_id: number }>(`/trocas/${encodeURIComponent(code.trim())}`)); notify("Código conferido."); } catch (reason) { setChecked(null); notify(reason instanceof Error ? reason.message : "Código não encontrado.", true); } }
  if (busy || !company) return <p className="loading-state">Carregando seus dados…</p>;
  return <div className="profile-sections"><section className="panel"><h2>Meu cadastro</h2><p className="muted">Atualize os dados da empresa parceira.</p><form className="form-grid" onSubmit={updateCompany}><Field label="Nome" name="nome" defaultValue={company.nome}/><Field label="E-mail" name="email" type="email" defaultValue={company.email}/><Field label="Login" name="login" defaultValue={company.login}/><Field label="CNPJ" name="cnpj" defaultValue={company.cnpj}/><Field label="Nova senha (opcional)" name="senha" type="password"/><button type="submit">Salvar cadastro</button></form></section><section className="panel"><h2>{editing ? "Editar vantagem" : "Nova vantagem"}</h2><form className="form-grid" onSubmit={saveAdvantage}><Field label="Descrição" name="descricao" defaultValue={editing?.descricao} wide/><Field label="Foto (URL ou referência)" name="foto" defaultValue={editing?.foto}/><Field label="Custo em moedas" name="custo_em_moedas" type="number" defaultValue={editing?.custo_em_moedas}/><button type="submit">{editing ? "Salvar alteração" : "Criar vantagem"}</button>{editing && <button type="button" className="secondary-button" onClick={() => setEditing(null)}>Cancelar</button>}</form></section><section className="panel"><h2>Minhas vantagens</h2><div className="record-list">{advantages.map(item => <article className="record-card" key={item.id}><div><span className="record-id">Oferta #{item.id}</span><h3>{item.descricao}</h3><p>{item.custo_em_moedas} moedas · {item.foto}</p></div><div className="record-actions"><button type="button" className="secondary-button" onClick={() => setEditing(item)}>Editar</button><button type="button" className="danger-button" onClick={() => void remove(item.id)}>Remover</button></div></article>)}{advantages.length === 0 && <p className="empty-state">Você ainda não cadastrou vantagens.</p>}</div></section><section className="panel"><h2>Conferir código de troca</h2><form className="inline-form" onSubmit={check}><input aria-label="Código de troca" value={code} onChange={event => setCode(event.target.value)} placeholder="Cole o código do aluno" required/><button type="submit">Conferir</button></form>{checked && <p className="success-box">Código válido: {checked.quantidade} moedas · aluno #{checked.aluno_id}.</p>}</section></div>;
}

function StatementPanel({ statement, outgoing = false }: { statement: Statement; outgoing?: boolean }) {
  return <section className="panel"><div className="section-heading"><div><h2>Extrato</h2><p className="muted">Movimentações recentes.</p></div><strong className="balance">{statement.saldo} moedas</strong></div><div className="statement-list">{statement.envios.map(item => <div className="statement-row" key={`e-${item.id}`}><span>Envio para aluno #{item.aluno_id}<small>{item.motivo}</small></span><strong>{outgoing ? "-" : "+"}{item.quantidade}</strong></div>)}{statement.trocas.map(item => <div className="statement-row" key={`t-${item.id}`}><span>Resgate #{item.vantagem_id}<small>{item.codigo}</small></span><strong>-{item.quantidade}</strong></div>)}{statement.envios.length + statement.trocas.length === 0 && <p className="empty-state">Nenhuma movimentação ainda.</p>}</div></section>;
}

function Field({ label, name, type = "text", defaultValue, wide = false }: { label: string; name: string; type?: string; defaultValue?: string | number; wide?: boolean }) {
  return <label className={wide ? "span-two" : ""}>{label}<input name={name} type={type} defaultValue={defaultValue} required={name !== "senha"}/></label>;
}
