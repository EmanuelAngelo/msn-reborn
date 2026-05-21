# MSN Reborn

Aplicação web inspirada no antigo MSN Messenger, construída como MVP usando **Django REST Framework** no backend e **Vue.js + TailwindCSS** no frontend.

O objetivo do projeto é recriar a experiência clássica do MSN com tecnologias atuais: login, lista de contatos, solicitações de amizade, conversa em tempo real, presença online/offline, botão de chamar atenção e integração com Spotify para exibir no status a música que o usuário está ouvindo.

---

## Sumário

- [Visão geral](#visão-geral)
- [Stack utilizada](#stack-utilizada)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Funcionalidades atuais](#funcionalidades-atuais)
- [Backend Django](#backend-django)
- [Frontend Vue](#frontend-vue)
- [Configuração local](#configuração-local)
- [Configuração do Spotify](#configuração-do-spotify)
- [API REST](#api-rest)
- [WebSockets](#websockets)
- [Fluxos principais](#fluxos-principais)
- [Banco de dados](#banco-de-dados)
- [Autenticação](#autenticação)
- [Pontos de atenção](#pontos-de-atenção)
- [Próximas evoluções sugeridas](#próximas-evoluções-sugeridas)

---

## Visão geral

O **MSN Reborn** é um comunicador web com visual nostálgico inspirado no MSN Messenger.

A aplicação permite que usuários façam cadastro, login, adicionem contatos, aceitem solicitações de amizade, conversem em tempo real e exibam no perfil a música atualmente em reprodução no Spotify.

A base atual já conta com:

- autenticação via token;
- API REST documentada com Swagger e ReDoc;
- frontend em Vue consumindo a API;
- chat em tempo real via WebSocket;
- presença online/offline em tempo real;
- integração funcional com Spotify OAuth;
- estrutura preparada inicialmente para SQLite, mas pensada para migração futura para PostgreSQL.

---

## Stack utilizada

### Backend

- Python
- Django
- Django REST Framework
- Django Channels
- Daphne
- SQLite em desenvolvimento
- PostgreSQL preparado para uso futuro
- drf-spectacular para documentação Swagger/ReDoc
- django-cors-headers
- Token Authentication do DRF
- Requests para comunicação com API do Spotify

### Frontend

- Vue.js
- Vite
- TailwindCSS
- Axios
- WebSocket API nativa do navegador
- LocalStorage para armazenamento do token de autenticação

### Integração externa

- Spotify Web API
- Spotify OAuth Authorization Code Flow
- Endpoint principal utilizado: música em reprodução atual do usuário

---

## Estrutura do projeto

```text
msn_reborn_project/
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── msn/
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── style.css
│       └── services/
│           ├── api.js
│           ├── auth.js
│           ├── chatSocket.js
│           ├── msn.js
│           └── presenceSocket.js
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Funcionalidades atuais

### Usuário e autenticação

- Cadastro de usuário.
- Login por e-mail e senha.
- Retorno de token de autenticação.
- Logout com remoção do token.
- Endpoint `/api/me/` para consultar e atualizar perfil.
- Atualização de status do usuário.

### Perfil

Cada usuário possui um perfil com:

- nome de exibição;
- mensagem pessoal;
- avatar;
- status;
- último acesso;
- música atual do Spotify.

Status disponíveis:

```text
online
away
busy
invisible
offline
```

### Contatos

- Buscar usuários cadastrados.
- Enviar solicitação de amizade.
- Listar solicitações recebidas e enviadas.
- Aceitar solicitação.
- Recusar solicitação.
- Criar contato dos dois lados após aceite.
- Listar contatos com status e música atual.

### Chat

- Abrir conversa direta com um contato.
- Criar conversa caso ainda não exista.
- Recuperar histórico de mensagens.
- Enviar mensagem em tempo real via WebSocket.
- Receber mensagens sem atualizar a página.
- Indicador de “digitando”.
- Botão “chamar atenção”.
- Efeito visual de tremida no frontend.

### Presença em tempo real

- Usuário fica online ao conectar.
- Usuário fica offline ao desconectar/logout.
- Lista de contatos atualiza sem refresh.
- WebSocket dedicado para presença.

### Spotify

- Conectar conta Spotify.
- Callback OAuth funcional.
- Salvar `access_token`, `refresh_token` e expiração.
- Renovar token expirado.
- Sincronizar música atual.
- Exibir música atual no perfil e na lista de contatos.

---

## Backend Django

O backend usa um projeto Django chamado `core` e um app principal chamado `msn`.

A criação base segue o padrão:

```bash
django-admin startproject core .
django-admin startapp msn
```

### Apps principais instalados

No `core/settings.py`:

```python
INSTALLED_APPS = [
    'daphne',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_spectacular',
    'channels',

    'msn',
]
```

### Configuração REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

A autenticação principal usada pelo frontend atualmente é **Token Authentication**.

---

## Frontend Vue

O frontend fica na pasta `frontend/` e foi criado com Vite, Vue e TailwindCSS.

Scripts disponíveis:

```json
{
  "dev": "vite --host 127.0.0.1",
  "build": "vite build",
  "preview": "vite preview --host 127.0.0.1"
}
```

### Serviços principais do frontend

```text
frontend/src/services/api.js
```

Responsável por criar a instância do Axios, configurar a URL base da API, anexar token nas requisições e tratar CSRF quando necessário.

```text
frontend/src/services/auth.js
```

Responsável por login, cadastro, logout e consulta do perfil autenticado.

```text
frontend/src/services/msn.js
```

Responsável por contatos, solicitações, conversas, mensagens, Spotify e status musical.

```text
frontend/src/services/chatSocket.js
```

Responsável pela conexão WebSocket de conversa em tempo real.

```text
frontend/src/services/presenceSocket.js
```

Responsável pela conexão WebSocket de presença online/offline em tempo real.

### URL base do frontend

O frontend roda em:

```text
http://127.0.0.1:5173
```

### URL base da API

A API roda em:

```text
http://127.0.0.1:8000/api
```

### URL base do WebSocket

Os WebSockets usam:

```text
ws://127.0.0.1:8000
```

---

## Configuração local

### 1. Clonar/abrir o projeto

Entre na pasta raiz do projeto, onde existe o arquivo `manage.py`.

```bash
cd msn_reborn_project
```

### 2. Criar ambiente virtual

No Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
```

No Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências do backend

```bash
pip install -r requirements.txt
```

### 4. Rodar migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Criar superusuário

```bash
python manage.py createsuperuser
```

### 6. Rodar backend

```bash
python manage.py runserver 127.0.0.1:8000
```

O backend ficará disponível em:

```text
http://127.0.0.1:8000
```

### 7. Rodar frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

O frontend ficará disponível em:

```text
http://127.0.0.1:5173
```

---

## Configuração do Spotify

A integração com Spotify usa o fluxo OAuth do Spotify.

### 1. Criar app no Spotify Developer Dashboard

Acesse o painel de desenvolvedor do Spotify e crie um app.

Sugestão de configuração:

```text
App name: MSN Reborn
Description: Aplicação de mensagens inspirada no antigo MSN com status musical via Spotify.
Website: http://127.0.0.1:5173
API usada: Web API
```

### 2. Configurar Redirect URI

No campo **Redirect URIs**, cadastre exatamente:

```text
http://127.0.0.1:8000/api/spotify/callback/
```

A URL precisa ser exatamente igual à configuração no Django, incluindo:

- protocolo `http`;
- IP `127.0.0.1`;
- porta `8000`;
- caminho `/api/spotify/callback/`;
- barra final `/`.

### 3. Configurar credenciais no Django

No arquivo:

```text
core/settings.py
```

Configure:

```python
SPOTIFY_CLIENT_ID = 'SEU_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'SEU_CLIENT_SECRET'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8000/api/spotify/callback/'
```

> Atenção: em ambiente real, o `Client Secret` não deve ficar versionado no código. Para produção, o ideal é usar variável de ambiente. No MVP local, foi deixado no `settings.py` apenas para facilitar o teste.

### 4. Permissões usadas

Atualmente o fluxo solicita os seguintes scopes:

```text
user-read-currently-playing
user-read-playback-state
user-read-private
```

O mais importante para a experiência MSN é:

```text
user-read-currently-playing
```

Ele permite consultar a música atualmente em reprodução.

### 5. Fluxo Spotify na aplicação

```text
Usuário logado clica em conectar Spotify
        ↓
Frontend abre /api/spotify/connect/?auth_token=<token>
        ↓
Backend gera state assinado com o ID do usuário
        ↓
Backend redireciona para autorização do Spotify
        ↓
Usuário autoriza
        ↓
Spotify retorna para /api/spotify/callback/
        ↓
Backend troca o code por access_token e refresh_token
        ↓
Backend salva SpotifyIntegration
        ↓
Backend ativa UserMusicPreference
        ↓
Usuário volta para o frontend em /?spotify=connected
```

### 6. Sincronização da música

A sincronização é feita pelo endpoint:

```http
POST /api/spotify/sync/
```

Esse endpoint:

1. verifica se o usuário tem Spotify conectado;
2. renova o token se estiver expirado;
3. chama a API do Spotify;
4. consulta a música atual;
5. salva em `UserMusicStatus`;
6. retorna os dados para o frontend.

Endpoint usado no Spotify:

```text
https://api.spotify.com/v1/me/player/currently-playing
```

### 7. Comportamentos esperados

Quando houver música tocando:

```text
♫ Artista - Música
```

Quando não houver música em reprodução:

```json
{
  "detail": "Nenhuma música em reprodução."
}
```

Quando o Spotify não estiver conectado:

```json
{
  "detail": "Spotify não conectado."
}
```

---

## API REST

A API usa a base:

```text
http://127.0.0.1:8000/api
```

### Documentação automática

Swagger:

```text
http://127.0.0.1:8000/api/docs/
```

ReDoc:

```text
http://127.0.0.1:8000/api/redoc/
```

Schema OpenAPI:

```text
http://127.0.0.1:8000/api/schema/
```

---

## Endpoints de autenticação

### Obter CSRF

```http
GET /api/auth/csrf/
```

Usado como apoio para requisições que precisam de CSRF. A autenticação principal do frontend é via token.

### Registrar usuário

```http
POST /api/auth/register/
```

Payload:

```json
{
  "email": "usuario@email.com",
  "username": "usuario",
  "password": "senha12345",
  "display_name": "Nome de Exibição"
}
```

Resposta esperada:

```json
{
  "token": "token_do_usuario",
  "profile": {
    "id": "uuid",
    "user_id": "uuid",
    "email": "usuario@email.com",
    "username": "usuario",
    "display_name": "Nome de Exibição",
    "personal_message": "",
    "avatar": null,
    "status": "online",
    "last_seen_at": null
  }
}
```

### Login

```http
POST /api/auth/login/
```

Payload:

```json
{
  "email": "usuario@email.com",
  "password": "senha12345"
}
```

Resposta esperada:

```json
{
  "token": "token_do_usuario",
  "profile": {}
}
```

### Logout

```http
POST /api/auth/logout/
```

No logout, o backend coloca o usuário como `offline` e remove o token.

---

## Endpoints de perfil

### Consultar perfil autenticado

```http
GET /api/me/
```

Header obrigatório:

```http
Authorization: Token SEU_TOKEN
```

### Atualizar perfil

```http
PATCH /api/me/
```

Payload exemplo:

```json
{
  "display_name": "Emanuel",
  "personal_message": "Codando e ouvindo música"
}
```

### Atualizar status

```http
PATCH /api/me/status/
```

Payload:

```json
{
  "status": "away"
}
```

Status válidos:

```text
online
away
busy
invisible
offline
```

---

## Endpoints de usuários e contatos

### Buscar usuários

```http
GET /api/users/search/?q=emanuel
```

Busca por:

- e-mail;
- username;
- display name.

### Listar contatos

```http
GET /api/contacts/
```

Retorna contatos do usuário autenticado com:

- perfil do contato;
- status do contato;
- música atual do contato;
- favorito/bloqueado.

### Criar solicitação de contato

```http
POST /api/contact-requests/
```

Payload:

```json
{
  "receiver": "uuid_do_usuario_destino",
  "message": "Olá, me adiciona aí!"
}
```

### Listar solicitações

```http
GET /api/contact-requests/
```

Retorna solicitações enviadas e recebidas pelo usuário autenticado.

### Aceitar solicitação

```http
POST /api/contact-requests/{id}/accept/
```

Ao aceitar, o backend cria dois registros de contato:

```text
Usuário A -> Usuário B
Usuário B -> Usuário A
```

### Recusar solicitação

```http
POST /api/contact-requests/{id}/reject/
```

---

## Endpoints de conversas

### Listar conversas

```http
GET /api/conversations/
```

### Abrir/criar conversa direta

```http
POST /api/conversations/direct/
```

Payload:

```json
{
  "contact_id": "uuid_do_contato"
}
```

Regras:

- o usuário destino precisa estar na lista de contatos;
- se já existir uma conversa direta entre os dois, o backend retorna a conversa existente;
- se não existir, cria uma nova conversa.

### Listar mensagens de uma conversa

```http
GET /api/conversations/{conversation_id}/messages/
```

### Enviar mensagem via REST

```http
POST /api/conversations/{conversation_id}/messages/
```

Payload:

```json
{
  "type": "text",
  "content": "Oi, tudo bem?"
}
```

Observação: o envio principal no frontend atual é feito via WebSocket. Esse endpoint REST permanece útil como fallback, teste e documentação.

### Chamar atenção via REST

```http
POST /api/conversations/{conversation_id}/nudge/
```

Observação: no frontend atual, o “chamar atenção” também pode ser disparado via WebSocket.

---

## Endpoints de música

### Preferências de música

```http
GET /api/music/preferences/
PATCH /api/music/preferences/
```

Payload exemplo:

```json
{
  "enabled": true,
  "visibility": "contacts",
  "show_album_cover": false,
  "show_when_paused": false,
  "show_spotify_link": true
}
```

### Status musical atual

```http
GET /api/music/status/
```

Retorna a música atual salva no backend para o usuário autenticado.

### Conectar Spotify

```http
GET /api/spotify/connect/?auth_token=SEU_TOKEN
```

Esse endpoint redireciona para o Spotify.

### Callback Spotify

```http
GET /api/spotify/callback/
```

Esse endpoint é chamado pelo Spotify após a autorização.

### Sincronizar Spotify

```http
POST /api/spotify/sync/
```

Atualiza a música atual consultando a API do Spotify.

---

## WebSockets

O projeto usa Django Channels com `InMemoryChannelLayer` em desenvolvimento.

No `core/settings.py`:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}
```

Para produção, o ideal é trocar para Redis.

---

## WebSocket de conversa

URL:

```text
ws://127.0.0.1:8000/ws/conversations/{conversation_id}/?token=SEU_TOKEN
```

Arquivo frontend:

```text
frontend/src/services/chatSocket.js
```

Arquivo backend:

```text
msn/consumers.py
```

Consumer:

```text
ChatConsumer
```

### Eventos enviados pelo frontend

Enviar mensagem:

```json
{
  "type": "message.send",
  "content": "Olá!"
}
```

Começou a digitar:

```json
{
  "type": "typing.start"
}
```

Parou de digitar:

```json
{
  "type": "typing.stop"
}
```

Chamar atenção:

```json
{
  "type": "nudge.send"
}
```

### Eventos recebidos pelo frontend

Conexão aceita:

```json
{
  "type": "connection.accepted",
  "conversation_id": "uuid",
  "message": "Conectado ao chat em tempo real."
}
```

Mensagem criada:

```json
{
  "type": "message.created",
  "message": {
    "id": "uuid",
    "conversation": "uuid",
    "sender": {
      "id": "uuid",
      "username": "usuario",
      "email": "usuario@email.com"
    },
    "sender_name": "Nome",
    "type": "text",
    "content": "Olá!",
    "sent_at": "2026-05-21T12:00:00-03:00"
  }
}
```

Chamar atenção recebido:

```json
{
  "type": "nudge.received",
  "message": {}
}
```

Digitando:

```json
{
  "type": "typing.updated",
  "user": {
    "id": "uuid",
    "username": "usuario",
    "email": "usuario@email.com"
  },
  "is_typing": true
}
```

---

## WebSocket de presença

URL:

```text
ws://127.0.0.1:8000/ws/presence/?token=SEU_TOKEN
```

Arquivo frontend:

```text
frontend/src/services/presenceSocket.js
```

Consumer:

```text
PresenceConsumer
```

### Eventos enviados pelo frontend

Ping periódico:

```json
{
  "type": "presence.ping"
}
```

Alterar status:

```json
{
  "type": "presence.set_status",
  "status": "online"
}
```

### Eventos recebidos pelo frontend

Conexão pronta:

```json
{
  "type": "presence.ready",
  "profile": {}
}
```

Presença atualizada:

```json
{
  "type": "presence.updated",
  "profile": {
    "user_id": "uuid",
    "display_name": "Emanuel",
    "status": "online"
  }
}
```

Esse evento é usado para atualizar a lista de contatos sem refresh.

---

## Fluxos principais

### Cadastro e login

```text
Usuário cadastra conta
        ↓
Backend cria User
        ↓
Signals criam UserProfile, UserMusicPreference e UserMusicStatus
        ↓
Backend gera token
        ↓
Frontend salva token no localStorage
        ↓
Frontend carrega dashboard
```

### Adicionar contato

```text
Usuário busca outro usuário
        ↓
Envia solicitação
        ↓
Outro usuário aceita
        ↓
Backend cria Contact dos dois lados
        ↓
Ambos aparecem na lista de contatos
```

### Conversa em tempo real

```text
Usuário clica em contato
        ↓
Frontend chama /api/conversations/direct/
        ↓
Backend retorna conversa existente ou cria nova
        ↓
Frontend abre WebSocket da conversa
        ↓
Usuário envia mensagem
        ↓
Backend salva Message
        ↓
Backend dispara evento para grupo da conversa
        ↓
Participantes recebem mensagem sem atualizar a página
```

### Presença online/offline

```text
Usuário faz login
        ↓
Frontend abre WebSocket de presença
        ↓
Backend marca usuário como online
        ↓
Backend envia evento para grupo de presença
        ↓
Contatos atualizam status em tempo real
```

### Música no status

```text
Usuário conecta Spotify
        ↓
Backend salva tokens
        ↓
Usuário sincroniza Spotify
        ↓
Backend consulta música atual
        ↓
Backend salva UserMusicStatus
        ↓
Frontend mostra música abaixo do perfil
```

---

## Banco de dados

O projeto usa SQLite em desenvolvimento:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

A estrutura foi pensada para futura migração para PostgreSQL:

- IDs principais com UUID;
- relacionamentos por ForeignKey/OneToOne;
- uso de `TextChoices` para status e tipos;
- sem uso de campos exclusivos do PostgreSQL no MVP;
- constraints de unicidade para contatos e participantes.

### Modelos principais

```text
User
UserProfile
ContactRequest
Contact
Conversation
ConversationParticipant
Message
PresenceSession
SpotifyIntegration
UserMusicPreference
UserMusicStatus
```

### Migração futura para PostgreSQL

Exemplo de configuração futura:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'msn_reborn_db',
        'USER': 'postgres',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Autenticação

A autenticação principal é feita com token do DRF.

Após login ou cadastro, o backend retorna:

```json
{
  "token": "...",
  "profile": {}
}
```

O frontend salva o token em:

```text
localStorage['msn_auth_token']
```

Todas as chamadas protegidas enviam:

```http
Authorization: Token SEU_TOKEN
```

O WebSocket também recebe o token via query string:

```text
?token=SEU_TOKEN
```

---

## Documentação da API

Com o backend rodando, acesse:

```text
http://127.0.0.1:8000/api/docs/
```

ou:

```text
http://127.0.0.1:8000/api/redoc/
```

Essas páginas são geradas pelo `drf-spectacular`.

---

## Pontos de atenção

### Não misturar localhost com 127.0.0.1

Use sempre:

```text
Frontend: http://127.0.0.1:5173
Backend:  http://127.0.0.1:8000
Spotify Redirect URI: http://127.0.0.1:8000/api/spotify/callback/
```

Evite misturar `localhost` com `127.0.0.1`, porque isso pode gerar problema de cookie, CORS, sessão e callback.

### Client Secret do Spotify

No MVP local, o secret pode ser colocado diretamente no `settings.py` para facilitar o teste.

Em produção, nunca versionar o `Client Secret` no Git.

### Channel Layer

O projeto usa `InMemoryChannelLayer`, que é adequado para desenvolvimento local.

Em produção, usar Redis:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### Spotify pausado ou fechado

Quando não existe música tocando, o endpoint do Spotify pode retornar `204 No Content`. O backend trata esse cenário marcando `is_playing=False` e limpando os campos principais.

---

## Comandos úteis

### Backend

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Testar configuração Spotify no Django

```bash
python manage.py shell -c "from django.conf import settings; print(settings.SPOTIFY_CLIENT_ID); print(len(settings.SPOTIFY_CLIENT_SECRET)); print(settings.SPOTIFY_REDIRECT_URI)"
```

O tamanho do secret não deve ser `0`.

---

## Próximas evoluções sugeridas

### Produto

- Notificações sonoras ao receber mensagem.
- Sons nostálgicos estilo MSN.
- Emoticons clássicos.
- Winks/animações.
- Envio de arquivos.
- Foto de perfil com upload real.
- Conversas em grupo.
- Busca no histórico de mensagens.
- Tema Windows XP/MSN 7.5.

### Técnico

- Migrar banco para PostgreSQL.
- Trocar `InMemoryChannelLayer` por Redis.
- Melhorar persistência de presença com múltiplas abas/dispositivos.
- Criar testes automatizados.
- Separar configurações por ambiente.
- Proteger secrets com variáveis de ambiente.
- Adicionar paginação real nas mensagens.
- Criar serviço assíncrono para sincronizar Spotify periodicamente.

### Spotify

- Atualização automática da música em intervalo controlado.
- Mostrar capa do álbum.
- Link “Abrir no Spotify”.
- Configuração para ocultar música pausada.
- Exibir música dos contatos em tempo real via WebSocket.

---

## Resumo final

O **MSN Reborn** é um MVP funcional de mensageria nostálgica com API Django REST, frontend Vue, chat em tempo real, presença online/offline e integração com Spotify.

A aplicação já possui base suficiente para evoluir de protótipo para produto mais completo, mantendo a proposta principal: recriar a experiência do antigo MSN usando uma stack moderna.
