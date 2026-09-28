<!-- README baseado no template do Prof. Dr. João Paulo Aramuni (Lab. de Desenvolvimento de Software). Campos em _itálico_ ou entre [colchetes] devem ser preenchidos/adaptados pelo grupo. -->

---

# 🪙 Sistema de Moeda Estudantil 👨‍💻

> [!NOTE]
> Plataforma que estimula o **reconhecimento do mérito estudantil** por meio de uma **moeda virtual**: professores distribuem moedas aos alunos e os alunos as trocam por **vantagens em empresas parceiras**.
> 🖼️ _Crie uma logo para o projeto e substitua a imagem ao lado._

<table>
  <tr>
    <td width="800px">
      <div align="justify">
        O <b>Sistema de Moeda Estudantil</b> conecta <b>professores</b>, <b>alunos</b> e <b>empresas parceiras</b> em um ciclo de reconhecimento: cada professor recebe <b>1.000 moedas por semestre</b> (com saldo acumulável) para premiar bom comportamento e participação em aula; os alunos acumulam essas moedas e as trocam por <b>descontos e produtos</b> cadastrados pelas empresas. Cada troca gera um <b>cupom com código único</b>, enviado por e-mail ao aluno e ao parceiro. Este repositório reúne a <b>modelagem UML</b>, a <b>documentação</b> e o <b>código</b> da <b>Release 1</b>, desenvolvido em <b>arquitetura MVC</b> na disciplina de Laboratório de Desenvolvimento de Software.
      </div>
    </td>
    <td>
      <div>
        <img src="https://joaopauloaramuni.github.io/image/logo_ES_vertical.png" alt="Logo do Projeto" width="120px"/>
      </div>
    </td>
  </tr> 
</table>

---

## 🚧 Status do Projeto

🟡 **Em desenvolvimento** — Sprint atual: **Lab03S01 (Modelagem)**

