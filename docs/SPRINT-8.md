# Sprint 8 — Dashboard

## Objetivo

Persistir os dados produzidos pelo pipeline (partidas, clipes,
publicações) e apresentar um resumo agregado via CLI.

## Entregas

- [x] `json_store.py` — `JSONStore`, armazenamento genérico em arquivos
      JSON (uma "tabela" por arquivo: matches.json, clips.json,
      publications.json)
- [x] `repository.py` — `PipelineRepository`, com métodos para registrar
      partidas processadas, clipes gerados e publicações (sucesso/falha)
- [x] `dashboard.py` — `build_summary()` (agrega totais, taxa de sucesso,
      publicações por plataforma) e `print_summary()` (formata e imprime
      o relatório)
- [x] CLI estendida com o subcomando `dashboard` (`python -m
      fifa_content_engine dashboard`)
- [x] Configuração `DATA_DIR` adicionada (`.env`/`Settings`), com padrão
      `.fifa_data/` (ignorado pelo git)
- [x] Testes cobrindo o armazenamento, o repositório e o resumo agregado

## Decisões técnicas

- Persistência: arquivos JSON simples, sem banco de dados
- Apresentação: relatório via CLI, sem dependência nova
- **Direção de dependência importante**: o Data Layer não importa nada
  de `video_engine`/`ai_engine`/`content_engine`/`publishing_engine` —
  são esses módulos que vão chamar o `PipelineRepository` para persistir
  o que produzem. Isso mantém o Data Layer como uma camada de base,
  sem acoplamento com as camadas de cima

## Ainda não integrado

Esta sprint entrega a infraestrutura de persistência e o relatório, mas
**ainda não conecta automaticamente** o `PipelineRepository` às etapas do
pipeline (Video Engine, Content Engine, Publishing Engine) — ou seja, os
dados só aparecem no dashboard se algo chamar `record_match`/`record_clip`/
`record_publication` explicitamente. Conectar isso ao fluxo principal do
pipeline é um bom próximo passo, mas ficou fora do escopo desta sprint
para não misturar "criar a infraestrutura" com "integrar em todo lugar".

## Critério de conclusão

Partidas, clipes e publicações podem ser registrados via
`PipelineRepository` e visualizados através de `python -m
fifa_content_engine dashboard` — validado por testes automatizados e por
um teste manual de ponta a ponta.
