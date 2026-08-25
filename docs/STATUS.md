# Status do Projeto

## Sprint atual

**Sprint 8 — Dashboard (concluída)**

## Estado

Data Layer implementado: armazenamento em arquivos JSON (`JSONStore`),
`PipelineRepository` para registrar partidas/clipes/publicações, e um
Dashboard via CLI (`python -m fifa_content_engine dashboard`) que mostra
totais e taxa de sucesso das publicações por plataforma.

Nota: a infraestrutura de persistência ainda não está conectada
automaticamente às etapas do pipeline (Video/AI/Content/Publishing
Engine) — os dados aparecem no dashboard apenas quando algo chama o
`PipelineRepository` explicitamente. Ver docs/SPRINT-8.md para detalhes.

Próximo foco: Sprint 9 — Analytics (métricas mais detalhadas sobre o
desempenho do conteúdo publicado).
