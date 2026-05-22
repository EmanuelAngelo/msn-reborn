# Correção — Contatos, Solicitações e Presença em tempo real

Esta versão corrige o fluxo de adicionar contatos e atualização de presença sem precisar atualizar a página.

## O que foi ajustado

### 1. Busca de usuários

Ao pesquisar um usuário e enviar solicitação:

- o usuário sai imediatamente da lista de resultados;
- se pesquisar novamente sem limpar o campo, ele não aparece mais;
- o backend também passou a filtrar usuários que já são contatos ou que possuem solicitação pendente/aceita com o usuário logado.

Arquivo principal:

```txt
msn/views.py
```

Função ajustada:

```txt
search_users
```

---

### 2. Solicitação aparece para o outro usuário sem refresh

Foi criado um WebSocket geral de presença/notificações:

```txt
ws://127.0.0.1:8000/ws/presence/?token=TOKEN
```

Quando uma solicitação é enviada, o backend dispara evento para o usuário que recebeu:

```json
{
  "type": "contact_request_created"
}
```

O frontend recebe esse evento e recarrega automaticamente a lista de solicitações.

Arquivos principais:

```txt
msn/consumers.py
msn/routing.py
frontend/src/services/presenceSocket.js
frontend/src/App.vue
frontend/src/components/ContactManager.vue
```

---

### 3. Aceite de contato atualiza os dois lados

Quando o usuário aceita a solicitação:

- o backend cria os contatos dos dois lados;
- envia evento para quem aceitou;
- envia evento para quem enviou;
- os dois frontends atualizam a lista de contatos sem refresh.

Evento usado:

```json
{
  "type": "contacts_changed"
}
```

---

### 4. Status online/offline atualiza em tempo real

Quando o usuário entra ou sai, o WebSocket de presença envia:

```json
{
  "type": "contact_status_updated",
  "user_id": "uuid",
  "status": "online"
}
```

O frontend atualiza a bolinha do contato automaticamente.

---

### 5. Correção adicional no chat

Também foi ajustado o token do WebSocket do chat para usar o mesmo token do login:

```txt
msn_auth_token
```

Antes havia divergência entre `auth_token` e `msn_auth_token`.

---

## Como testar

1. Abra o sistema em uma janela normal com o usuário A.
2. Abra o sistema em uma janela anônima com o usuário B.
3. Usuário A pesquisa o usuário B e envia solicitação.
4. Usuário B deve ver a solicitação sem atualizar a página.
5. Usuário B aceita.
6. Os dois devem ver o contato na lista sem refresh.
7. O status online deve aparecer automaticamente.

