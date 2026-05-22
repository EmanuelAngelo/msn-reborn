# MSN Reborn - MVP Django REST + Vue

Projeto inspirado no antigo MSN Messenger, com backend em Django REST Framework e frontend em Vue 3 + TailwindCSS.

Esta versão foi ajustada para desenvolvimento local usando **127.0.0.1 em tudo**. Isso evita o erro comum de sessão/CSRF em que o login funciona, mas o endpoint `/api/me/` retorna `403 Forbidden` porque o navegador trata `localhost` e `127.0.0.1` como origens diferentes para cookie de sessão.

## Estrutura

```text
msn_reborn_project/
├── core/
├── msn/
├── frontend/
├── manage.py
├── requirements.txt
├── .env.example
├── API_GUIDE.md
└── README.md
```

## 1. Configurar Spotify

No Spotify Developer Dashboard, cadastre exatamente esta Redirect URI:

```text
http://127.0.0.1:8000/api/spotify/callback/
```

A URI precisa ser idêntica à do `.env`, incluindo a barra final `/`.

> Importante: se você já compartilhou um Client Secret ou token em algum lugar, gere um novo Client Secret no painel do Spotify.

## 2. Rodar backend

No Windows PowerShell, dentro da pasta do projeto:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Abra o arquivo `.env` e preencha:

```env
SPOTIFY_CLIENT_ID=seu_client_id_novo
SPOTIFY_CLIENT_SECRET=seu_client_secret_novo
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/spotify/callback/
FRONTEND_URL=http://127.0.0.1:5173
```

Depois rode:

```powershell
python manage.py makemigrations
python manage.py makemigrations msn
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

## 3. Rodar frontend

Em outro terminal:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Acesse:

```text
http://127.0.0.1:5173
```

## 4. Documentação da API

Com o backend ligado:

```text
http://127.0.0.1:8000/api/docs/
http://127.0.0.1:8000/api/redoc/
http://127.0.0.1:8000/api/schema/
```

## 5. Endpoints principais

```text
GET    /api/auth/csrf/
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/me/
PATCH  /api/me/
PATCH  /api/me/status/

GET    /api/users/search/?q=emanuel
GET    /api/contacts/
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
GET    /api/music/preferences/
PATCH  /api/music/preferences/
GET    /api/spotify/connect/
GET    /api/spotify/callback/
POST   /api/spotify/sync/
```

## 6. Como testar o fluxo de contatos

1. Crie dois usuários diferentes.
2. Entre com o usuário A.
3. Pesquise o e-mail ou nome do usuário B na área **Adicionar contatos**.
4. Envie solicitação.
5. Saia e entre com o usuário B.
6. Aceite a solicitação.
7. Os dois usuários passam a aparecer na lista de contatos.

## 7. Como testar o Spotify

1. Entre no sistema.
2. Clique em **Conectar/Sync Spotify**.
3. Autorize no Spotify.
4. O backend volta para o frontend com `?spotify=connected`.
5. Deixe alguma música tocando no Spotify.
6. Clique novamente em **Conectar/Sync Spotify** para sincronizar.

Para o status estilo MSN, o endpoint usado é:

```text
https://api.spotify.com/v1/me/player/currently-playing
```

Scopes usados:

```text
user-read-currently-playing user-read-playback-state user-read-private
```

## 8. SQLite agora, PostgreSQL depois

O projeto continua usando SQLite no início, mas os models já foram feitos pensando em migração futura para PostgreSQL:

- UUIDField nas entidades principais.
- ForeignKey e OneToOne bem definidos.
- Constraints por migrations do Django.
- Sem ArrayField, JSONField específico ou recursos exclusivos de PostgreSQL no MVP.

Quando for migrar, ajuste `DATABASES` no `core/settings.py` e rode as migrations no novo banco.
