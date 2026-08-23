# Status do Projeto

## Sprint atual

**Sprint 2 — Video Engine (concluída)**

## Estado

Video Engine implementado com ffmpeg/ffprobe via subprocess: validação real
de arquivos (extensão + stream de vídeo via ffprobe), normalização para
mp4/h264/aac, e detecção de mudanças de cena usando o filtro nativo do
ffmpeg. Tudo coberto por testes de ponta a ponta com vídeo sintético gerado
via lavfi, sem depender de arquivos externos.

Próximo foco: Sprint 3 — AI Analysis (identificar momentos relevantes das
partidas a partir dos candidatos a cena e gerar metadados de conteúdo).
