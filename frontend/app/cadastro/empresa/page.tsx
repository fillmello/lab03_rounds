"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiRequest, errorText } from "../../../lib/api";

export default function CompanyRegistrationPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget; // currentTarget vira null depois de um await
    const form = new FormData(formElement);
    const payload = Object.fromEntries(form);
    payload.cnpj = String(payload.cnpj).replace(/\D/g, "");
    try {
      const company = await apiRequest<{ id: number }>("/empresas", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setError(false);
      setMessage(`Cadastro realizado. Seu ID é ${company.id}.`);
      formElement.reset();
    } catch (reason) {
      setError(true);
      setMessage(errorText(reason, "Não foi possível concluir o cadastro."));
    }
  }

  return (
    <div className="form-page narrow-page">
      <div className="page-heading">
        <span className="eyebrow">Parceria</span>
        <h1>Traga sua empresa para a comunidade</h1>
        <p>Ofereça vantagens para alunos e faça parte dessa rede.</p>
      </div>
      <section className="panel">
        <form className="form-stack" onSubmit={submit}>
          <Field label="Nome da empresa" name="nome" />
          <Field label="CNPJ" name="cnpj" />
          <Field label="E-mail" name="email" type="email" />
          <Field label="Login" name="login" />
          <Field label="Senha (mínimo 8 caracteres)" name="senha" type="password" />
          <button type="submit">Cadastrar empresa</button>
        </form>
        <p className={`form-message ${error ? "error" : ""}`}>{message}</p>
        <Link href="/login" className="back-link">Voltar para o login</Link>
      </section>
    </div>
  );
}

function Field({ label, name, type = "text" }: { label: string; name: string; type?: string }) {
  const isPassword = type === "password";
  return <label>{label}<input name={name} type={type} required minLength={isPassword ? 8 : undefined} maxLength={isPassword ? 128 : undefined} autoComplete={isPassword ? "new-password" : undefined} /></label>;
}
