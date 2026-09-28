# Histórias do Usuário

Formato: **Como** `<ator>`, **eu quero** `<ação>`, **para que** `<benefício>`.

## Autenticação e cadastro

### HU01 — Realizar login
Como **aluno, professor ou empresa parceira**, eu quero entrar no sistema com login e senha, para que somente eu acesse minhas informações e funcionalidades.

**Critérios de aceitação**
- Credenciais válidas dão acesso ao perfil correspondente.
- Credenciais inválidas exibem mensagem de erro sem revelar qual campo está incorreto.
- Funcionalidades protegidas não são acessíveis sem autenticação.

### HU02 — Cadastrar-se como aluno
Como **aluno**, eu quero me cadastrar informando nome, e-mail, CPF, RG, endereço, instituição e curso, para que eu possa participar do sistema de mérito e receber moedas.

**Critérios de aceitação**
- A instituição é escolhida em uma lista pré-cadastrada.
- Todos os campos são obrigatórios; CPF e e-mail não podem estar duplicados.
- Login e senha são definidos no cadastro.

### HU03 — Cadastrar-se como empresa parceira
Como **empresa parceira**, eu quero me cadastrar no sistema, para que eu possa oferecer vantagens aos alunos e ganhar visibilidade.

**Critérios de aceitação**
- Cadastro exige nome, CNPJ, e-mail, login e senha.
- CNPJ e e-mail não podem estar duplicados.

## Moedas

### HU04 — Enviar moedas a um aluno
Como **professor**, eu quero enviar moedas a um aluno informando o motivo, para que eu reconheça seu bom comportamento ou participação em aula.

**Critérios de aceitação**
- O envio só é permitido com saldo suficiente.
- O motivo é obrigatório (não pode ser vazio).
- O saldo do professor é debitado e o do aluno creditado.
- A transação aparece no extrato de ambos.

### HU05 — Ser notificado ao receber moedas
Como **aluno**, eu quero receber um e-mail quando ganhar moedas, para que eu saiba quem me reconheceu e por quê.

**Critérios de aceitação**
- O e-mail informa professor, quantidade e motivo.

### HU06 — Consultar extrato (professor)
Como **professor**, eu quero consultar meu extrato, para que eu saiba meu saldo atual e quais moedas já distribuí.

**Critérios de aceitação**
- Exibe saldo total e lista de envios (aluno, quantidade, motivo, data).

### HU07 — Consultar extrato (aluno)
Como **aluno**, eu quero consultar meu extrato, para que eu acompanhe meu saldo, as moedas recebidas e as trocas realizadas.

**Critérios de aceitação**
- Exibe saldo total e lista de recebimentos e trocas, com data.

### HU08 — Receber moedas semestrais
Como **professor**, eu quero receber 1.000 moedas a cada semestre com acúmulo do saldo restante, para que eu tenha moedas para reconhecer meus alunos ao longo do tempo.

**Critérios de aceitação**
- O crédito soma 1.000 ao saldo atual, sem zerar o saldo anterior.

## Vantagens

### HU09 — Cadastrar vantagem
Como **empresa parceira**, eu quero cadastrar uma vantagem com descrição, foto e custo em moedas, para que os alunos possam trocá-la por suas moedas.

**Critérios de aceitação**
- Descrição, foto e custo (> 0) são obrigatórios.

### HU10 — Trocar moedas por vantagem
Como **aluno**, eu quero trocar minhas moedas por uma vantagem cadastrada, para que eu obtenha descontos ou produtos oferecidos pelas empresas parceiras.

**Critérios de aceitação**
- Só é permitido com saldo suficiente.
- O custo é descontado do saldo do aluno.
- É gerado um código único para a troca.

### HU11 — Receber cupom por e-mail
Como **aluno**, eu quero receber um e-mail com o cupom da troca, para que eu apresente o código presencialmente à empresa.

**Critérios de aceitação**
- O e-mail contém o código gerado e a descrição da vantagem.

### HU12 — Conferir troca de vantagem
Como **empresa parceira**, eu quero receber um e-mail com o mesmo código do cupom e conferi-lo quando o aluno o apresentar, para que eu valide a troca presencial da vantagem.

**Critérios de aceitação**
- O e-mail à empresa contém o mesmo código enviado ao aluno.
- A empresa consegue verificar a validade do código no sistema.

## Rastreabilidade (História → Caso de Uso)

| História | Caso de uso |
|----------|-------------|
| HU01 | UC01 Realizar login |
| HU02, HU03 | UC02 Cadastrar-se |
| HU04, HU05 | UC03 Enviar moedas a um aluno |
| HU06, HU07 | UC04 Consultar extrato |
| HU08 | UC08 Creditar moedas semestrais (Sistema) |
| HU09 | UC06 Cadastrar vantagem |
| HU10, HU11 | UC05 Trocar moedas por vantagem |
| HU12 | UC07 Conferir troca de vantagem |
