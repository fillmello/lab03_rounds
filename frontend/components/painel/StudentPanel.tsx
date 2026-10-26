"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { apiOrigin, apiRequest, errorText } from "../../lib/api";
import { Field } from "./Field";
import { PasswordDialog } from "./PasswordDialog";
import { StatementPanel } from "./StatementPanel";
import { Advantage, Notify, Statement, Student, User, Voucher } from "./types";

export function StudentPanel({ user, notify }: { user: User; notify: Notify }) {
  const [student, setStudent] = useState<Student | null>(null);
  const [statement, setStatement] = useState<Statement | null>(null);
  const [advantages, setAdvantages] = useState<Advantage[]>([]);
  const [busy, setBusy] = useState(true);

  const load = useCallback(async () => {
    try {
      const [profile, extract, items] = await Promise.all([
        apiRequest<Student>(`/alunos/${user.id}`),
        apiRequest<Statement>("/extratos/aluno"),
        apiRequest<Advantage[]>("/vantagens"),
      ]);
      setStudent(profile);
      setStatement(extract);
      setAdvantages(items);
    } catch (reason) {
      notify(errorText(reason, "Não foi possível carregar seus dados."), true);
    } finally {
      setBusy(false);
    }
  }, [notify, user.id]);
  useEffect(() => { void load(); }, [load]);

  async function update(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const payload = Object.fromEntries(Object.entries(data).filter(([, value]) => String(value).trim()));
    try {
      await apiRequest(`/alunos/${user.id}`, { method: "PUT", body: JSON.stringify(payload) });
      notify("Cadastro atualizado com sucesso.");
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível atualizar o cadastro."), true);
    }
  }

  async function redeem(advantage: Advantage) {
    if (!window.confirm(`Resgatar "${advantage.descricao}" por ${advantage.custo_em_moedas} moedas?`)) return;
    try {
      const result = await apiRequest<Voucher>(`/vantagens/${advantage.id}/resgatar`, { method: "POST" });
      notify(`Resgate realizado. Código do cupom: ${result.codigo} (também enviado por e-mail).`);
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível resgatar a vantagem."), true);
    }
  }

  if (busy || !student || !statement) return <p className="loading-state">Carregando seus dados…</p>;
  return (
    <div className="profile-sections">
      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Meu cadastro</h2>
            <p className="muted">Mantenha seus dados atualizados.</p>
          </div>
          <strong className="balance">{statement.saldo} moedas</strong>
        </div>
        <form className="form-grid" onSubmit={update}>
          <Field label="Nome" name="nome" defaultValue={student.nome} />
          <Field label="E-mail" name="email" type="email" defaultValue={student.email} />
          <Field label="Login" name="login" defaultValue={student.login} />
          <Field label="Curso" name="curso" defaultValue={student.curso} />
          <Field label="RG" name="rg" defaultValue={student.rg} />
          <Field label="Endereço" name="endereco" defaultValue={student.endereco} wide />
          <button type="submit" className="full-width-submit">Salvar cadastro</button>
        </form>
      </section>
      <PasswordDialog notify={notify} />
      <section className="panel">
        <h2>Vantagens disponíveis</h2>
        <p className="muted">Use suas moedas para resgatar benefícios.</p>
        <div className="record-list">
          {advantages.map((item) => (
            <article className="record-card" key={item.id}>
              <div className="record-media">
                {item.foto_url && <img className="thumb" src={`${apiOrigin()}${item.foto_url}`} alt={item.descricao} />}
                <div>
                  <span className="record-id">{item.empresa_nome}</span>
                  <h3>{item.descricao}</h3>
                  <p>{item.custo_em_moedas} moedas</p>
                </div>
              </div>
              <button type="button" onClick={() => void redeem(item)} disabled={statement.saldo < item.custo_em_moedas}>Resgatar</button>
            </article>
          ))}
          {advantages.length === 0 && <p className="empty-state">Nenhuma vantagem disponível.</p>}
        </div>
      </section>
      <StatementPanel statement={statement} role="aluno" />
    </div>
  );
}
