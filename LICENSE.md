# Licença de Uso e Segurança — MSN Reborn

Copyright (c) 2026 Manel/Emanuel Coutinho

Este projeto, provisoriamente chamado **MSN Reborn**, é uma aplicação de mensageria em tempo real inspirada em experiências clássicas de comunicadores instantâneos, desenvolvida com Django, Django REST Framework, WebSocket, Vue.js, TailwindCSS e integração com Spotify.

Esta licença foi criada para permitir a evolução do projeto com segurança, preservando a autoria, impedindo uso indevido e deixando claro que credenciais, tokens, integrações e dados de usuários devem ser tratados com responsabilidade.

---

## 1. Permissões concedidas

É permitido:

1. Usar este projeto para estudo, desenvolvimento, testes locais e evolução pessoal.
2. Modificar o código-fonte para criar novas funcionalidades.
3. Criar forks privados para desenvolvimento e experimentação.
4. Usar trechos do código como referência técnica em outros projetos pessoais ou internos.
5. Executar a aplicação em ambiente local, homologação ou produção própria.

---

## 2. Restrições

Não é permitido, sem autorização expressa do autor:

1. Vender este projeto como produto próprio.
2. Redistribuir o projeto completo como se fosse de autoria de terceiros.
3. Remover créditos, referências de autoria ou avisos de licença.
4. Publicar versões modificadas sem informar que são derivadas deste projeto.
5. Usar o nome **MSN Reborn** ou identidade visual associada para fins comerciais sem autorização.
6. Inserir, manter ou distribuir credenciais reais no código-fonte, incluindo:
   - Client Secret do Spotify;
   - Access Token;
   - Refresh Token;
   - Secret Key do Django;
   - senhas de banco de dados;
   - chaves de API;
   - tokens de autenticação.

---

## 3. Segurança e proteção de credenciais

Este projeto pode integrar serviços externos, como a API do Spotify. Por isso, é obrigatório seguir estas regras:

1. Nunca versionar credenciais reais em repositórios públicos.
2. Nunca expor `SPOTIFY_CLIENT_SECRET` no frontend.
3. Nunca salvar tokens sensíveis em código-fonte.
4. Em produção, armazenar segredos em variáveis de ambiente ou serviço seguro de secrets.
5. Regenerar imediatamente qualquer credencial exposta acidentalmente.
6. Usar HTTPS em ambiente de produção.
7. Proteger rotas autenticadas com autenticação adequada.
8. Validar permissões de acesso antes de entregar mensagens, contatos ou dados de perfil.
9. Evitar logs contendo tokens, senhas, códigos OAuth ou dados sensíveis de usuários.
10. Respeitar as políticas oficiais dos serviços integrados, incluindo Spotify Developer Terms.

---

## 4. Dados dos usuários

Quem operar, hospedar ou modificar este projeto deve respeitar a privacidade dos usuários.

Dados como mensagens, status online, contatos, perfil, foto, música atual e tokens de integração devem ser tratados como informações privadas.

É proibido:

1. Coletar dados sem informar o usuário.
2. Expor mensagens privadas.
3. Compartilhar tokens de integração.
4. Usar dados de reprodução musical para rastreamento indevido.
5. Manter dados sensíveis sem necessidade técnica.

Recomenda-se implementar, antes de produção:

1. Política de privacidade.
2. Termos de uso.
3. Criptografia ou proteção adequada para tokens sensíveis.
4. Rotina de exclusão de conta e remoção de dados.
5. Logs de auditoria para ações críticas.

---

## 5. Uso da API do Spotify

A integração com Spotify deve seguir as regras oficiais da plataforma.

Este projeto deve usar a API do Spotify apenas para funcionalidades autorizadas pelo usuário, como exibir a música atualmente em reprodução no status.

O uso recomendado no MVP é:

- `user-read-currently-playing`

Não é permitido usar tokens do Spotify para acessar, manipular ou coletar dados além do escopo autorizado pelo usuário.

O `Client Secret` deve permanecer exclusivamente no backend.

---

## 6. Responsabilidade sobre implantação

O projeto é fornecido em estado de desenvolvimento.

Antes de usar em produção, é responsabilidade de quem implanta:

1. Revisar configurações de segurança.
2. Trocar `DEBUG=True` para `DEBUG=False`.
3. Configurar `ALLOWED_HOSTS` corretamente.
4. Usar banco de dados adequado, como PostgreSQL.
5. Configurar HTTPS.
6. Configurar Redis ou outro backend apropriado para WebSocket em produção.
7. Proteger arquivos estáticos e mídias.
8. Garantir backup dos dados.
9. Revisar autenticação e permissões.
10. Fazer testes de segurança.

---

## 7. Ausência de garantia

Este software é fornecido "como está", sem garantias de qualquer tipo.

O autor não se responsabiliza por:

1. Perda de dados.
2. Falhas de segurança causadas por má configuração.
3. Uso indevido de credenciais.
4. Violação de políticas de terceiros.
5. Indisponibilidade de APIs externas.
6. Danos diretos ou indiretos decorrentes do uso do projeto.

---

## 8. Contribuições

Contribuições são bem-vindas, desde que respeitem:

1. A arquitetura do projeto.
2. As boas práticas de segurança.
3. A privacidade dos usuários.
4. A autoria original.
5. A proposta do projeto.

Ao contribuir, o colaborador declara que possui direito sobre o código enviado e autoriza seu uso dentro deste projeto.

---

## 9. Uso comercial

O uso comercial deste projeto, total ou parcial, exige autorização prévia do autor.

Isso inclui:

1. Venda do sistema.
2. Oferta como SaaS.
3. Hospedagem para terceiros mediante cobrança.
4. Uso por empresas como produto final.
5. Revenda ou empacotamento comercial.

O uso interno, experimental ou educacional não exige autorização adicional, desde que respeite esta licença.

---

## 10. Créditos

Projeto idealizado e evoluído por:

**Manel/Emanuel Coutinho**

Com foco em criar uma experiência moderna de mensageria inspirada no antigo MSN, utilizando tecnologias atuais e boas práticas de desenvolvimento web.

---

## 11. Resumo simples

Você pode estudar, modificar e evoluir o projeto.

Você não pode vender, redistribuir como se fosse seu, remover créditos ou expor credenciais.

Se for colocar em produção, revise segurança, privacidade, autenticação, banco de dados, HTTPS e tokens.

---

Última atualização: 21/05/2026.
