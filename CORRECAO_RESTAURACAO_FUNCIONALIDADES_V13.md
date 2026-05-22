# Correção v13 — restauração das funcionalidades e ajuste de deploy

Esta versão mantém e restaura as funcionalidades que já tinham sido construídas:

- alteração de status manual: online, ausente, ocupado, invisível e offline;
- edição da mensagem pessoal/subnick;
- alteração do nome de exibição;
- upload e exibição da foto de perfil;
- exibição da foto dos contatos;
- busca de usuários filtrando quem já recebeu convite, quem já enviou convite e quem já é contato;
- atualização de solicitações de contato em tempo real;
- atualização de contatos em tempo real após aceitar solicitação;
- atualização de status/perfil/música via WebSocket de presença;
- scroll interno no chat;
- integração Spotify com auto-sync;
- configuração de CORS para o frontend hospedado na Vercel.

## Arquivos principais alterados

- `core/settings.py`
- `frontend/src/services/api.js`
- `frontend/src/services/auth.js`
- `frontend/.env.example`
- `frontend/.env`

## Configuração no Spotify

Cadastre as duas Redirect URIs no Spotify Developer Dashboard:

```text
http://127.0.0.1:8000/api/spotify/callback/
https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/
```

Depois cole seu Client ID e Client Secret em `core/settings.py`:

```python
SPOTIFY_CLIENT_ID = 'SEU_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'SEU_CLIENT_SECRET'
```

## Vercel

No projeto da Vercel, configure:

```env
VITE_API_BASE_URL=https://emanuelangelo1992.pythonanywhere.com/api
VITE_WS_BASE_URL=wss://emanuelangelo1992.pythonanywhere.com
```

## PythonAnywhere

Depois de subir os arquivos, clique em **Reload** na aba Web.

Observação: o PythonAnywhere tradicional pode ter limitações para WebSocket/ASGI. A API REST funciona, mas chat/presença em tempo real podem exigir plataforma com suporte ASGI/WebSocket.
