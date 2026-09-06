# Sprint 11 — Generalização multi-jogo + legendas automáticas

## Objetivo

Primeiro passo rumo a um produto de assinatura para qualquer criador de
conteúdo de gameplay (não só FIFA): generalizar a taxonomia de momentos e
os textos gerados pela IA para funcionar com qualquer jogo, e adicionar
legendas automáticas queimadas nos clipes.

## Contexto

Depois de refletir sobre o padrão de começar vários projetos ambiciosos
sem terminar, a decisão foi dar sequência ao fifa-content-engine em vez de
começar do zero um produto de assinatura completo. Este é o **menor passo
possível** rumo a esse produto: generalizar o que já existe, sem adicionar
recursos grandes (multi-usuário, billing, torcida, narração) ainda.

## Entregas

- [x] **Taxonomia genérica de momentos**: `gol/falta/defesa/lance_perigoso`
      → `vitoria/quase/comemoracao/falha/acao_intensa/outro`, funciona para
      qualquer gênero de jogo (esportes, FPS, corrida, etc.)
- [x] **Prompt da IA generalizado**: `OpenAIFrameClassifier` aceita um
      `game_context` opcional (ex: "FIFA 26", "Call of Duty"); sem ele, o
      prompt já é genérico para "gameplay"
- [x] **Hashtags/tags generalizadas**: `build_caption()` e
      `build_video_metadata()` aceitam um `game_name` opcional em vez de
      terem "FIFA26" fixo no código
- [x] **Categoria do YouTube**: trocada de "Sports" (17) para "Gaming" (20)
- [x] **Legendas automáticas**: novo módulo `captioning.py`, queima o
      título do momento no rodapé do clipe via ffmpeg. Usa `fontfile`
      explícito (não `font` por nome) para **evitar o bug de fontconfig**
      encontrado no Windows durante os testes reais desta sessão
- [x] `ContentGenerator` ganhou os parâmetros `game_name` e
      `burn_captions` (desligado por padrão — não quebra uso existente)
- [x] Testes atualizados em toda a taxonomia antiga + testes novos para
      captioning e para os parâmetros novos do generator
- [x] Testado manualmente com um jogo de FPS (Call of Duty) e um jogo de
      corrida (Forza Horizon) — confirma que nada de futebol vaza na saída

## Correções incluídas (descobertas no teste real da sessão anterior)

- `youtube_auth.py`: adicionado escopo `youtube.force-ssl`, necessário
  para `videos.update()` (mudar visibilidade depois de publicado) — o
  escopo `youtube.upload` sozinho só permite criar vídeos
- `scene_detection.py`: threshold padrão reduzido de 0.4 para 0.2 —
  testado com gravação real, 0.4 não detectava nada em jogo aberto
- `ffmpeg_ingestor.py`: `scene_threshold` agora configurável no construtor

## O que NÃO entrou nesta sprint (de propósito)

- Suporte a torcida/efeitos sonoros
- Narração automática
- Multi-usuário / assinatura / billing
- Interface (app/web) para outras pessoas usarem sem mexer em código

Essas ficam para depois de validar que o pipeline generalizado funciona
bem na prática, testando com mais de um jogo real.

## Critério de conclusão

O pipeline completo (Video Engine → AI Engine → Content Engine →
Publishing Engine) funciona com qualquer jogo, sem nenhuma referência
hardcoded a futebol/FIFA no código de produção — validado por 120 testes
automatizados e por testes manuais com dois jogos de gêneros diferentes.
