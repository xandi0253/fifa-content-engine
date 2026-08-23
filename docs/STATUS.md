# Status do Projeto

## Sprint atual

**Sprint 1 — Foundation (concluída)**

## Estado

Estrutura completa de módulos criada (video_engine, ai_engine, content_engine,
publishing_engine, data_layer), lint/format configurado com ruff, pipeline de
CI no GitHub Actions (lint + format check + testes) e esqueleto inicial do
Video Engine (interface `VideoIngestor` + `VideoSource`) com testes passando.

Próximo foco: Sprint 2 — Video Engine (ingestão real de vídeo com FFmpeg,
detecção de cenas, conversão).
