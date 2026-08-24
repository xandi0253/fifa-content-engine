# Sprint 4 — Content Generation

## Objetivo

Transformar os `Moment`s relevantes identificados pelo AI Engine em
conteúdo pronto para publicação: um clipe de vídeo cortado e uma
legenda/caption, sem nenhuma chamada extra a modelos de IA.

## Entregas

- [x] `clip_duration.py` — regra de duração variável do clipe por
      `moment_type` (padding base) e `score` (multiplicador de 0.7x a 1.3x)
- [x] `clip_extraction.py` — corta o clipe de vídeo com ffmpeg na janela
      calculada, recodificando para garantir corte preciso
- [x] `caption.py` — monta a legenda reaproveitando title/description do
      AI Engine, com hashtags fixas por tipo de momento
- [x] `content_piece.py` — `ContentPiece` (moment + clip_path + caption)
- [x] `generator.py` — `ContentGenerator` orquestra tudo: filtra apenas
      moments relevantes, calcula a janela, recorta com base na duração
      real do vídeo (via `video_engine.ffprobe`), corta o clipe e monta
      a legenda
- [x] Testes cobrindo as regras de duração, corte de clipe, legenda e o
      pipeline completo de ponta a ponta

## Decisões técnicas

- Duração do clipe: variável, com padding base por tipo de momento e
  ajuste pelo score (gol tem o maior padding: 8s antes / 12s depois)
- Legenda gerada junto com o clipe nesta sprint, sem nova chamada à API
  (reaproveita os dados já gerados na Sprint 3)
- A janela de corte é sempre recortada para caber dentro da duração real
  do vídeo (não corta antes do início nem além do fim)

## Critério de conclusão

Uma lista de `Moment`s (vinda do AI Engine) pode ser transformada em uma
lista de `ContentPiece` — cada um com um clipe de vídeo existente no disco
e uma legenda pronta — validado por testes automatizados de ponta a ponta.
