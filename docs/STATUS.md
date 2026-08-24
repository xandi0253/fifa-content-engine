# Status do Projeto

## Sprint atual

**Sprint 5 — YouTube (concluída)**

## Estado

Publishing Engine implementado para o YouTube: autenticação OAuth 2.0
(installed-app flow, com token reutilizado entre execuções), montagem de
metadados (título/descrição/tags/categoria/privacidade) e upload via
YouTube Data API v3. Uma `PublishingQueue` processa vários clipes isolando
falhas por item. Testes cobrem tudo com um publisher falso (mock), sem
depender de credenciais reais nem do fluxo OAuth interativo.

Privacidade padrão dos vídeos: `public`. Recomenda-se testar com
`private`/`unlisted` antes de publicar em produção.

Próximo foco: Sprint 6 — Instagram (integração com a API do Instagram
para publicação dos clipes como Reels).
