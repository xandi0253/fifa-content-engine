# Status do Projeto

## Sprint atual

**Sprint 9 — Analytics (concluída)**

## Estado

Clientes de estatísticas implementados para as 3 plataformas (YouTube,
Instagram, TikTok), um novo `record_stats_snapshot()` no repositório para
guardar medições ao longo do tempo, e um relatório de desempenho
(`python -m fifa_content_engine analytics`) que junta clipes com a
métrica mais recente de cada plataforma, ordenado por views.

Limitação documentada: buscar estatísticas do YouTube funciona de ponta
a ponta (o video_id vem da própria URL salva), mas Instagram e TikTok
exigem ids que os publishers atuais não retornam ainda (media_id/
video_id reais) — ver docs/SPRINT-9.md.

Próximo foco: Sprint 10 — Monetization (registro manual de receita por
clipe/plataforma).
