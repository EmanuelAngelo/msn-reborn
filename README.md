# MSN Reborn

Messenger inspirado no **Windows Live Messenger (MSN)**, com backend em **Django REST Framework + Channels** e frontend em **Vue 3 + TailwindCSS**.

Experiência nostálgica com chat em tempo real, status de presença, nudge, música no perfil (Spotify) e interface responsiva para web e mobile.

## Funcionalidades

### Autenticação e perfil
- Registro e login com **Token Authentication**
- Perfil com nome, mensagem pessoal, foto e status (online, ausente, ocupado, invisível, offline)
- Modo **invisível** — aparece como offline para os contatos
- Upload de avatar com URLs de mídia compatíveis com Docker e proxy Nginx

### Contatos e presença
- Busca e adição de contatos com solicitações (aceitar/recusar)
- **Favoritos** e **bloqueio** de contatos
- Atualização em tempo real de status, nome, foto e música via WebSocket
- **Notificação estilo MSN** quando um contato fica online (popup no canto inferior direito, some em 3s)

### Chat
- Conversas diretas 1:1
- Mensagens em tempo real (WebSocket) com fallback por polling REST
- Indicador **"está digitando..."** com animação
- **Nudge** — chamar atenção com animação de tremor na tela
- Marcação automática de mensagens como lidas
- **Minimizar conversas** — barra inferior estilo MSN com várias conversas abertas
- Histórico de até 100 mensagens por conversa

### Música (Spotify)
- OAuth com Spotify
- Exibir faixa atual no perfil e na lista de contatos
- Preferências de privacidade (visibilidade, capa, pausado)

## Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | Django 5, DRF, Channels, Daphne |
| Frontend | Vue 3, Vite, TailwindCSS 4 |
| Tempo real | WebSockets + Redis (Docker) |
| Banco | SQLite (padrão) / PostgreSQL (opcional) |
| Docs API | drf-spectacular (Swagger/ReDoc) |

## Estrutura do projeto

```text
msn-reborn/
├── core/                  # Settings, URLs, ASGI/WSGI
├── msn/                   # Models, API, WebSockets, Spotify
├── frontend/              # SPA Vue 3
├── docker/                # Entrypoint e config Nginx
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
├── .env.example
├── API_GUIDE.md
├── SECURITY.md
└── LICENSE                # MIT
```

## Rodar com Docker (recomendado)

Pré-requisitos: Docker e Docker Compose.

```bash
cp .env.example .env
# Edite .env (Spotify, SECRET_KEY, etc.)

docker compose up -d --build
```

| Serviço | URL |
|---------|-----|
| Frontend | http://127.0.0.1:8080 |
| Backend / Swagger | http://127.0.0.1:8000/api/docs/ |
| WebSocket | ws://127.0.0.1:8080/ws/ (via Nginx) |

Serviços: **backend** (Django + Daphne), **frontend** (Nginx + Vue), **redis** (channel layer).

```bash
docker compose down          # parar
docker compose logs -f       # logs
docker compose up -d --build # rebuild após mudanças
```

## Rodar localmente (sem Docker)

Use **127.0.0.1** de forma consistente (evita problemas de CORS/origem).

### Backend

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Acesse: http://127.0.0.1:5173

O Vite já faz proxy de `/api`, `/media` e `/ws` para o backend local.

### Variáveis de ambiente (`.env`)

```env
APP_ENV=local
DEBUG=True
SECRET_KEY=sua-chave-secreta

# Spotify (opcional)
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=

# Redis (opcional — Docker usa redis://redis:6379/0)
REDIS_URL=

# PostgreSQL (opcional)
# DATABASE_URL=postgres://user:pass@host:5432/msn
```

