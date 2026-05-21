# Política de Segurança — MSN Reborn

Este documento descreve recomendações de segurança para desenvolvimento, testes e futura produção do projeto **MSN Reborn**.

---

## 1. Versões suportadas

Durante a fase de MVP, apenas a versão principal em desenvolvimento é considerada suportada.

| Versão | Suporte |
|---|---|
| MVP atual | Sim |
| versões antigas de teste | Não |

---

## 2. Como reportar vulnerabilidades

Caso identifique uma falha de segurança, não publique detalhes em issues públicas.

Reporte diretamente ao mantenedor do projeto com:

1. Descrição do problema.
2. Passos para reproduzir.
3. Impacto esperado.
4. Arquivos ou endpoints envolvidos.
5. Sugestão de correção, se houver.

---

## 3. Credenciais e segredos

Nunca exponha em repositório:

- `SECRET_KEY` do Django;
- `SPOTIFY_CLIENT_SECRET`;
- access tokens;
- refresh tokens;
- senhas de banco;
- tokens de autenticação;
- arquivos `.env` reais;
- dumps de banco de produção.

Se qualquer segredo for exposto:

1. Revogue imediatamente.
2. Gere uma nova credencial.
3. Atualize a aplicação.
4. Revise logs e histórico de commits.

---

## 4. Backend Django

Recomendações mínimas antes de produção:

1. Usar `DEBUG = False`.
2. Configurar `ALLOWED_HOSTS`.
3. Usar HTTPS.
4. Usar banco PostgreSQL.
5. Configurar CORS apenas para domínios confiáveis.
6. Proteger rotas com autenticação.
7. Validar se o usuário tem acesso à conversa antes de retornar mensagens.
8. Validar se o usuário tem relação de contato antes de abrir conversa.
9. Não registrar tokens em logs.
10. Usar armazenamento seguro para tokens OAuth.

---

## 5. WebSocket

O WebSocket deve validar:

1. Token de autenticação.
2. Permissão de acesso à conversa.
3. Participação real do usuário na conversa.
4. Eventos recebidos do cliente.
5. Tamanho máximo de mensagem.

Em produção, recomenda-se usar Redis como channel layer.

---

## 6. Spotify

Regras específicas:

1. O `Client Secret` fica somente no backend.
2. O frontend nunca deve receber o `Client Secret`.
3. Tokens do usuário devem ser protegidos.
4. Scopes devem ser mínimos.
5. Para o MVP, usar apenas `user-read-currently-playing`.
6. Se o usuário desconectar o Spotify, os tokens devem ser removidos ou desativados.
7. Em caso de vazamento, regenerar o secret no Spotify Developer Dashboard.

---

## 7. Frontend

Recomendações:

1. Não colocar segredos no Vue.
2. Não armazenar informações sensíveis desnecessárias no `localStorage`.
3. Tratar erros de API sem expor detalhes internos.
4. Validar estados de autenticação.
5. Evitar renderizar HTML vindo de usuários sem sanitização.

---

## 8. Dados pessoais

O projeto pode manipular:

- nome de usuário;
- e-mail;
- foto de perfil;
- status online;
- frase pessoal;
- contatos;
- mensagens;
- música atual do Spotify.

Esses dados devem ser tratados como privados.

---

## 9. Checklist antes de produção

Antes de publicar:

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` segura
- [ ] PostgreSQL configurado
- [ ] HTTPS configurado
- [ ] Redis configurado para Channels
- [ ] CORS restrito
- [ ] CSRF revisado
- [ ] tokens Spotify protegidos
- [ ] logs sem segredos
- [ ] política de privacidade criada
- [ ] termos de uso criados
- [ ] backups configurados
- [ ] permissões revisadas
- [ ] testes de autenticação executados
- [ ] testes de WebSocket executados

---

## 10. Observação

Este projeto ainda está em evolução. A segurança deve ser revisada continuamente conforme novas funcionalidades forem adicionadas.
