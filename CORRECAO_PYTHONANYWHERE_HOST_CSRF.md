# Correção PythonAnywhere — ALLOWED_HOSTS, API do frontend e Spotify

Esta versão corrige o erro:

```text
Invalid HTTP_HOST header: 'emanuelangelo1992.pythonanywhere.com'
```

## 1. Backend Django

No `core/settings.py`, o domínio foi incluído em `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'emanuelangelo1992.pythonanywhere.com',
    '.pythonanywhere.com',
]
```

A API também foi configurada para usar `TokenAuthentication`, evitando depender do cookie de sessão do Django Admin no frontend.

## 2. Frontend

O frontend agora aponta para:

```text
https://emanuelangelo1992.pythonanywhere.com/api
```

Arquivo alterado:

```text
frontend/src/services/api.js
```

Também removemos a chamada obrigatória para `/api/auth/csrf/` no login/cadastro, porque a aplicação usa Token Authentication.

## 3. Spotify

No Spotify Developer Dashboard, adicione esta Redirect URI:

```text
https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/
```

Se ainda for testar localmente, mantenha também:

```text
http://127.0.0.1:8000/api/spotify/callback/
```

No `core/settings.py`, configure seu Client ID e Client Secret. O Secret real não foi enviado no zip por segurança.

## 4. Depois de subir no PythonAnywhere

No painel Web do PythonAnywhere:

1. recarregue a aplicação usando o botão **Reload**;
2. limpe cache do navegador;
3. teste `https://emanuelangelo1992.pythonanywhere.com/api/auth/csrf/`;
4. teste login pelo frontend.

## 5. Observação sobre WebSocket

O projeto usa WebSocket para chat em tempo real. Dependendo do plano/configuração do PythonAnywhere, WebSocket/ASGI pode não funcionar como em Render/Railway/VPS. A API REST e login funcionam normalmente com WSGI.
