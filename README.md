# FIFA Content Engine

Plataforma de automação para transformar gravações de partidas de FIFA em conteúdo digital de forma inteligente.

## Objetivo

O projeto não é apenas um cortador de vídeos. O objetivo é construir uma fábrica de conteúdo capaz de:

- receber partidas completas;
- analisar eventos e momentos relevantes;
- selecionar oportunidades de conteúdo;
- gerar vídeos curtos e outros formatos;
- adicionar edição, legendas e identidade visual;
- gerar títulos, descrições, hashtags e CTAs;
- preparar e, futuramente, publicar conteúdo em múltiplas plataformas;
- medir desempenho e usar os dados para melhorar a seleção de conteúdo.

## Status

**Sprint 1 — Foundation** em validação.

## Desenvolvimento

O código fica em `src/fifa_content_engine` e os testes em `tests`.

Nunca versionar vídeos, credenciais, tokens ou arquivos temporários. Use `.env` localmente a partir de `.env.example`.

## Próxima etapa

Depois da validação da Foundation: **Sprint 2 — Video Engine**.
