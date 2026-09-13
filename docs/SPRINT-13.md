# Sprint 13 — Seleção manual de trecho do vídeo

## Objetivo

Permitir escolher manualmente um trecho específico do vídeo (do minuto
X ao minuto Y) para processar, em vez de depender só da detecção
automática de cena no vídeo inteiro.

## Contexto

Antes desta sprint, testar um trecho específico exigia cortar
manualmente com ffmpeg (`-ss`/`-t`) antes de rodar o pipeline -- foi
exatamente o que fizemos várias vezes nos testes reais com FIFA 26 e
Mortal Kombat 1 (pra pular introduções/menus). Esta sprint embute isso
direto no pipeline.

## Entregas

- [x] `trimming.py` (novo, em video_engine) — `trim_video()` corta um
      trecho do vídeo via ffmpeg (`-c copy`, rápido, sem recodificar)
- [x] `errors.py` — nova exceção `TrimError`
- [x] `run_pipeline.py` — novos argumentos `--start-minute` e
      `--end-minute` (precisam ser usados juntos); quando informados,
      corta o vídeo antes de processar
- [x] Testes cobrindo corte válido, intervalo inválido (fim antes do
      início), início negativo, arquivo de origem ausente

## Correção incluída (fora do escopo original, descoberta ao verificar)

O `DEFAULT_SCENE_THRESHOLD` tinha revertido para `0.4` no main (a
correção da sessão anterior, que reduzia para `0.2`, não tinha sido
mergeada de fato). Corrigido novamente aqui.

## Critério de conclusão

Um trecho específico do vídeo (minuto X a Y) pode ser processado sem
precisar de um comando ffmpeg manual separado — validado por testes
automatizados e por teste manual reproduzindo o fluxo completo
(corte → normalização → detecção de cena).
