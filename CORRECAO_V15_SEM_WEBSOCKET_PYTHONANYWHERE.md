# Correção v15 — Produção no PythonAnywhere sem WebSocket

Esta atualização não remove funcionalidades existentes.

Ajustes feitos:

- Desativada a tentativa de WebSocket por padrão em produção.
- Adicionada variável `VITE_ENABLE_WEBSOCKETS=false`.
- Removida a mensagem visual: `Erro no chat em tempo real. Usando atualização automática.` quando o WebSocket estiver desativado.
- Mantido fallback por REST/polling para chat, convites, aceite de convite, contatos e presença.
- O chat continua funcionando enviando por REST e buscando mensagens automaticamente.

## Vercel

Configure:

```env
VITE_API_BASE_URL=https://emanuelangelo1992.pythonanywhere.com/api
VITE_WS_BASE_URL=wss://emanuelangelo1992.pythonanywhere.com
VITE_ENABLE_WEBSOCKETS=false
```

Depois faça novo deploy.

## Quando usar WebSocket real

Se migrar o backend para um provedor com ASGI/WebSocket, como Render, Railway, Fly.io ou VPS, altere:

```env
VITE_ENABLE_WEBSOCKETS=true
```
