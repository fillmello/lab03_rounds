export type User = { id: number; nome: string; tipo: "aluno" | "professor" | "empresa_parceira" };
export type Notify = (message: string, error?: boolean) => void;

export type Student = { id: number; nome: string; email: string; login: string; cpf: string; rg: string; endereco: string; curso: string; instituicao_id: number; saldo: number };
export type StudentSummary = { id: number; nome: string; curso: string };
export type Professor = { id: number; nome: string; email: string; login: string; cpf: string; departamento: string; instituicao_id: number; saldo: number };
export type Company = { id: number; nome: string; email: string; login: string; cnpj: string };
export type Institution = { id: number; nome: string };
export type Advantage = { id: number; descricao: string; custo_em_moedas: number; empresa_id: number; empresa_nome: string; foto_url: string | null };

export type Shipment = { id: number; data: string; quantidade: number; motivo: string; professor_id: number; professor_nome: string; aluno_id: number; aluno_nome: string };
export type Redemption = { id: number; data: string; quantidade: number; codigo: string; aluno_id: number; aluno_nome: string; vantagem_id: number; vantagem_descricao: string };
export type Statement = { saldo: number; envios: Shipment[]; trocas: Redemption[] };
export type Voucher = { codigo: string; quantidade: number; vantagem_id: number; saldo_restante: number };
