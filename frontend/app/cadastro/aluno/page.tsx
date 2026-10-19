"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { apiRequest } from "../../../lib/api";

type Institution = { id: number; nome: string };

export default function StudentRegistrationPage() {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    apiRequest<Institution[]>("/instituicoes").then(setInstitutions).catch(() => setInstitutions([]));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const onlyDigits = (value: FormDataEntryValue | null) => String(value || "").replace(/\D/g, "");
    try {
      const student = await apiRequest<{ id: number }>("/alunos", {
        method: "POST",
        body: JSON.stringify({
          nome: form.get("nome"), email: form.get("email"), login: form.get("login"),
          senha: form.get("senha"), cpf: onlyDigits(form.get("cpf")), rg: form.get("rg"),
          endereco: form.get("endereco"), curso: form.get("curso"),
          instituicao_id: Number(form.get("instituicao_id")),
        }),
      });
      setError(false);
      setMessage(`Cadastro realizado. Seu ID é ${student.id}.`);
      event.currentTarget.reset();
    } catch (reason) {
      setError(true);
      setMessage(reason instanceof Error ? reason.message : "Não foi possível concluir o cadastro.");
    }
  }

  return (
    <div className="form-page">
      <div className="page-heading">
        <span className="eyebrow">Novo cadastro</span>
        <h1>Crie sua conta de aluno</h1>
        <p>Preencha seus dados para participar da rede de reconhecimento.</p>
      </div>
      <section className="panel wide-panel">
        <form className="form-stack" onSubmit={submit}>
          <div className="form-grid">
            <Field label="Nome completo" name="nome" />
            <Field label="E-mail" name="email" type="email" />
            <Field label="Login" name="login" />
            <Field label="Senha" name="senha" type="password" />
            <Field label="CPF" name="cpf" />
            <Field label="RG" name="rg" />
            <Field label="Endereço" name="endereco" wide />
            <Field label="Curso" name="curso" />
            <label>Instituição<select name="instituicao_id" required><option value="">Selecione</option>{institutions.map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}</select></label>
          </div>
          <button type="submit">Criar conta</button>
        </form>
        <p className={`form-message ${error ? "error" : ""}`}>{message}</p>
        <Link href="/login" className="back-link">Voltar para o login</Link>
      </section>
    </div>
  );
}

function Field({ label, name, type = "text", wide = false }: { label: string; name: string; type?: string; wide?: boolean }) {
  return <label className={wide ? "span-two" : ""}>{label}<input name={name} type={type} required /></label>;
}
