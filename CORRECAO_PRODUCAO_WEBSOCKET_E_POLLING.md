# Correção produção — WebSocket, chat e convites

Alterações feitas sem remover funcionalidades existentes:

1. `frontend/src/services/api.js`
   - Adicionado `getWebSocketBaseUrl()`.
   - Se `VITE_WS_BASE_URL` não existir, o WebSocket passa a ser calculado a partir da URL da API.
   - Isso evita fallback para `ws://127.0.0.1:8000` em produção.

2. `frontend/src/services/presenceSocket.js`
   - Agora usa `getWebSocketBaseUrl()`.

3. `frontend/src/services/chatSocket.js`
   - Agora usa `getWebSocketBaseUrl()`.

4. `frontend/src/App.vue`
   - Adicionado polling de contatos/solicitações como fallback quando WebSocket de presença não estiver disponível.
   - Convites e aceite passam a aparecer sem precisar atualizar a página, mesmo em servidor sem WebSocket.

5. `frontend/src/components/ChatWindow.vue`
   - Adicionado fallback REST para envio de mensagem quando WebSocket não estiver aberto.
   - Adicionado polling de mensagens como fallback quando WebSocket do chat não estiver disponível.
   - O chat continua usando WebSocket quando disponível.

6. `frontend/.env`
   - Ajustado para produção:
     - `VITE_API_BASE_URL=https://emanuelangelo1992.pythonanywhere.com/api`
     - `VITE_WS_BASE_URL=wss://emanuelangelo1992.pythonanywhere.com`

Observação: se o PythonAnywhere não suportar WebSocket/ASGI no seu plano, o sistema usará polling para manter chat, convites e contatos atualizados sem refresh manual.
