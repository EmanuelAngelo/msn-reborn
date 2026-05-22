# Correção v9 — Perfil, status manual, mensagem pessoal e foto

Esta atualização adiciona ao MVP do MSN Reborn os ajustes de perfil que estavam faltando.

## O que foi adicionado

### 1. Alteração manual de status

Agora o usuário consegue escolher manualmente:

- Online
- Ausente
- Ocupado
- Invisível
- Offline

A alteração é salva no backend e enviada em tempo real para os contatos conectados pelo WebSocket de presença.

### 2. Mensagem pessoal / subnick

Foi adicionada edição da mensagem pessoal, simulando o antigo subnick do MSN.

Exemplo:

```text
Codando e tomando café ☕
```

Quando o usuário salva, os contatos recebem a atualização sem precisar atualizar a página.

### 3. Nome de exibição

O usuário também pode alterar o nome que aparece na lista de contatos e na tela principal.

### 4. Foto de perfil

Agora o usuário consegue escolher uma imagem local para o perfil.

O backend salva o arquivo em:

```text
media/avatars/
```

Durante desenvolvimento local, o Django serve os arquivos de mídia quando `DEBUG=True`.

### 5. Atualização em tempo real para contatos

Foi criado o evento de presença:

```json
{
  "type": "profile_updated",
  "user_id": "uuid-do-usuario",
  "profile": {}
}
```

Esse evento atualiza nos contatos:

- status;
- mensagem pessoal;
- nome de exibição;
- foto de perfil.

## Arquivos alterados

Backend:

```text
msn/serializers.py
msn/views.py
msn/consumers.py
```

Frontend:

```text
frontend/src/services/auth.js
frontend/src/services/presenceSocket.js
frontend/src/App.vue
frontend/src/components/ProfilePanel.vue
frontend/src/components/ContactList.vue
```

## Observação

A imagem de perfil depende do pacote `Pillow`, que já está no `requirements.txt`.

Se o upload de imagem falhar, rode:

```powershell
pip install -r requirements.txt
```

Depois reinicie o backend.
