# Sprint 3 — AI Analysis

## Objetivo

Identificar momentos relevantes das partidas a partir dos timestamps
candidatos gerados pelo Video Engine, e gerar metadados de conteúdo
(título, descrição) para cada um, usando a API de visão da OpenAI.

## Entregas

- [x] `frame_extraction.py` — extrai um frame (JPEG) do vídeo em um
      timestamp específico, via ffmpeg
- [x] `classifier.py` — interface `FrameClassifier` (contrato)
- [x] `openai_classifier.py` — `OpenAIFrameClassifier`, implementação
      concreta usando `gpt-4o` com visão (resposta forçada em JSON)
- [x] `moments.py` — dataclass `Moment` e parser/validador da resposta
      do modelo (`parse_model_response`)
- [x] `analyzer.py` — `AIMomentAnalyzer` orquestra extração + classificação
      + parsing para uma lista de timestamps
- [x] Testes cobrindo parsing, extração de frame e o pipeline completo,
      usando um `FakeFrameClassifier` — nenhum teste chama a API real da
      OpenAI (sem custo, sem necessidade de chave configurada)
- [x] Dependência `openai` adicionada ao `pyproject.toml`

## Decisões técnicas

- Provedor de IA: OpenAI (GPT-4o com visão)
- Resposta estruturada em JSON: `is_relevant`, `moment_type`, `score`,
  `title`, `description`
- Testes usam mock (`FakeFrameClassifier`) — sem chamadas reais à API
- O cliente da OpenAI é instanciado de forma preguiçosa (lazy), então a
  dependência só é usada de fato quando `OpenAIFrameClassifier.classify()`
  é chamado, mantendo os testes rápidos e desacoplados

## Configuração necessária

Para usar `OpenAIFrameClassifier` de verdade (fora dos testes), é preciso
definir `OPENAI_API_KEY` no `.env` (ver `.env.example`).

## Critério de conclusão

Uma lista de timestamps candidatos (vinda do Video Engine) pode ser
transformada em uma lista de `Moment`, cada um com classificação de
relevância, tipo, score, título e descrição — validado por testes
automatizados de ponta a ponta.
