"""Data Layer.

Armazena partidas, clipes, publicações, snapshots de métricas e receita
usados pelas demais camadas do pipeline, em arquivos JSON simples (ver
json_store.JSONStore e repository.PipelineRepository). O Dashboard
(dashboard.py) monta um resumo agregado; o Analytics (analytics.py)
monta o relatório de desempenho por clipe/plataforma; o Monetization
(monetization.py) agrega a receita registrada manualmente.
"""
