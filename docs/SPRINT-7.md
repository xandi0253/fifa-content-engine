# Sprint 7 — TikTok

## Objetivo

Publicar os clipes gerados pelo Content Engine no TikTok, usando a
TikTok Content Posting API (Direct Post).

## Entregas

- [x] `tiktok_client.py` — wrapper fino da Content Posting API:
      `init_video_post()` (inicia a publicação via PULL_FROM_URL) e
      `get_post_status()` (consulta o status)
- [x] `tiktok_publisher.py` — `TikTokPublisher`, implementação concreta
      de `VideoPublisher`: hospeda o clipe (via `MediaHoster`, mesmo
      contrato da Sprint 6), inicia a publicação e aguarda o status
      `PUBLISH_COMPLETE`
- [x] Testes cobrindo o cliente da API e o publisher (fluxo de sucesso,
      falha de publicação, timeout de polling) — nenhum teste chama a
      API real do TikTok

## Decisões técnicas

- Fonte do vídeo: `PULL_FROM_URL` — reaproveita o `MediaHoster` já
  definido na Sprint 6, em vez de implementar upload de arquivo em chunks
- Privacidade padrão: `PUBLIC_TO_EVERYONE`
- Testes usam mock — sem chamadas reais à API do TikTok

## Limitação importante do retorno

Diferente do YouTube e do Instagram, a TikTok Content Posting API **não
retorna uma URL pública do post** no fluxo de status de publicação. Por
isso, `TikTokPublisher.publish()` retorna uma referência no formato
`"tiktok:publish_id=<id>"`, não uma URL de fato. Isso está documentado
no código para não gerar expectativa equivocada.

## Configuração necessária

Para publicar de verdade (fora dos testes):
1. Uma conta de desenvolvedor no TikTok for Developers com acesso à
   Content Posting API
2. Preencher `TIKTOK_ACCESS_TOKEN` no `.env`
3. Um `MediaHoster` concreto configurado (mesmo requisito da Sprint 6)

## Critério de conclusão

Um `ContentPiece` pode ser publicado no TikTok através do
`TikTokPublisher`, desde que um `MediaHoster` concreto seja fornecido —
validado por testes automatizados que não dependem de credenciais reais
nem de chamadas de rede.
