# Sprint 12 — Vídeo de melhores momentos (compilação)

## Objetivo

Combinar todos os clipes relevantes de uma gravação em um único vídeo
de "melhores momentos", em vez de gerar vários clipes separados.

## Contexto

Surgiu de um teste real com uma partida de FIFA 26: o pipeline encontrou
4 momentos relevantes (um gol, uma defesa, uma disputa na área e uma
tentativa bloqueada) em 5 minutos de gravação. Publicar 4 vídeos
separados é menos interessante do que um único vídeo com os melhores
lances -- daí a ideia desta sprint.

## Entregas

- [x] `compilation.py` (novo, em content_engine) — `concatenate_clips()`
      junta clipes usando o demuxer concat do ffmpeg, recodificando (não
      `-c copy`) para evitar incompatibilidades sutis entre os clipes
- [x] `build_compilation_piece()` — junta vários `ContentPiece` em um só,
      com título "Melhores Momentos" (+ nome do jogo, se informado),
      score médio dos momentos, e descrição listando os títulos de cada
      lance incluído
- [x] `run_pipeline.py` atualizado: quando há mais de um clipe relevante,
      combina automaticamente em um único vídeo antes de publicar (em
      vez de publicar cada clipe separadamente)
- [x] Testes cobrindo concatenação (duração combinada correta), lista
      vazia (erro), e a montagem do ContentPiece combinado

## Decisões técnicas

- Sempre que há mais de 1 clipe relevante, o pipeline substitui a lista
  de clipes individuais pelo vídeo combinado — não há opção de manter
  os dois (decisão explícita: só o vídeo combinado é publicado)
- Ordem dos clipes no vídeo final: a mesma ordem em que os momentos
  foram analisados (cronológica, já que os timestamps de cena vêm em
  ordem crescente do Video Engine)

## Critério de conclusão

Múltiplos `ContentPiece`s podem ser combinados em um único vídeo válido,
com metadados (título/descrição/score) refletindo o conjunto — validado
por testes automatizados e por teste manual reproduzindo o cenário real
do pipeline completo (Video Engine → AI Engine → Content Engine →
Compilação).
