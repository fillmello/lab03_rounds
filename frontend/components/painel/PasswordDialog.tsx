"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiRequest, errorText } from "../../lib/api";
import { Notify } from "./types";

const MIN_LENGTH = 8;

export function PasswordDialog({ notify }: { notify: Notify }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [modalError, setModalError] = useState("");

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const current = String(form.get("senha_atual") ?? "");
    const next = String(form.get("nova_senha") ?? "");
    const confirmation = String(form.get("confirmacao") ?? "");
    setModalError("");
    if (next.length < MIN_LENGTH) return setModalError(`A nova senha deve ter no mínimo ${MIN_LENGTH} caracteres.`);
    if (next !== confirmation) return setModalError("A confirmação da nova senha não confere.");
    if (next === current) return setModalError("A nova senha deve ser diferente da atual.");
    setBusy(true);
    try {
      await apiRequest("/me/senha", {
        method: "POST",
        body: JSON.stringify({ senha_atual: current, nova_senha: next, confirmacao: confirmation }),
      });
      setOpen(false); // o formulário é desmontado junto com o modal
      notify("Senha alterada com sucesso.");
    } catch (reason) {
      setModalError(errorText(reason, "Não foi possível alterar a senha."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className="password-card">
        <div>
          <span className="record-id">Segurança da conta</span>
          <h2>Mudar senha</h2>
          <p className="muted">Atualize sua senha usando a senha atual para confirmar sua identidade.</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => { setModalError(""); setOpen(true); }}>
          Mudar senha
        </button>
      </section>
      {open && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setOpen(false); }}>
          <section className="modal panel" role="dialog" aria-modal="true" aria-labelledby="password-title">
            <h2 id="password-title">Mudar senha</h2>
            <p className="muted">Confirme sua senha atual e escolha uma nova senha com no mínimo {MIN_LENGTH} caracteres.</p>
            {modalError && <p className="modal-error" role="alert">{modalError}</p>}
            <form className="form-stack" onSubmit={submit}>
              <PasswordField label="Senha atual" name="senha_atual" autoComplete="current-password" autoFocus />
              <PasswordField label="Nova senha" name="nova_senha" autoComplete="new-password" minLength={MIN_LENGTH} />
              <PasswordField label="Confirmar nova senha" name="confirmacao" autoComplete="new-password" minLength={MIN_LENGTH} />
              <div className="modal-actions">
                <button type="submit" className="full-width-submit" disabled={busy}>{busy ? "Salvando..." : "Salvar nova senha"}</button>
                <button type="button" className="secondary-button full-width-submit" onClick={() => setOpen(false)}>Cancelar</button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  );
}

type PasswordFieldProps = { label: string; name: string; autoComplete: string; minLength?: number; autoFocus?: boolean };

function PasswordField({ label, name, autoComplete, minLength, autoFocus }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false);
  return (
    <label>
      {label}
      <span className="password-input">
        <input name={name} type={visible ? "text" : "password"} autoComplete={autoComplete} minLength={minLength} maxLength={128} autoFocus={autoFocus} required />
        <button type="button" className="visibility-button" aria-pressed={visible} aria-label={`${visible ? "Ocultar" : "Mostrar"} ${label.toLowerCase()}`} onClick={() => setVisible((current) => !current)}>
          {visible ? "Ocultar" : "Visualizar"}
        </button>
      </span>
    </label>
  );
}
