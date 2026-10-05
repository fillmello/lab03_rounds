# Requisitos — Sistema de Moeda Estudantil (Release 1)

## Requisitos Funcionais

- **RF01** — O sistema deve permitir que alunos, professores e empresas parceiras realizem login.
- **RF02** — O sistema deve permitir que o aluno se cadastre informando nome, e-mail, CPF, RG, endereço, instituição de ensino e curso.
- **RF03** — O sistema deve permitir que a empresa parceira se cadastre informando seus dados e credenciais de acesso.
- **RF04** — O sistema deve permitir que o professor envie moedas a um aluno, informando quantidade, destinatário e motivo obrigatório.
- **RF05** — O sistema deve permitir que alunos e professores consultem saldo e extrato de transações.
- **RF06** — O sistema deve permitir que a empresa parceira cadastre vantagens com descrição, foto e custo em moedas.
- **RF07** — O sistema deve permitir que o aluno troque moedas por uma vantagem, descontando o custo do seu saldo.
- **RF08** — O sistema deve permitir que a empresa parceira confira uma troca por meio do código do cupom.
- **RF09** — O sistema deve enviar notificações por e-mail ao aluno quando ele receber moedas e ao aluno e à empresa quando houver uma troca.
- **RF10** — O sistema deve gerar um código único para cada troca e enviar o mesmo código ao aluno e à empresa parceira.
- **RF11** — O sistema deve creditar 1.000 moedas ao professor a cada semestre, acumulando o saldo restante.

## Requisitos Não Funcionais

- **RNF01** — O sistema deve utilizar arquitetura **MVC**.
- **RNF02** — O sistema deve exigir autenticação nos fluxos protegidos.
- **RNF03** — O sistema deve persistir os dados em banco de dados; a estratégia será definida na Sprint 2.
- **RNF04** — Os modelos UML devem ser versionados no repositório.
- **RNF05** — O sistema deve representar `Usuario` como classe abstrata de autenticação, com `Aluno`, `Professor` e `EmpresaParceira` como especializações.
- **RNF06** — O sistema deve representar `Transacao` como classe abstrata, especializada em `EnvioMoeda` e `TrocaVantagem`.
