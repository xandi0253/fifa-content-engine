# Sprint 2 — Video Engine

## Objetivo

Implementar o Video Engine de verdade: receber, validar, converter e
detectar cenas em vídeos de partidas, usando ffmpeg/ffprobe via subprocess.

## Entregas

- [x] `ffprobe.py` — wrapper para inspecionar metadados do vídeo (duração,
      codec, presença de stream de vídeo)
- [x] `conversion.py` — normalização para mp4/h264/aac via ffmpeg
- [x] `scene_detection.py` — detecção de mudanças de cena usando o filtro
      nativo `select='gt(scene,threshold)'` do ffmpeg
- [x] `FfmpegVideoIngestor` — implementação concreta de `VideoIngestor`
      combinando validação, conversão e detecção de cenas
- [x] `VideoSource` estendido com `format_name`, `video_codec` e
      `scene_timestamps`
- [x] Testes de ponta a ponta usando vídeo sintético gerado via ffmpeg
      (lavfi), sem depender de arquivos reais de partida

## Decisões técnicas

- ffmpeg chamado via `subprocess` direto (sem dependência `ffmpeg-python`)
- Sem forçar resolução/fps na normalização — apenas container e codecs
- Detecção de cenas é puramente visual (mudança de quadro), sem análise de
  conteúdo — a análise por IA é escopo da Sprint 3

## Critério de conclusão

Um vídeo de entrada pode ser validado, convertido para o formato padrão do
pipeline e ter suas mudanças de cena detectadas, tudo comprovado por testes
automatizados que rodam sem depender de arquivos externos.
