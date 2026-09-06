# Status do Projeto

## Sprint atual

**Sprint 11 — Generalização multi-jogo + legendas automáticas (concluída)**

## Estado

Roadmap original (10 sprints) completo e **validado com dados reais**:
rodou o pipeline inteiro com gravação real de FIFA 26, incluindo
autenticação OAuth de verdade, chamada real à API da OpenAI, e publicação
real (e depois pública) no YouTube.

A partir daí, o projeto entrou em uma segunda fase: transformar-se em um
produto para qualquer jogo, não só FIFA. Sprint 11 é o primeiro passo
dessa fase — generalização da taxonomia de momentos, do prompt da IA, das
hashtags/tags, e legendas automáticas queimadas no clipe. Ver
docs/SPRINT-11.md.

## Pendências para uso em produção (fora do escopo das sprints)

- Implementar um `MediaHoster` concreto (Instagram/TikTok exigem URL
  pública do clipe)
- Capturar media_id (Instagram) e video_id definitivo (TikTok) nas
  publicações, para permitir analytics automatizado dessas plataformas
- Conectar o `PipelineRepository` automaticamente às etapas do pipeline
  (hoje precisa ser chamado explicitamente)
- Configurar credenciais reais de cada plataforma no `.env`

## Pendências para virar produto multi-usuário (visão de longo prazo)

- Torcida/efeitos sonoros, narração automática (fora do escopo da Sprint 11)
- Multi-usuário, assinatura, billing
- Interface (app/web) para uso sem precisar mexer em código

Ver docs/SPRINT-10.md e docs/SPRINT-11.md para o detalhamento completo.
