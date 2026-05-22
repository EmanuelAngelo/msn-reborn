# Ajustes para PythonAnywhere + Frontend + Spotify

Esta versão foi ajustada para o domínio:

```text
https://emanuelangelo1992.pythonanywhere.com
```

## 1. Correção do erro Invalid HTTP_HOST

O erro:

```text
Invalid HTTP_HOST header: 'emanuelangelo1992.pythonanywhere.com'
```

foi corrigido em `core/settings.py`:

```python
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "emanuelangelo1992.pythonanywhere.com",
    ".pythonanywhere.com",
]
```

## 2. API usada pelo frontend

O frontend agora aponta por padrão para:

```text
https://emanuelangelo1992.pythonanywhere.com/api
```

Arquivo alterado:

```text
frontend/src/services/api.js
```

Também foram ajustados:

```text
frontend/.env
frontend/.env.example
```

com:

```env
VITE_API_BASE_URL=https://emanuelangelo1992.pythonanywhere.com/api
VITE_WS_BASE_URL=wss://emanuelangelo1992.pythonanywhere.com
```

## 3. Spotify Developer Dashboard

No painel do Spotify, em **Redirect URIs**, adicione:

```text
https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/
```

Se você também continuar testando localmente, mantenha também:

```text
http://127.0.0.1:8000/api/spotify/callback/
```

O `core/settings.py` agora usa por padrão:

```python
SPOTIFY_REDIRECT_URI = "https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/"
```

## 4. Client Secret do Spotify

Por segurança, o `SPOTIFY_CLIENT_SECRET` real foi removido.

No `core/settings.py`, coloque seu secret nesta linha:

```python
SPOTIFY_CLIENT_SECRET = os.environ.get(
    "SPOTIFY_CLIENT_SECRET",
    "COLE_AQUI_SEU_CLIENT_SECRET_DO_SPOTIFY",
)
```

Você pode trocar o texto `COLE_AQUI...` pelo seu secret localmente, ou configurar como variável de ambiente no PythonAnywhere.

## 5. Atenção sobre WebSocket no PythonAnywhere

O projeto usa Django Channels/WebSocket para chat, presença online e atualizações em tempo real.

Historicamente, aplicações WebSocket/ASGI não funcionam no PythonAnywhere padrão, e a própria equipe do PythonAnywhere já informou no fórum que Django Channels/WebSocket não funcionava no ambiente padrão. Consulte o suporte/painel do PythonAnywhere para verificar se sua conta tem ASGI/WebSocket habilitado.

Se WebSocket não funcionar no PythonAnywhere, a API REST funcionará normalmente, mas recursos em tempo real podem precisar de:

1. deploy em serviço com ASGI/WebSocket, como Render, Railway, Fly.io, VPS, DigitalOcean etc.; ou
2. fallback por polling no frontend.

## 6. Comandos básicos no PythonAnywhere

No console Bash do PythonAnywhere:

```bash
cd ~/msn_reborn_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

Depois configure a aba **Web** do PythonAnywhere apontando para o projeto Django.

## 7. URLs principais

API:

```text
https://emanuelangelo1992.pythonanywhere.com/api/
```

Swagger:

```text
https://emanuelangelo1992.pythonanywhere.com/api/docs/
```

Callback Spotify:

```text
https://emanuelangelo1992.pythonanywhere.com/api/spotify/callback/
```
