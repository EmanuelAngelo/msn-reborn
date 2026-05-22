# MSN Reborn API Guide

## Pontos corrigidos nesta versão

- Frontend usando `http://localhost:8000/api` por padrão para evitar perda de cookie de sessão entre `localhost` e `127.0.0.1`.
- `CSRF_TRUSTED_ORIGINS` adicionado no Django.
- Login e cadastro agora deixam o usuário com status `online`.
- Logout muda o usuário para `offline`.
- Nova rota para alterar status manualmente: `PATCH /api/me/status/`.
- Tela para buscar usuários e enviar solicitação de contato.
- Tela para aceitar ou recusar solicitações recebidas.
- Fluxo real de OAuth do Spotify implementado com `state` salvo na sessão.

## Rotas principais

### Autenticação

```txt
GET    /api/auth/csrf/
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/me/
PATCH  /api/me/
PATCH  /api/me/status/
```

### Contatos

```txt
GET    /api/users/search/?q=emanuel
GET    /api/contacts/
GET    /api/contact-requests/
POST   /api/contact-requests/
POST   /api/contact-requests/{id}/accept/
POST   /api/contact-requests/{id}/reject/
```

Payload para enviar solicitação:

```json
{
  "receiver": "uuid-do-usuario",
  "message": "Me adiciona no MSN Reborn?"
}
```

### Conversas

```txt
GET    /api/conversations/
POST   /api/conversations/direct/
GET    /api/conversations/{id}/messages/
POST   /api/conversations/{id}/messages/
POST   /api/conversations/{id}/nudge/
```

### Spotify

```txt
GET    /api/spotify/connect/
GET    /api/spotify/callback/
POST   /api/spotify/sync/
GET    /api/music/status/
GET    /api/music/preferences/
PATCH  /api/music/preferences/
```

## Configuração Spotify

No arquivo `.env` do backend:

```env
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/api/spotify/callback/
```

No painel do Spotify Developer, cadastre exatamente esta Redirect URI:

```txt
http://localhost:8000/api/spotify/callback/
```

## Documentação Swagger

Com o backend rodando:

```txt
http://localhost:8000/api/docs/
http://localhost:8000/api/redoc/
```
