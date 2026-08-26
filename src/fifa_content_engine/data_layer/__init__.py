"""Data Layer.

Armazena partidas, clipes, publicações e snapshots de métricas usados
pelas demais camadas do pipeline, em arquivos JSON simples (ver
json_store.JSONStore e repository.PipelineRepository). O Dashboard
(dashboard.py) monta um resumo agregado; o Analytics (analytics.py)
monta o relatório de desempenho por clipe/plataforma, a partir dos
snapshots de métricas buscados nas APIs (ver publishing_engine/
youtube_stats.py, instagram_stats.py, tiktok_stats.py).
"""
