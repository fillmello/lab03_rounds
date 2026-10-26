# Arquitetura e tecnologias — Sistema de Moeda Estudantil

## 1. Visão geral

Professores distribuem moedas a alunos; alunos trocam moedas por vantagens de empresas parceiras. Três perfis (aluno, professor, empresa parceira) entram por login e senha.

```
Next.js (View)  ──fetch + cookie──▶  FastAPI  ──SQLAlchemy──▶  SQLite / PostgreSQL
                                        │
                                        └──smtplib──▶ SMTP (Mailtrap)
```

## 2. Componentes × camadas (MVC)

| Componente (diagrama da Sprint 1) | Controller | Service | Model / Repository |
|---|---|---|---|
| Autenticação | `controller/auth.py`, `deps.py` | `service/auth.py`, `throttle.py`, `usuarios.py` | `Usuario` |
| Cadastro | `alunos.py`, `empresas.py`, `admin.py` | `service/usuarios.py` | `Aluno`, `EmpresaParceira`, `Professor`, `InstituicaoEnsino` |
| Moedas | `moedas.py`, `professores.py` | `service/moedas.py`, `semestre.py` | `EnvioMoeda` |
| Vantagens | `vantagens.py` | `service/moedas.py`, `fotos.py` | `Vantagem`, `TrocaVantagem` |
| Notificação | (chamada pelos controllers) | `service/notificacao.py` | — |

O controller só recebe a requisição, valida permissão e delega; as regras (saldo, mesma instituição, crédito semestral, código do cupom) ficam no service; as consultas, em `repository/repositories.py`. A View é o front-end Next.js.

## 3. Persistência

- **Estratégia:** ORM com SQLAlchemy 2 (sem DAO manual). Tabelas criadas por `create_all` ao iniciar.
- **Herança de `Usuario`:** tabela base `usuario` (com a coluna `tipo`) e tabelas `aluno`, `professor` e `empresa_parceira` ligadas pela mesma chave primária (*joined table inheritance*).
- **Transações:** `EnvioMoeda` e `TrocaVantagem` têm tabelas próprias; o saldo fica em `aluno` e `professor` e é atualizado na mesma transação do registro.
- **Integridade:** chaves estrangeiras ativadas no SQLite (`PRAGMA foreign_keys=ON`), o que impede remover alunos ou vantagens com histórico.
- Modelo ER: [`diagramas/modelo-er.puml`](diagramas/modelo-er.puml).

## 4. O que mudou desde a modelagem inicial

| Modelado | Implementado | Motivo |
|---|---|---|
| Professores "pré-cadastrados" sem ator responsável | Área `/admin` (token) cadastra instituições e professores, individualmente ou por lista | Faltava quem fizesse o pré-cadastro; empresas não devem criar professores com moedas |
| `Transacao` abstrata | Duas tabelas independentes, sem tabela `transacao` | Participantes e regras diferentes; extrato une as duas listas |
| Foto da vantagem como atributo | Upload de JPG/PNG (até 2 MB) salvo em `uploads/` | Atende o requisito sem depender de hospedagem externa |
| Autenticação genérica | Cookie HttpOnly assinado com expiração; senhas PBKDF2 com salt; bloqueio após 5 falhas | Segurança; trocar a senha derruba as outras sessões |
| Crédito semestral por `creditarSemestre()` | `service/semestre.py`, aplicado ao iniciar e quando o professor usa o sistema | O saldo acumula e não depende de reiniciar a API |

## 5. Tecnologias

### FastAPI
- **O que é:** framework web Python com validação por tipos (Pydantic) e documentação automática em `/docs`.
- **Por que:** pouco código para uma API REST, validação de entrada embutida e testes simples com `TestClient`.
- **Demo:** abrir `http://localhost:8000/docs`, fazer `POST /api/login` e depois `POST /api/moedas/enviar`.
- **Dificuldades:** respostas `204` não têm corpo (o front precisa tratá-las); mensagens de validação vêm em inglês, então há um handler que as traduz.

### SQLAlchemy 2
- **O que é:** ORM que mapeia classes Python para tabelas.
- **Por que:** mapeia a herança de `Usuario` e troca SQLite por PostgreSQL só com `DATABASE_URL`.
- **Demo:** `src/model/entities.py` define as tabelas; `repository/repositories.py` faz as consultas.
- **Dificuldades:** o SQLite ignora chaves estrangeiras por padrão; foi preciso ativá-las.

### Next.js + React + TypeScript
- **O que é:** framework React com roteamento por pastas; o TypeScript tipa as respostas da API.
- **Por que:** páginas separadas por perfil e componentes reutilizáveis (`components/painel`).
- **Demo:** cadastrar um aluno em `/cadastro/aluno`, entrar e abrir "Mudar senha" no painel.
- **Dificuldades:** o cookie de sessão só é enviado se front e API usarem o mesmo host (`localhost` ≠ `127.0.0.1`); `event.currentTarget` fica `null` depois de um `await`.

### pytest
- **O que é:** framework de testes Python.
- **Por que:** cada cenário BDD crítico ganha ao menos um teste automatizado.
- **Demo:** `python -m pytest -q`.
