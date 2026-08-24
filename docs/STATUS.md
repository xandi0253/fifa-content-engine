# Status do Projeto

## Sprint atual

**Sprint 7 — TikTok (concluída)**

## Estado

Publishing Engine estendido para o TikTok: cliente da Content Posting API
(`init_video_post` via PULL_FROM_URL, `get_post_status` para polling) e
`TikTokPublisher` orquestrando hospedagem (reaproveitando o `MediaHoster`
da Sprint 6) + publicação. Testes cobrem tudo com mocks, sem depender de
credenciais reais nem chamadas de rede.

As três plataformas de vídeo do roadmap (YouTube, Instagram, TikTok)
estão implementadas. Falta apenas configurar um `MediaHoster` concreto e
as credenciais reais de cada plataforma para publicar de verdade.

Próximo foco: Sprint 8 — Dashboard (visualização do status do pipeline
e do conteúdo gerado/publicado).
