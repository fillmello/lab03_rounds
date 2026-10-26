import { Statement } from "./types";

// A API devolve datas em UTC sem fuso; sem o "Z" o navegador as leria como horário local.
function formatDate(value: string): string {
  return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`).toLocaleString("pt-BR");
}

type Row = { key: string; date: string; title: string; detail: string; amount: number };

export function StatementPanel({ statement, role }: { statement: Statement; role: "aluno" | "professor" }) {
  const rows: Row[] = [
    ...statement.envios.map((item): Row =>
      role === "professor"
        ? { key: `e-${item.id}`, date: item.data, title: `Enviado para ${item.aluno_nome}`, detail: item.motivo, amount: -item.quantidade }
        : { key: `e-${item.id}`, date: item.data, title: `Recebido de ${item.professor_nome}`, detail: item.motivo, amount: item.quantidade }),
    ...statement.trocas.map((item): Row => ({
      key: `t-${item.id}`, date: item.data, title: `Resgate: ${item.vantagem_descricao}`, detail: `Cupom ${item.codigo}`, amount: -item.quantidade,
    })),
  ].sort((a, b) => b.date.localeCompare(a.date));

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <h2>Extrato</h2>
          <p className="muted">Movimentações recentes.</p>
        </div>
        <strong className="balance">{statement.saldo} moedas</strong>
      </div>
      <div className="statement-list">
        {rows.map((row) => (
          <div className="statement-row" key={row.key}>
            <span>
              {row.title}
              <small>{row.detail} · {formatDate(row.date)}</small>
            </span>
            <strong>{row.amount > 0 ? "+" : ""}{row.amount}</strong>
          </div>
        ))}
        {rows.length === 0 && <p className="empty-state">Nenhuma movimentação ainda.</p>}
      </div>
    </section>
  );
}