### Frontend ( `frontend/.env` )

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_WS_BASE_URL=ws://127.0.0.1:8000
VITE_ENABLE_WEBSOCKETS=true
```

## Produção (PythonAnywhere + Vercel)

### Backend (PythonAnywhere)

No `.env` do servidor:

```env
APP_ENV=production
DEBUG=False
SECRET_KEY=chave-forte
ALLOWED_HOSTS=127.0.0.1,localhost,emanuelangelo1992.pythonanywhere.com,.pythonanywhere.com
CORS_ALLOWED_ORIGINS=https://msn-reborn-ochre.vercel.app
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

WebSocket no PythonAnywhere (plano padrão) **não está disponível** — o frontend usa polling REST automaticamente quando `VITE_ENABLE_WEBSOCKETS=false`.

**Avatares e mídia (`/media/`):**

1. Faça deploy do código atualizado e **Reload** no painel Web do PythonAnywhere.
2. A pasta `media/` **não vai para o Git** — fotos enviadas no ambiente local **não existem** no servidor de produção. É preciso **enviar a foto de perfil de novo** logado em produção (Vercel + PA).
3. Garanta que o diretório `media/` exista e seja gravável no servidor:

```bash
mkdir -p ~/msn-reborn/media/avatars
chmod 755 ~/msn-reborn/media
```

4. *(Opcional, mais rápido)* No painel **Web → Static files**, mapeie:

| URL            | Directory                          |
|----------------|------------------------------------|
| `/media/`      | `/home/SEU_USUARIO/msn-reborn/media/` |

Substitua `SEU_USUARIO` pelo seu usuário do PythonAnywhere.

### Frontend (Vercel)

```env
VITE_API_BASE_URL=https://emanuelangelo1992.pythonanywhere.com/api
VITE_ENABLE_WEBSOCKETS=false
```

## Spotify

1. Crie um app em [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Cadastre a Redirect URI (local ou produção):

```text
http://127.0.0.1:8000/api/spotify/callback/
https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/
```

3. Preencha `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` no `.env`
4. No app: **Conectar/Sync Spotify**

Scopes: `user-read-currently-playing`, `user-read-playback-state`, `user-read-private`

## Documentação da API

- Swagger: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Guia detalhado: [API_GUIDE.md](API_GUIDE.md)

### Endpoints principais

```text
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/me/
PATCH  /api/me/
PATCH  /api/me/status/

GET    /api/users/search/?q=nome
GET    /api/contacts/
POST   /api/contacts/{id}/block/
POST   /api/contacts/{id}/favorite/

GET    /api/contact-requests/
POST   /api/contact-requests/
POST   /api/contact-requests/{id}/accept/
POST   /api/contact-requests/{id}/reject/

GET    /api/conversations/
POST   /api/conversations/direct/
GET    /api/conversations/{id}/messages/
POST   /api/conversations/{id}/messages/
POST   /api/conversations/{id}/nudge/

GET    /api/music/status/
PATCH  /api/music/preferences/
GET    /api/spotify/connect/
POST   /api/spotify/sync/
```

### WebSockets

```text
ws://host/ws/presence/?token=SEU_TOKEN
ws://host/ws/conversations/{id}/?token=SEU_TOKEN
```

## Como testar

### Contatos e chat
1. Crie dois usuários em abas ou navegadores diferentes
2. Envie e aceite solicitação de contato
3. Abra a conversa, envie mensagens e teste o nudge
4. Minimize com **`_`** na barra do chat — restaure pela barra inferior

### Presença e notificações
1. Usuário A: status **offline** → salvar → **online**
2. Usuário B: deve ver popup *"acabou de ficar online"*

### Digitação
1. Com WebSocket ativo, digite em uma aba
2. A outra exibe *"está digitando..."* com animação

## Segurança

- Nunca commite `.env`, tokens ou `SPOTIFY_CLIENT_SECRET`
- Use variáveis de ambiente em produção
- Consulte [SECURITY.md](SECURITY.md)

## Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE).

## Autor

**Emanuel Coutinho** — projeto de estudo e homenagem ao MSN Messenger clássico.
