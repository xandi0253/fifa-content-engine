# Status do Projeto

## Sprint atual

**Sprint 3 — AI Analysis (concluída)**

## Estado

AI Engine implementado com a API de visão da OpenAI (GPT-4o): extração de
frames nos timestamps candidatos (via ffmpeg), classificação de cada frame
em um momento estruturado (relevante ou não, tipo, score, título e
descrição), e um analisador (`AIMomentAnalyzer`) que orquestra o pipeline
completo. Testes cobrem tudo com um classificador falso (mock), sem
depender de chave de API real nem gastar créditos.

Próximo foco: Sprint 4 — Content Generation (transformar os momentos
relevantes em conteúdo pronto: Shorts, Reels, posts).
