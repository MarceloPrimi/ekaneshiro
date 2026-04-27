# SGK — Sistema de Gestão Kaneshiro

Sistema web completo para gestão de salão de beleza: agendamentos, clientes, profissionais, serviços, produtos, pagamentos e relatórios — com integração ao Google Calendar e Google Sheets.

---

## Funcionalidades

- **Agendamentos** — criação, edição, confirmação, conclusão e cancelamento; status em tempo real
- **Clientes** — cadastro completo com histórico de agendamentos
- **Profissionais** — gerenciamento de equipe com vinculação de serviços e agenda Google Calendar
- **Serviços** — catálogo com duração e preço por serviço
- **Produtos** — controle de estoque com categorias
- **Pagamentos** — registro de pagamentos por agendamento
- **Relatórios** — visão consolidada de receita (restrito a admins)
- **Usuários** — controle de acesso com três perfis: `admin`, `recepcionista` e `profissional`
- **Google Calendar** — cada profissional pode ter uma agenda individual sincronizada
- **Google Sheets** — exportação automática de agendamentos e pagamentos em abas mensais (`Ag-YYYY-MM` / `Pag-YYYY-MM`)

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 · FastAPI · Uvicorn |
| ORM / Migrations | SQLAlchemy 2 · Alembic |
| Banco de dados | MySQL (via PyMySQL) |
| Autenticação | JWT (python-jose · passlib) |
| Frontend | Vue 3 · Vite · Pinia · Vue Router |
| Estilo | Tailwind CSS |
| Calendário UI | FullCalendar |
| Integrações | Google Calendar API · Google Sheets API |

---

## Estrutura do projeto

```
├── main.py                  # Entrypoint FastAPI
├── alembic/                 # Migrations do banco
├── api/                     # Routers (endpoints REST)
├── core/                    # Configurações e segurança (JWT)
├── db/                      # Models SQLAlchemy e sessão do banco
├── schemas/                 # Schemas Pydantic (validação)
├── services/                # Lógica de negócio + integrações Google
├── tests/                   # Testes automatizados (pytest)
└── frontend/                # App Vue 3 (SPA)
    └── src/
        ├── views/           # Páginas da aplicação
        ├── stores/          # Estado global (Pinia)
        ├── router/          # Rotas com guarda de autenticação
        └── api/client.js    # Cliente Axios centralizado
```

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- MySQL rodando localmente (ou via Docker)

---

### Backend

**1. Clone o repositório e crie o ambiente virtual**

```bash
git clone https://github.com/seu-usuario/ekaneshiro.git
cd ekaneshiro
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**2. Instale as dependências**

```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```env
DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/sgk
SECRET_KEY=uma-chave-secreta-longa-e-aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Calendar (opcional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Google Sheets (opcional — necessita service_account.json)
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_SPREADSHEET_ID=
```

**4. Crie o banco e rode as migrations**

```bash
# Crie o banco no MySQL antes:
# CREATE DATABASE sgk CHARACTER SET utf8mb4;

alembic upgrade head
```

**5. (Opcional) Popule dados iniciais**

```bash
python seed.py
```

**6. Suba o servidor**

```bash
uvicorn main:app --reload
```

API disponível em `http://localhost:8000`
Documentação interativa em `http://localhost:8000/docs`

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponível em `http://localhost:5173`

---

## Testes

```bash
# Na raiz do projeto, com o venv ativo:
pytest
```

---

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `DATABASE_URL` | ✅ | String de conexão MySQL no formato `mysql+pymysql://...` |
| `SECRET_KEY` | ✅ | Chave para assinatura dos tokens JWT |
| `ALGORITHM` | ✅ | Algoritmo JWT (padrão: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Tempo de expiração do token (padrão: `30`) |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | ⚠️ | Caminho para o JSON da service account Google |
| `GOOGLE_SPREADSHEET_ID` | ⚠️ | ID da planilha Google Sheets para exportação |
| `GOOGLE_CLIENT_ID` | ⚠️ | Client ID OAuth para Google Calendar |
| `GOOGLE_CLIENT_SECRET` | ⚠️ | Client Secret OAuth para Google Calendar |

> ⚠️ Variáveis marcadas são necessárias apenas se as integrações com Google forem utilizadas.

---

## Perfis de acesso

| Perfil | Permissões |
|---|---|
| `admin` | Acesso total — inclui relatórios e gerenciamento de usuários |
| `recepcionista` | Agendamentos, clientes, profissionais, serviços e produtos |
| `profissional` | Visualização dos próprios agendamentos |

---

## Deploy

Veja o arquivo [DEPLOY.md](DEPLOY.md) para o passo a passo completo de como colocar o projeto online usando Railway (backend + MySQL) e Vercel (frontend).

---

## Segurança

- Senhas armazenadas com hash bcrypt via `passlib`
- Autenticação stateless com JWT
- CORS configurável por ambiente
- `service_account.json` e `.env` **nunca devem ser versionados**
