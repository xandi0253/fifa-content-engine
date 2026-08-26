# Sprint 9 — Analytics

## Objetivo

Buscar métricas reais de engajamento (views, likes, comentários) das
plataformas de publicação e apresentar um relatório de desempenho do
conteúdo.

## Entregas

- [x] `youtube_stats.py` — `get_video_statistics()` (usa a mesma
      autenticação OAuth do YouTubePublisher) e `extract_video_id()`
      (extrai o video_id da URL armazenada)
- [x] `instagram_stats.py` — `get_media_insights()` (like_count,
      comment_count via Graph API)
- [x] `tiktok_stats.py` — `get_video_stats()` (view/like/comment/share
      count via Content Posting API)
- [x] `repository.py` — novo método `record_stats_snapshot()`: registra
      uma medição pontual de métricas por clipe/plataforma, permitindo
      acompanhar a evolução ao longo do tempo
- [x] `analytics.py` — `build_performance_report()` junta clipes com o
      snapshot mais recente de cada plataforma; `format_performance_report()`
      formata ordenado por `view_count`
- [x] CLI estendida com o subcomando `analytics`
- [x] Testes cobrindo os três clientes de estatísticas (com mock) e o
      relatório de desempenho — nenhum teste chama APIs reais

## Limitação conhecida (documentada, não resolvida nesta sprint)

`get_video_statistics()` do YouTube funciona de ponta a ponta porque o
video_id pode ser extraído da própria URL armazenada. **Isso não é
verdade para Instagram e TikTok**:
- Instagram: `get_media_insights()` exige o `media_id` numérico da
  Graph API, mas o `InstagramPublisher` (Sprint 6) retorna apenas o
  permalink (com o shortcode, não o media_id)
- TikTok: `get_video_stats()` exige o `video_id` definitivo, mas o
  `TikTokPublisher` (Sprint 7) retorna apenas o `publish_id`

Ou seja, buscar métricas de Instagram/TikTok funciona (testado com
mocks), mas **não há automação hoje** que resolva o id certo a partir do
que está salvo em `publications`. Resolver isso — guardando o id nativo
de cada plataforma junto da publicação — é um bom próximo passo, fora do
escopo desta sprint.

## Critério de conclusão

Métricas podem ser registradas via `record_stats_snapshot()` e
visualizadas através de `python -m fifa_content_engine analytics`,
ordenadas por desempenho — validado por testes automatizados e por um
teste manual de ponta a ponta.
