"use client";

import { useCallback, useEffect, useState } from "react";
import { CompanyPanel } from "../../components/painel/CompanyPanel";
import { ProfessorPanel } from "../../components/painel/ProfessorPanel";
import { StudentPanel } from "../../components/painel/StudentPanel";
import { User } from "../../components/painel/types";
import { apiRequest } from "../../lib/api";

const PROFILE_LABEL = { aluno: "Aluno", professor: "Professor", empresa_parceira: "Empresa parceira" } as const;

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  const notify = useCallback((text: string, isError = false) => {
    setMessage(text);
    setError(isError);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  useEffect(() => {
    apiRequest<User>("/me")
      .then(setUser)
      .catch(() => { window.location.href = "/login"; })
      .finally(() => setLoading(false));
  }, []);

  async function signOut() {
    await apiRequest("/logout", { method: "POST" }).catch(() => undefined);
    window.location.href = "/login";
  }

  if (loading) return <div className="dashboard"><p className="loading-state">Carregando seu painel…</p></div>;
  if (!user) return null;
  return (
    <div className="dashboard">
      <div className="dashboard-top">
        <div>
          <span className="eyebrow">{PROFILE_LABEL[user.tipo]}</span>
          <h1>Olá, {user.nome}.</h1>
          <p>Gerencie sua conta e acompanhe suas movimentações.</p>
        </div>
        <button type="button" className="secondary-button" onClick={signOut}>Sair</button>
      </div>
      {message && <p className={`form-message ${error ? "error" : ""}`} role={error ? "alert" : "status"}>{message}</p>}
      {user.tipo === "aluno" && <StudentPanel user={user} notify={notify} />}
      {user.tipo === "professor" && <ProfessorPanel user={user} notify={notify} />}
      {user.tipo === "empresa_parceira" && <CompanyPanel user={user} notify={notify} />}
    </div>
  );
}
