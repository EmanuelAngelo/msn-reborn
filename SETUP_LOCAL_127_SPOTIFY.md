# Ajuste local: 127.0.0.1 + Spotify

Use sempre este trio:

```text
Backend:  http://127.0.0.1:8000
Frontend: http://127.0.0.1:5173
Spotify Redirect URI: http://127.0.0.1:8000/api/spotify/callback/
```

Não misture `localhost` com `127.0.0.1`, porque isso pode causar perda do cookie de sessão e retornar `403 Forbidden` no `/api/me/` depois do login.

## Backend `.env`

```env
SECRET_KEY=troque-essa-chave-em-desenvolvimento
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5173
FRONTEND_URL=http://127.0.0.1:5173
SPOTIFY_CLIENT_ID=seu_client_id_novo
SPOTIFY_CLIENT_SECRET=seu_client_secret_novo
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/spotify/callback/
```

## Frontend `.env`

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Comandos

Backend:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Frontend:

```powershell
cd frontend
npm run dev
```


## Correção aplicada na v4

Esta versão usa DRF TokenAuthentication no frontend para evitar 403 em `/api/me/`, `/api/contact-requests/` e `/api/spotify/sync/` quando o navegador não persiste o cookie de sessão entre `127.0.0.1:5173` e `127.0.0.1:8000`.

Depois do login, o backend retorna:

```json
{
  "token": "...",
  "profile": { }
}
```

O frontend salva esse token no `localStorage` e envia nas próximas requisições como:

```http
Authorization: Token seu_token
```

Para conectar o Spotify, o frontend envia o token na URL de início do OAuth apenas em ambiente local:

```text
/api/spotify/connect/?auth_token=...
```

O callback usa um `state` assinado pelo Django para identificar o usuário com segurança durante o fluxo OAuth.
