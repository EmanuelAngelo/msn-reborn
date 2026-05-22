# Correção — Layout do chat com scroll interno

Nesta atualização o chat deixou de crescer junto com a página e com o menu lateral.

## Problema

Ao enviar muitas mensagens, o componente de chat aumentava a altura da tela inteira. Com isso, o menu lateral também crescia e a experiência ficava ruim.

## Ajuste aplicado

- O `main` agora usa `h-screen overflow-hidden`.
- O grid principal agora ocupa a altura total disponível.
- A lateral usa `flex` e `overflow-y-auto` internamente.
- O `ChatWindow` usa `h-full min-h-0 flex flex-col`.
- A área de mensagens usa `min-h-0 flex-1 overflow-y-auto`, criando scroll apenas dentro da caixa de mensagens.
- O cabeçalho e a barra de envio ficam fixos dentro da janela do chat.

## Arquivos alterados

- `frontend/src/App.vue`
- `frontend/src/components/ChatWindow.vue`

## Resultado esperado

Ao conversar por muito tempo, apenas a área branca das mensagens deve rolar. O menu lateral e a janela principal não devem aumentar de altura.
