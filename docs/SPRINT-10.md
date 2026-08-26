# Sprint 10 — Monetization

## Objetivo

Registrar manualmente a receita recebida por clipe/plataforma (ex:
repasse de anúncios) e apresentar um resumo agregado.

## Entregas

- [x] `repository.py` — novo método `record_revenue()`: registra um
      valor de receita (amount, currency, note opcional) por clipe/
      plataforma
- [x] `monetization.py` — `build_revenue_summary()` (soma total, total
      por plataforma, detecta moedas diferentes) e `format_revenue_summary()`
      (formata o relatório, com aviso se houver mistura de moedas)
- [x] CLI estendida com o subcomando `revenue`
- [x] Testes cobrindo o registro, a agregação e a formatação (incluindo
      o caso de moedas diferentes)

## Decisões técnicas

- **Sem integração com APIs de pagamento** — os valores são informados
  manualmente por quem opera o pipeline, via `record_revenue()`
- Moeda padrão: BRL
- **Sem conversão entre moedas**: se houver registros em moedas
  diferentes, o total soma os valores numéricos sem converter — o
  relatório emite um aviso explícito nesse caso (`has_mixed_currencies`),
  em vez de somar silenciosamente valores incompatíveis

## Critério de conclusão

Valores de receita podem ser registrados via `record_revenue()` e
visualizados através de `python -m fifa_content_engine revenue`,
agregados por plataforma — validado por testes automatizados e por um
teste manual de ponta a ponta.

---

# Roadmap completo

Com esta sprint, as 10 sprints do roadmap original estão implementadas:

1. ✅ Foundation
2. ✅ Video Engine
3. ✅ AI Analysis
4. ✅ Content Generation
5. ✅ YouTube
6. ✅ Instagram
7. ✅ TikTok
8. ✅ Dashboard
9. ✅ Analytics
10. ✅ Monetization

## O que falta para uso em produção (fora do escopo das sprints)

- Implementar um `MediaHoster` concreto (Instagram e TikTok exigem URL
  pública do clipe — ver Sprint 6)
- Capturar o media_id (Instagram) e o video_id definitivo (TikTok) nas
  publicações, para permitir analytics automatizado dessas duas
  plataformas (ver Sprint 9)
- Conectar o `PipelineRepository` automaticamente às etapas do pipeline
  (Video/AI/Content/Publishing Engine) — hoje ele existe como
  infraestrutura, mas precisa ser chamado explicitamente (ver Sprint 8)
- Configurar credenciais reais de cada plataforma (OpenAI, YouTube,
  Instagram, TikTok) no `.env`
