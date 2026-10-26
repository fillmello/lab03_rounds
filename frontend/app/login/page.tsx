"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiRequest } from "../../lib/api";

export default function LoginPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError(false);
    const form = new FormData(event.currentTarget);
    try {
      await apiRequest("/login", {
        method: "POST",
        body: JSON.stringify({ login: form.get("login"), senha: form.get("senha") }),
      });
      window.location.href = "/painel";
    } catch (reason) {
      setError(true);
      setMessage(reason instanceof Error ? reason.message : "Não foi possível entrar.");
    }
  }

  return (
    <div className="auth-page">
      <section className="intro-block">
        <span className="eyebrow">Moeda Estudantil</span>
        <h1>Reconhecimento que vira oportunidade.</h1>
        <p>Acompanhe suas moedas, reconheça boas atitudes e aproveite benefícios.</p>
      </section>
      <section className="panel auth-panel">
        <span className="eyebrow">Acesso</span>
        <h2>Entrar na conta</h2>
        <p className="muted">Use seus dados para continuar.</p>
        <form className="form-stack" onSubmit={submit}>
          <label htmlFor="login">Login</label>
          <input id="login" name="login" required />
          <label htmlFor="senha">Senha</label>
          <input id="senha" name="senha" type="password" required />
          <button type="submit">Entrar</button>
        </form>
        <p className={`form-message ${error ? "error" : ""}`}>{message}</p>
        <div className="panel-footer">
          <span>Primeiro acesso?</span>
          <Link href="/cadastro/aluno">Criar conta</Link>
        </div>
      </section>
    </div>
  );
}
