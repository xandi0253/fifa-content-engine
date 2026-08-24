# Status do Projeto

## Sprint atual

**Sprint 4 — Content Generation (concluída)**

## Estado

Content Engine implementado: clipes de vídeo com duração variável (padding
por tipo de momento, ajustado pelo score), corte via ffmpeg, e legenda/caption
montada a partir dos dados já gerados pelo AI Engine (sem chamada extra à
IA). `ContentGenerator` orquestra tudo, filtrando apenas moments relevantes
e recortando a janela de corte para caber na duração real do vídeo.

Próximo foco: Sprint 5 — YouTube (integração com a YouTube Data API v3
para publicação automática dos clipes gerados).
