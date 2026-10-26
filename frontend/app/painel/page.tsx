"use client";

import { useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useCallback, useEffect, useState } from "react";
import { apiRequest } from "../../lib/api";

type RecordType = "alunos" | "empresas";
type Student = {
  id: number;
  nome: string;
  email: string;
  login: string;
  cpf: string;
  rg: string;
  endereco: string;
  curso: string;
  instituicao_id: number;
  saldo: number;
};
type Company = { id: number; nome: string; email: string; login: string; cnpj: string };
type Institution = { id: number; nome: string };

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="dashboard"><p>Carregando painel...</p></div>}>
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const params = useSearchParams();
  const loggedType = params.get("tipo") === "empresa_parceira" ? "empresas" : "alunos";
  const [type, setType] = useState<RecordType>("alunos");
  const [students, setStudents] = useState<Student[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  const loadRecords = useCallback(async () => {
    try {
      if (type === "alunos") setStudents(await apiRequest<Student[]>("/alunos"));
      else setCompanies(await apiRequest<Company[]>("/empresas"));
      setError(false);
    } catch (reason) {
      setError(true);
      setMessage(reason instanceof Error ? reason.message : "Não foi possível carregar os cadastros.");
    }
  }, [type]);

  useEffect(() => {
    apiRequest<Institution[]>("/instituicoes").then(setInstitutions).catch(() => undefined);
  }, []);

  useEffect(() => {
    setType(loggedType);
  }, [loggedType]);

  useEffect(() => {
    setEditingId(null);
    void loadRecords();
  }, [loadRecords, loggedType]);

  async function removeRecord(id: number) {
    const label = type === "alunos" ? "aluno" : "empresa";
    if (!window.confirm(`Deseja realmente remover este ${label}?`)) return;
    try {
      await apiRequest(`/${type}/${id}`, { method: "DELETE" });
      setMessage("Cadastro removido com sucesso.");
      setError(false);
      await loadRecords();
    } catch (reason) {
      setError(true);
      setMessage(reason instanceof Error ? reason.message : "Não foi possível remover o cadastro.");
    }

  }

  async function signOut() {
    await apiRequest("/logout", { method: "POST" }).catch(() => undefined);
    window.location.href = "/login";
  }

  async function saveRecord(event: FormEvent<HTMLFormElement>, id: number) {
    event.preventDefault();
    const form = Object.fromEntries(new FormData(event.currentTarget));
    const payload: Record<string, string | number> = Object.fromEntries(
      Object.entries(form)
        .filter(([, value]) => String(value).trim() !== "")
        .map(([key, value]) => [key, String(value)]),
    );
    if (type === "alunos") payload.instituicao_id = Number(payload.instituicao_id);
    try {
      await apiRequest(`/${type}/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      setEditingId(null);
      setMessage("Cadastro atualizado com sucesso.");
      setError(false);
      await loadRecords();
    } catch (reason) {
      setError(true);
      setMessage(reason instanceof Error ? reason.message : "Não foi possível atualizar o cadastro.");
    }
  }

  const records = type === "alunos" ? students : companies;
  return (
    <div className="dashboard">
      <div className="dashboard-top">
        <div>
          <span className="eyebrow">Área de gerenciamento</span>
          <h1>Olá, {params.get("nome") || "visitante"}.</h1>
          <p>Consulte, edite e remova os cadastros da rede.</p>
        </div>
        <button type="button" className="secondary-button" onClick={signOut}>Sair</button>
      </div>
      <section className="panel">
        <div className="management-heading">
          <div>
            <h2>Cadastros</h2>
            <p className="muted">Escolha uma categoria para visualizar os registros.</p>
          </div>
          <span className="profile-label">
            Perfil: {type === "alunos" ? "Aluno" : "Empresa parceira"}
          </span>
        </div>
        <p className={`form-message ${error ? "error" : ""}`}>{message}</p>
        {records.length === 0 ? (
          <p className="empty-state">Nenhum cadastro encontrado.</p>
        ) : (
          <div className="record-list">
            {records.map((record) => (
              editingId === record.id
                ? <EditForm key={record.id} type={type} record={record} institutions={institutions} onSubmit={(event) => saveRecord(event, record.id)} onCancel={() => setEditingId(null)} />
                : <RecordCard key={record.id} type={type} record={record} onEdit={() => setEditingId(record.id)} onRemove={() => removeRecord(record.id)} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function RecordCard({ type, record, onEdit, onRemove }: {
  type: RecordType;
  record: Student | Company;
  onEdit: () => void;
  onRemove: () => void;
}) {
  const student = type === "alunos" ? record as Student : null;
  return (
    <article className="record-card">
      <div>
        <span className="record-id">ID {record.id}</span>
        <h3>{record.nome}</h3>
        <p>{record.email} · Login: {record.login}</p>
        <p>{student ? `CPF: ${student.cpf} · Curso: ${student.curso} · Saldo: ${student.saldo}` : `CNPJ: ${(record as Company).cnpj}`}</p>
      </div>
      <div className="record-actions">
        <button type="button" className="secondary-button" onClick={onEdit}>Editar</button>
        <button type="button" className="danger-button" onClick={onRemove}>Remover</button>
      </div>
    </article>
  );
}

function EditForm({ type, record, institutions, onSubmit, onCancel }: {
  type: RecordType;
  record: Student | Company;
  institutions: Institution[];
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
}) {
  const student = type === "alunos" ? record as Student : null;
  const company = type === "empresas" ? record as Company : null;
  return (
    <form className="edit-form" onSubmit={onSubmit}>
      <h3>Editando: {record.nome}</h3>
      <div className="form-grid">
        <Field label="Nome" name="nome" defaultValue={record.nome} />
        <Field label="E-mail" name="email" type="email" defaultValue={record.email} />
        <Field label="Login" name="login" defaultValue={record.login} />
        {student ? <>
          <Field label="CPF" name="cpf" defaultValue={student.cpf} />
          <Field label="RG" name="rg" defaultValue={student.rg} />
          <Field label="Curso" name="curso" defaultValue={student.curso} />
          <Field label="Endereço" name="endereco" defaultValue={student.endereco} wide />
          <label>Instituição<select name="instituicao_id" defaultValue={student.instituicao_id}>{institutions.map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}</select></label>
        </> : <Field label="CNPJ" name="cnpj" defaultValue={company?.cnpj} />}
        <Field label="Nova senha (opcional)" name="senha" type="password" />
      </div>
      <div className="record-actions">
        <button type="submit">Salvar alterações</button>
        <button type="button" className="secondary-button" onClick={onCancel}>Cancelar</button>
      </div>
    </form>
  );
}

function Field({ label, name, type = "text", defaultValue, wide = false }: {
  label: string;
  name: string;
  type?: string;
  defaultValue?: string | number;
  wide?: boolean;
}) {
  return <label className={wide ? "span-two" : ""}>{label}<input name={name} type={type} defaultValue={defaultValue} /></label>;
}
