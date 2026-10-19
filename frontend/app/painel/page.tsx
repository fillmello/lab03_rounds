"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useState } from "react";
import { apiRequest } from "../../lib/api";

export default function DashboardPage() {
  return <Suspense fallback={<div className="dashboard"><p>Carregando painel...</p></div>}><DashboardContent /></Suspense>;
}

function DashboardContent() {
  const params = useSearchParams();
  const [type, setType] = useState("alunos");
  const [id, setId] = useState("");
  const [result, setResult] = useState("Os dados aparecerão aqui.");

  async function lookup() {
    if (!id) { setResult("Informe um ID válido."); return; }
    try { setResult(JSON.stringify(await apiRequest(`/${type}/${id}`), null, 2)); }
    catch (reason) { setResult(reason instanceof Error ? reason.message : "Cadastro não encontrado."); }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-top">
        <div>
          <span className="eyebrow">Área de consulta</span>
          <h1>Olá, {params.get("nome") || "visitante"}.</h1>
          <p>Consulte os cadastros disponíveis.</p>
        </div>
        <Link href="/login" className="secondary-button">Sair</Link>
      </div>
      <section className="panel">
        <h2>Consultar cadastro</h2>
        <div className="lookup-grid">
          <label>Tipo<select value={type} onChange={(event) => setType(event.target.value)}><option value="alunos">Aluno</option><option value="empresas">Empresa</option></select></label>
          <label>ID<input type="number" min="1" value={id} onChange={(event) => setId(event.target.value)} /></label>
          <button type="button" onClick={lookup}>Consultar</button>
        </div>
        <pre className="result">{result}</pre>
      </section>
    </div>
  );
}
