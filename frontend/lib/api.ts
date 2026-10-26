// Sem NEXT_PUBLIC_API_URL, usa o mesmo host da página (localhost ou 127.0.0.1) para que o
// cookie de sessão seja enviado: hosts diferentes contam como sites diferentes e o cookie é bloqueado.
export function apiUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  const host = typeof window !== "undefined" ? window.location.hostname : "127.0.0.1";
  return `http://${host}:8000/api`;
}

export function apiOrigin(): string {
  return new URL(apiUrl()).origin;
}

function getErrorMessage(body: unknown): string {
  if (typeof body === "string" && body) return body;
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) => (item && typeof item === "object" && "msg" in item ? String((item as { msg: unknown }).msg) : String(item)))
        .join(". ");
    }
  }
  return "Não foi possível concluir a operação.";
}

async function readBody(response: Response): Promise<unknown> {
  // Respostas 204 (logout, trocar senha, remover) não têm corpo.
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiRequest<T = void>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  // Com FormData o navegador define o Content-Type (com o boundary).
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  let response: Response;
  try {
    response = await fetch(`${apiUrl()}${path}`, { ...options, headers, credentials: "include" });
  } catch {
    throw new Error("Não foi possível conectar ao servidor. Verifique se a API está em execução.");
  }
  const body = await readBody(response);
  if (!response.ok) throw new Error(getErrorMessage(body));
  return body as T;
}

export function errorText(reason: unknown, fallback: string): string {
  return reason instanceof Error ? reason.message : fallback;
}
