# Status do Projeto

## Sprint atual

**Sprint 6 — Instagram (concluída)**

## Estado

Publishing Engine estendido para o Instagram (Reels): interface
`MediaHoster` (contrato plugável, sem implementação concreta ainda — a
hospedagem real fica para configurar depois), cliente da Instagram Graph
API (contêiner de mídia, polling de status, publicação, permalink), e
`InstagramPublisher` orquestrando o fluxo completo. Testes cobrem tudo
com mocks, sem depender de credenciais reais nem chamadas de rede.

Próximo foco: Sprint 7 — TikTok (integração com a API do TikTok para
publicação dos clipes).
