# Requisitos — Sistema de Moeda Estudantil (Release 1)

## Regras de negócio

| ID | Regra |
|----|-------|
| RN01 | Alunos se cadastram informando **nome, e-mail, CPF, RG, endereço, instituição de ensino e curso**. |
| RN02 | As **instituições** são pré-cadastradas; o aluno apenas seleciona a sua. |
| RN03 | **Professores** são pré-cadastrados (lista enviada pela instituição). Armazena-se nome, CPF, departamento e vínculo com a instituição. |
| RN04 | A cada semestre cada professor recebe **1.000 moedas**. |
| RN05 | O saldo do professor é **acumulável** entre semestres (saldo restante + 1.000 novas). |
| RN06 | Para enviar moedas, o professor precisa de **saldo suficiente**, deve indicar o **aluno** e o **motivo** (mensagem aberta, **obrigatória**). |
| RN07 | O aluno é **notificado por e-mail** ao receber moedas. |
| RN08 | Professor e aluno consultam o **extrato** (saldo + transações). Professor: envios. Aluno: recebimentos e trocas. |
| RN09 | Empresas parceiras se cadastram e registram **vantagens** com **descrição, foto e custo em moedas**. |
| RN10 | Ao resgatar uma vantagem, o custo é **descontado do saldo** do aluno (saldo deve ser suficiente). |
| RN11 | O sistema gera um **código único** por troca e envia **e-mail de cupom ao aluno** e **e-mail de conferência à empresa**, ambos com o **mesmo código**. |
| RN12 | Aluno, professor e empresa parceira possuem **login e senha**; toda funcionalidade exige **autenticação**. |

## Requisitos funcionais (resumo)

| ID | Requisito | Ator(es) | Regras |
|----|-----------|----------|--------|
| RF01 | Realizar login | Aluno, Professor, Empresa | RN12 |
| RF02 | Cadastrar aluno | Aluno | RN01, RN02 |
| RF03 | Cadastrar empresa parceira | Empresa | RN09, RN12 |
| RF04 | Enviar moedas a aluno | Professor | RN04–RN07 |
| RF05 | Consultar extrato | Aluno, Professor | RN08 |
| RF06 | Cadastrar vantagem | Empresa | RN09 |
| RF07 | Trocar moedas por vantagem | Aluno | RN10, RN11 |
| RF08 | Conferir troca de vantagem (código) | Empresa | RN11 |
| RF09 | Notificar por e-mail (moeda recebida e cupom) | Sistema | RN07, RN11 |
| RF10 | Creditar 1.000 moedas por semestre ao professor | Sistema | RN04, RN05 |

## Requisitos não funcionais

- Arquitetura **MVC**.
- Autenticação obrigatória em todos os fluxos.
- Persistência em banco de dados (estratégia definida na Sprint 2).
- Modelos UML versionados no repositório.

## Premissas e decisões de modelagem (revisar em grupo)

1. Cadastro do professor (via lista da instituição) é **carga administrativa**, fora do escopo dos atores do sistema nesta release.
2. `Transacao` é abstrata, com especializações `EnvioMoeda` (professor → aluno) e `TrocaVantagem` (aluno → vantagem), pois têm participantes e regras distintos.
3. O código do cupom é atributo de `TrocaVantagem` e é o mesmo enviado aos dois e-mails.
4. Empresa parceira é modelada como especialização de `Usuario` para reaproveitar a autenticação.
5. O crédito semestral é feito por rotina do sistema (`Professor.creditarSemestre()`), somando 1.000 ao saldo existente.