[![Versão](https://img.shields.io/badge/Versão-v0.1.0-blue)](https://github.com/SEU-USUARIO/sistema-moeda-estudantil/releases)
[![Sprint](https://img.shields.io/badge/Sprint-Lab03S01-orange)](docs/sprints/lab03s01.md)
[![Modelagem](https://img.shields.io/badge/Modelagem-PlantUML-green)](docs/diagramas)
[![Arquitetura](https://img.shields.io/badge/Arquitetura-MVC-blueviolet)](#-arquitetura)
[![Licença](https://img.shields.io/github/license/SEU-USUARIO/sistema-moeda-estudantil)](#-licença)

![GitHub last commit](https://img.shields.io/github/last-commit/SEU-USUARIO/sistema-moeda-estudantil?style=for-the-badge&logo=clockify) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/SEU-USUARIO/sistema-moeda-estudantil?style=for-the-badge&color=007ec6&logo=gitkraken) ![GitHub repo size](https://img.shields.io/github/repo-size/SEU-USUARIO/sistema-moeda-estudantil?style=for-the-badge&logo=files)

> 🔁 Substitua `SEU-USUARIO` pelo usuário/organização do GitHub do grupo.

---

## 📚 Índice
- [Links Úteis](#-links-úteis)
- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Arquitetura](#-arquitetura)
  - [Diagramas UML](#diagramas-uml)
  - [Mapeamento Componentes × MVC](#mapeamento-componentes--mvc)
- [Instalação e Execução](#-instalação-e-execução)
  - [Pré-requisitos](#pré-requisitos)
  - [Variáveis de Ambiente](#-variáveis-de-ambiente)
  - [Instalação de Dependências](#-instalação-de-dependências)
  - [Inicialização do Banco de Dados](#-inicialização-do-banco-de-dados)
  - [Como Executar a Aplicação](#-como-executar-a-aplicação)
  - [Execução Local Completa com Docker Compose](#-execução-local-completa-com-docker-compose-incluindo-banco-de-dados)
- [Deploy](#-deploy)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Demonstração](#-demonstração)
  - [Aplicação Web](#-aplicação-web)
  - [Exemplo de saída no Terminal](#-exemplo-de-saída-no-terminal-para-back-end-api-cli)
- [Testes](#-testes)
- [Documentações utilizadas](#-documentações-utilizadas)
- [Autores](#-autores)
- [Contribuição](#-contribuição)
- [Agradecimentos](#-agradecimentos)
- [Transparência sobre uso de IA](#-transparência-sobre-uso-de-ia)
- [Licença](#-licença)

---

## 🔗 Links Úteis
* 📦 **Repositório:** [github.com/SEU-USUARIO/sistema-moeda-estudantil](https://github.com/SEU-USUARIO/sistema-moeda-estudantil)
  > 💻 **Descrição:** Repositório oficial do grupo, com todas as versões dos modelos UML e do código.
* 🌐 **Demo Online:** _[link-da-demo-web]_ (a definir, se houver deploy)
  > 💻 **Descrição:** Link para a aplicação em ambiente de produção.
* 📖 **Documentação:** [`docs/`](docs/)
  > 📚 **Descrição:** [Requisitos e regras de negócio](docs/requisitos.md) · [Histórias do Usuário](docs/historias-de-usuario.md) · [Diagramas UML](docs/diagramas/) · [Guia da Sprint Lab03S01](docs/sprints/lab03s01.md)

---

## 📝 Sobre o Projeto

**Por que existe:** valorizar o mérito e o engajamento dos estudantes de forma tangível, criando um mecanismo simples de reconhecimento entre professores e alunos.

**Qual problema resolve:** professores não dispõem de uma forma estruturada e rastreável de reconhecer bom comportamento e participação; alunos não têm retorno concreto por esse esforço. A moeda virtual cria esse elo, e as empresas parceiras ganham visibilidade ao oferecer vantagens.

**Contexto:** projeto acadêmico da disciplina de **Laboratório de Desenvolvimento de Software** (Lab03, Release 1), desenvolvido em três sprints.

**Onde pode ser utilizado:** instituições de ensino participantes (pré-cadastradas), com professores, alunos e empresas parceiras interagindo pela plataforma.

### Perfis de usuário

| Perfil | Como entra no sistema | Principais ações |
|--------|-----------------------|------------------|
| **Aluno** | Auto-cadastro (nome, e-mail, CPF, RG, endereço, instituição e curso) | Receber moedas, consultar extrato, trocar moedas por vantagens |
| **Professor** | Pré-cadastrado a partir da lista enviada pela instituição | Enviar moedas a alunos (com motivo obrigatório), consultar extrato |
| **Empresa Parceira** | Auto-cadastro | Cadastrar vantagens (descrição, foto e custo), conferir trocas pelo código |

### Regras-chave
- Cada professor recebe **1.000 moedas por semestre**; o saldo **acumula** entre semestres.
- O envio exige **saldo suficiente** e **motivo** (mensagem obrigatória).
- O aluno é **notificado por e-mail** ao receber moedas.
- Na troca, o custo é **descontado do saldo** e um **e-mail com o mesmo código** é enviado ao aluno (cupom) e à empresa (conferência).
- Todos os perfis exigem **login e senha** (autenticação obrigatória).

> Regras completas: [`docs/requisitos.md`](docs/requisitos.md)

### 📅 Roadmap de Sprints

| Sprint | Pontos | Entregas | Status |
|--------|--------|----------|--------|
| **Lab03S01** | 6 | Casos de Uso, Histórias do Usuário, Diagrama de Classes, Diagrama de Componentes | 🟡 Em andamento |
| **Lab03S02** | 7 | Modelo ER, estratégia de acesso a dados (ORM/DAO), CRUD inicial de aluno e empresa parceira | ⚪ Pendente |
| **Lab03S03** | 7 | CRUD final, apresentação da arquitetura e persistência, tutorial das tecnologias (~20 min) | ⚪ Pendente |

---

## ✨ Funcionalidades Principais

- 🔐 **Autenticação Segura:** login com senha para aluno, professor e empresa parceira.
- 📝 **Cadastro:** auto-cadastro de alunos (com seleção de instituição pré-cadastrada) e de empresas parceiras.
- 🪙 **Distribuição de Moedas:** professor envia moedas a alunos com motivo obrigatório e validação de saldo.
- 🔄 **Crédito Semestral:** 1.000 moedas por semestre ao professor, com acúmulo do saldo restante.
- 📨 **Notificações por E-mail:** aviso ao aluno ao receber moedas e envio do cupom de troca.
- 📊 **Extrato:** saldo e histórico de transações (envios, recebimentos e trocas).
- 🎁 **Catálogo de Vantagens:** empresas cadastram vantagens com descrição, foto e custo em moedas.
- 🎟️ **Troca com Cupom:** desconto do saldo, geração de código único e conferência pela empresa parceira.

---

## 🛠 Tecnologias Utilizadas

> 🚧 _Stack a ser definida pelo grupo. Preencha conforme as decisões tomadas (a escolha também será apresentada no tutorial da Sprint 03)._

### 💻 Front-end

* **Framework/Biblioteca:** _[Ex: React, Thymeleaf, Angular]_
* **Linguagem/Superset:** _[Ex: TypeScript, JavaScript ES6+]_
* **Estilização:** _[Ex: Tailwind CSS, Bootstrap, Material UI]_
* **Build Tool:** _[Ex: Vite, Webpack]_

### 🖥️ Back-end

* **Linguagem/Runtime:** _[Ex: Java 17, Node.js 20, Python 3.11]_
* **Framework:** _[Ex: Spring Boot, NestJS, Django]_
* **Banco de Dados:** _[Ex: PostgreSQL, MySQL]_
* **ORM / Query Builder:** _[Ex: Hibernate/JPA, Prisma, TypeORM]_
* **Autenticação:** _[Ex: JWT, Spring Security]_
* **E-mail:** _[Ex: JavaMail, Nodemailer, SendGrid]_

### 🧩 Modelagem e Documentação

* **UML:** [PlantUML](https://plantuml.com/) (casos de uso, classes, componentes e sequência)
* **Versionamento:** Git / GitHub

### ⚙️ Infraestrutura & DevOps (opcional)

* **Containerização:** _[Ex: Docker, Docker Compose]_
* **CI/CD:** _[Ex: GitHub Actions]_

---

## 🏗 Arquitetura

O sistema segue o padrão **MVC (Model-View-Controller)**, com uma camada de **Service** para regras de negócio e uma camada de **Repository** (DAO/ORM, definida na Sprint 02) para persistência.

- **Model:** entidades de domínio (`Usuario`, `Aluno`, `Professor`, `EmpresaParceira`, `InstituicaoEnsino`, `Vantagem`, `Transacao`, `EnvioMoeda`, `TrocaVantagem`).
- **View:** telas de login, cadastro, envio de moedas, extrato, catálogo de vantagens e troca.
- **Controller:** recebe as requisições e orquestra os casos de uso.
- **Service:** regras de saldo, crédito semestral, geração do código do cupom e notificações.
- **Repository:** acesso ao banco de dados.

**Decisões de modelagem importantes**
- `Transacao` é **abstrata**, com as especializações `EnvioMoeda` (professor → aluno, com motivo) e `TrocaVantagem` (aluno → vantagem, com código), pois têm participantes e regras diferentes.
- `EmpresaParceira` **herda de `Usuario`** para reaproveitar a autenticação.
- O **extrato** é a lista de `Transacao` do usuário.
- O acúmulo semestral é feito por `Professor.creditarSemestre()`, que soma 1.000 ao saldo existente.

### Diagramas UML

Os fontes estão em [`docs/diagramas/`](docs/diagramas/) (`.puml`) e as imagens geradas em `docs/diagramas/img/`.

| Diagrama de Casos de Uso | Diagrama de Classes |
| :---: | :---: |
| <img src="docs/diagramas/img/casos-de-uso.png" alt="Diagrama de Casos de Uso" width="450px"> | <img src="docs/diagramas/img/diagrama-de-classes.png" alt="Diagrama de Classes" width="450px"> |
| [`casos-de-uso.puml`](docs/diagramas/casos-de-uso.puml) | [`diagrama-de-classes.puml`](docs/diagramas/diagrama-de-classes.puml) |
| **Diagrama de Componentes** | **Sequência: Enviar Moedas** |
| <img src="docs/diagramas/img/diagrama-de-componentes.png" alt="Diagrama de Componentes" width="450px"> | <img src="docs/diagramas/img/sequencia-enviar-moedas.png" alt="Sequência de envio de moedas" width="450px"> |
| [`diagrama-de-componentes.puml`](docs/diagramas/diagrama-de-componentes.puml) | [`sequencia-enviar-moedas.puml`](docs/diagramas/sequencia-enviar-moedas.puml) |
| **Sequência: Trocar Vantagem** | **Modelo ER** |
| <img src="docs/diagramas/img/sequencia-trocar-vantagem.png" alt="Sequência de troca de vantagem" width="450px"> | _Sprint Lab03S02_ |
| [`sequencia-trocar-vantagem.puml`](docs/diagramas/sequencia-trocar-vantagem.puml) | — |

Histórias do Usuário: [`docs/historias-de-usuario.md`](docs/historias-de-usuario.md)

### Mapeamento Componentes × MVC

| Componente (UML) | Responsabilidade | Camadas MVC |
|------------------|------------------|-------------|
| Módulo de Autenticação | Login e validação de senha de todos os perfis | controller + service + model (`Usuario`) |
| Módulo de Cadastro | Cadastro de aluno, empresa e carga de professores | controller + service + model |
| Módulo de Moedas | Envio, extrato, regras de saldo, crédito semestral | controller + service + model (`Transacao`, `EnvioMoeda`) |
| Módulo de Vantagens | Cadastro de vantagens, troca e geração de cupom | controller + service + model (`Vantagem`, `TrocaVantagem`) |
| Módulo de Notificação | Envio de e-mails (moeda recebida e cupom) | service (integração SMTP) |

**Trade-offs / limitações:** _[preencher: ex. saldo armazenado na entidade vs. derivado das transações; e-mails síncronos vs. assíncronos]_

---

## 🔧 Instalação e Execução

> 🚧 _Seção a ser preenchida a partir da Sprint 02, quando houver código executável. Abaixo, o esqueleto do template para adaptar à stack escolhida._

### Pré-requisitos
* **[Linguagem/Runtime]:** _versão_
* **Gerenciador de Pacotes / Build:** _[npm, Maven, Gradle, pip...]_
* **Banco de Dados:** _[PostgreSQL, MySQL...]_
* **Docker** (opcional, recomendado para o banco de dados)

---

### 🔑 Variáveis de Ambiente

Crie um arquivo `.env` (ou configure no sistema) com as variáveis abaixo. **Nunca versione segredos**; mantenha um `.env.example` sem valores sensíveis.

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `SERVER_PORT` | Porta do back-end. | `8080` |
| `DB_URL` | URL de conexão com o banco. | `jdbc:postgresql://localhost:5432/moeda_estudantil` |
| `DB_USER` | Usuário do banco. | `postgres` |
| `DB_PASSWORD` | Senha do banco. | `senha-segura-123` |
| `JWT_SECRET` | Segredo para assinatura de tokens (se aplicável). | `chave_super_segura_base64` |
| `MAIL_HOST` | Servidor SMTP para envio de e-mails. | `smtp.gmail.com` |
| `MAIL_PORT` | Porta SMTP. | `587` |
| `MAIL_USER` | Usuário/conta de e-mail remetente. | `noreply@exemplo.com` |
| `MAIL_PASSWORD` | Senha/app password do e-mail. | `sua_senha_aqui` |
| `API_URL` (front-end) | URL base da API consumida pelo front-end. | `http://localhost:8080/api` |

---

### 📦 Instalação de Dependências

1. **Clone o repositório:**

```bash
git clone https://github.com/SEU-USUARIO/sistema-moeda-estudantil.git
cd sistema-moeda-estudantil
```

2. **Instale as dependências** _(ajuste à stack escolhida)_:

```bash
# Exemplo Node.js
npm install

# Exemplo Maven
./mvnw clean install
```

---

### 💾 Inicialização do Banco de Dados

_Exemplo com PostgreSQL via Docker:_

```bash
docker run --name moeda_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=senha-segura-123 -e POSTGRES_DB=moeda_estudantil -p 5432:5432 -d postgres:16
```

**Migrações:** _[descrever se o schema é gerado pelo ORM (ex.: Hibernate ddl-auto) ou por Flyway/Liquibase/scripts SQL]_

**Carga inicial:** as **instituições** e os **professores** são pré-cadastrados; descreva aqui o script/seed que popula esses dados.

---

### ⚡ Como Executar a Aplicação

```bash
# _[comando de execução do back-end]_
# _[comando de execução do front-end, se separado]_
```
🚀 *A aplicação estará disponível em **http://localhost:8080** (ajuste conforme a stack).*

---

#### 🐳 Execução Local Completa com Docker Compose (Incluindo Banco de Dados)

> _Opcional. Preencha se o grupo adotar Docker Compose._

```bash
docker-compose up --build -d
docker ps
docker-compose down
```

---

## 🚀 Deploy

_[Descrever build de produção, variáveis do ambiente e comando de execução, caso o grupo faça deploy.]_

```bash
# Exemplo genérico
# 1. build do projeto
# 2. configurar variáveis de ambiente no provedor
# 3. executar o artefato gerado
```

---

## 📂 Estrutura de Pastas

```
.
├── .gitignore                    # 🧹 Ignora arquivos não versionados (.env, builds, plantuml.jar...).
├── README.md                     # 📘 Documentação principal do projeto.
├── LICENSE                       # ⚖️ Licença do projeto (a adicionar).
│
├── /docs                         # 📚 Documentação e modelagem
│   ├── requisitos.md             # 📋 Regras de negócio, requisitos e premissas.
│   ├── historias-de-usuario.md   # 🧑‍💼 Histórias do Usuário + rastreabilidade com casos de uso.
│   ├── /diagramas                # 🧩 Diagramas UML (PlantUML)
│   │   ├── casos-de-uso.puml
│   │   ├── diagrama-de-classes.puml
│   │   ├── diagrama-de-componentes.puml
│   │   ├── sequencia-enviar-moedas.puml
│   │   ├── sequencia-trocar-vantagem.puml
│   │   ├── README.md             # ℹ️ Como visualizar/gerar os diagramas.
│   │   └── /img                  # 🖼️ Imagens geradas (PNG).
│   └── /sprints
│       └── lab03s01.md           # ✅ Checklist e roteiro de commits da sprint.
│
├── /scripts
│   └── gerar-diagramas.sh        # 🛠️ Gera os PNGs dos diagramas PlantUML.
│
└── /src                          # 💻 Código-fonte (MVC) — a partir da Sprint 02
    ├── /model                    # 🧬 Entidades de domínio.
    ├── /view                     # 🎨 Telas / front-end.
    ├── /controller               # 🎮 Controladores (requisições e casos de uso).
    ├── /service                  # ⚙️ Regras de negócio (saldo, cupom, e-mail).
    └── /repository               # 🗄️ Acesso a dados (DAO/ORM).
```

---

## 🎥 Demonstração

> [!WARNING]
> Dê preferência a hospedar suas imagens em um **CDN** ou no **GitHub Pages** para que carreguem rapidamente e não quebrem.

### 🌐 Aplicação Web

| Tela | Captura de Tela |
| :---: | :---: |
| **Login** | **Cadastro de Aluno** |
| _Sua imagem aqui_ | _Sua imagem aqui_ |
| **Cadastro de Empresa Parceira** | **Cadastro de Vantagem** |
| _Sua imagem aqui_ | _Sua imagem aqui_ |
| **Envio de Moedas (Professor)** | **Extrato (Aluno/Professor)** |
| _Sua imagem aqui_ | _Sua imagem aqui_ |
| **Catálogo e Troca de Vantagens** | **Cupom / E-mail de Troca** |
| _Sua imagem aqui_ | _Sua imagem aqui_ |

### 💻 Exemplo de Saída no Terminal (para Back-end, API, CLI)

> _Exemplo ilustrativo. Ajuste rotas e campos à API real do grupo._

```bash
curl -X POST 'http://localhost:8080/api/moedas/enviar' \
     -H 'Authorization: Bearer <jwt-do-professor>' \
     -H 'Content-Type: application/json' \
     -d '{"alunoId": 12, "quantidade": 50, "motivo": "Excelente participação em aula"}'
```

**Saída Esperada:**
```json
{
  "id": 301,
  "tipo": "ENVIO_MOEDA",
  "professorId": 3,
  "alunoId": 12,
  "quantidade": 50,
  "motivo": "Excelente participação em aula",
  "saldoProfessor": 950
}
```

---

## 🧪 Testes

> 🚧 _A preencher a partir da Sprint 02._

### Testes Unitários e de Integração
```
# _[comando de testes da stack escolhida]_
```
*Ferramenta utilizada: _[JUnit, Jest, PyTest, ...]_*

**Cenários prioritários:** envio com saldo insuficiente, envio sem motivo, crédito semestral acumulando saldo, troca com saldo insuficiente, geração de código único de cupom, autenticação inválida.

---

## 🔗 Documentações utilizadas

* 📖 **PlantUML:** [Documentação Oficial](https://plantuml.com/)
* 📖 **UML:** [Guia de Diagramas UML](https://www.uml-diagrams.org/)
* 📖 **Guia de Estilo:** [**Conventional Commits**](https://www.conventionalcommits.org/en/v1.0.0/)
* 📖 **Documentação Interna:** [Requisitos](docs/requisitos.md) · [Histórias do Usuário](docs/historias-de-usuario.md)
* 📖 _[Framework/ORM/banco escolhidos pelo grupo]_

---

## 👥 Autores

**Professor:** _Nome do professor_

| 👤 Nome | 🖼️ Foto | :octocat: GitHub | 💼 LinkedIn | 📤 Gmail |
|---------|----------|-----------------|-------------|-----------|
| Nome 1  | <div align="center"><img src="https://joaopauloaramuni.github.io/image/aramunilogo.png" width="70px" height="70px"></div> | <div align="center"><a href="https://github.com/user1"><img src="https://joaopauloaramuni.github.io/image/github6.png" width="50px" height="50px"></a></div> | <div align="center"><a href="https://www.linkedin.com/in/user1"><img src="https://joaopauloaramuni.github.io/image/linkedin2.png" width="50px" height="50px"></a></div> | <div align="center"><a href="mailto:user1@gmail.com"><img src="https://joaopauloaramuni.github.io/image/gmail3.png" width="50px" height="50px"></a></div> |
| Nome 2  | <div align="center"><img src="https://joaopauloaramuni.github.io/image/aramunilogo.png" width="70px" height="70px"></div> | <div align="center"><a href="https://github.com/user2"><img src="https://joaopauloaramuni.github.io/image/github6.png" width="50px" height="50px"></a></div> | <div align="center"><a href="https://www.linkedin.com/in/user2"><img src="https://joaopauloaramuni.github.io/image/linkedin2.png" width="50px" height="50px"></a></div> | <div align="center"><a href="mailto:user2@gmail.com"><img src="https://joaopauloaramuni.github.io/image/gmail3.png" width="50px" height="50px"></a></div> |
| Nome 3  | <div align="center"><img src="https://joaopauloaramuni.github.io/image/aramunilogo.png" width="70px" height="70px"></div> | <div align="center"><a href="https://github.com/user3"><img src="https://joaopauloaramuni.github.io/image/github6.png" width="50px" height="50px"></a></div> | <div align="center"><a href="https://www.linkedin.com/in/user3"><img src="https://joaopauloaramuni.github.io/image/linkedin2.png" width="50px" height="50px"></a></div> | <div align="center"><a href="mailto:user3@gmail.com"><img src="https://joaopauloaramuni.github.io/image/gmail3.png" width="50px" height="50px"></a></div> |

> [!TIP]
> 💡 **Dica:** Escolha uma foto profissional, preferencialmente de rosto, evitando imagens com baixa qualidade, filtros excessivos ou elementos distrativos.

---

## 🤝 Contribuição

1. Faça um `fork` do projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`).
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade X'`). **(Utilize [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/))**
4. Faça o `push` para a branch (`git push origin feature/minha-feature`).
5. Abra um **Pull Request (PR)**.

> [!IMPORTANT]
> 📝 **Regras:** commits pequenos e frequentes, com mensagens claras (ex.: `docs: adiciona diagrama de casos de uso`). Sempre que um modelo UML for alterado, versione o `.puml` **e** a imagem gerada.

---

## 🙏 Agradecimentos

* [**Engenharia de Software PUC Minas**](https://www.instagram.com/engsoftwarepucminas/) - Pelo apoio institucional, estrutura acadêmica e fomento à inovação e boas práticas de engenharia.
* [**Prof. Dr. João Paulo Aramuni**](https://github.com/joaopauloaramuni) - Pelos valiosos ensinamentos sobre **Arquitetura de Software** e **Padrões de Projeto**.
* _[Adicione outras pessoas, canais e fontes que ajudaram o grupo.]_

---

## 🤖 Transparência sobre uso de IA

Em conformidade com a política de uso responsável de Inteligência Artificial da disciplina, a estrutura-base deste repositório (rascunhos dos diagramas PlantUML, histórias do usuário e README) foi gerada com apoio da ferramenta **Claude (Anthropic)**.

> ✍️ _O grupo deve descrever aqui o que foi gerado com IA, o que foi revisado/alterado e as decisões próprias tomadas._

---

## 📄 Licença

Este projeto é distribuído sob a **Licença MIT**. _(Adicione o arquivo `LICENSE` ou ajuste esta seção conforme a decisão do grupo.)_

---
