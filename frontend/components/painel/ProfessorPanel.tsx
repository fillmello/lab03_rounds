"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { apiRequest, errorText } from "../../lib/api";
import { Field } from "./Field";
import { PasswordDialog } from "./PasswordDialog";
import { StatementPanel } from "./StatementPanel";
import { Notify, Professor, Statement, StudentSummary, User } from "./types";

export function ProfessorPanel({ user, notify }: { user: User; notify: Notify }) {
  const [professor, setProfessor] = useState<Professor | null>(null);
  const [statement, setStatement] = useState<Statement | null>(null);
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [busy, setBusy] = useState(true);

  const load = useCallback(async () => {
    try {
      const [profile, extract, list] = await Promise.all([
        apiRequest<Professor>(`/professores/${user.id}`),
        apiRequest<Statement>("/extratos/professor"),
        apiRequest<StudentSummary[]>("/professores/me/alunos"),
      ]);
      setProfessor(profile);
      setStatement(extract);
      setStudents(list);
    } catch (reason) {
      notify(errorText(reason, "Não foi possível carregar seus dados."), true);
    } finally {
      setBusy(false);
    }
  }, [notify, user.id]);
  useEffect(() => { void load(); }, [load]);

  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; // currentTarget vira null depois de um await
    const data = Object.fromEntries(new FormData(form));
    try {
      await apiRequest("/moedas/enviar", {
        method: "POST",
        body: JSON.stringify({ aluno_id: Number(data.aluno_id), quantidade: Number(data.quantidade), motivo: data.motivo }),
      });
      notify("Moedas enviadas com sucesso. O aluno foi avisado por e-mail.");
      form.reset();
      await load();
    } catch (reason) {
      notify(errorText(reason, "Não foi possível enviar moedas."), true);
    }
  }

  if (busy || !professor || !statement) return <p className="loading-state">Carregando seus dados…</p>;
  return (
    <div className="profile-sections">
      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Saldo do professor</h2>
            <p className="muted">Reconheça um aluno da sua instituição. O saldo restante acumula para o próximo semestre.</p>
          </div>
          <strong className="balance">{statement.saldo} moedas</strong>
        </div>
        <form className="form-grid" onSubmit={send}>
          <label>
            Aluno
            <select name="aluno_id" required defaultValue="">
              <option value="" disabled>{students.length ? "Selecione um aluno" : "Nenhum aluno cadastrado na sua instituição"}</option>
              {students.map((item) => <option key={item.id} value={item.id}>{item.nome} · {item.curso}</option>)}
            </select>
          </label>
          <Field label="Quantidade" name="quantidade" type="number" min={1} max={statement.saldo} step={1} />
          <Field label="Motivo do reconhecimento" name="motivo" maxLength={1000} wide />
          <button type="submit" className="full-width-submit" disabled={statement.saldo < 1}>Enviar moedas</button>
        </form>
      </section>
      <PasswordDialog notify={notify} />
      <StatementPanel statement={statement} role="professor" />
    </div>
  );
}
