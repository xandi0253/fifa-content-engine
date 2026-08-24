"""Geração de legenda/caption para posts, a partir dos dados já produzidos pela IA.

Não faz nenhuma chamada extra a modelos de IA: reaproveita title/description/
moment_type que o AI Engine (Sprint 3) já gerou, sem custo adicional.
"""

from __future__ import annotations

from fifa_content_engine.ai_engine.moments import Moment

# Hashtags fixas por tipo de momento, além das hashtags base do projeto.
BASE_HASHTAGS = ["#FIFA26", "#Futebol", "#Highlights"]

MOMENT_HASHTAGS: dict[str, list[str]] = {
    "gol": ["#Gol", "#Golaço"],
    "comemoracao": ["#Comemoração"],
    "lance_perigoso": ["#LancePerigoso"],
    "defesa": ["#DefesaIncrível"],
    "falta": ["#Falta"],
    "outro": [],
}


def build_caption(moment: Moment) -> str:
    """Monta a legenda do post: título como headline, descrição como corpo,
    e hashtags relacionadas ao tipo do momento.
    """
    hashtags = BASE_HASHTAGS + MOMENT_HASHTAGS.get(moment.moment_type, [])
    hashtags_line = " ".join(hashtags)

    return f"{moment.title}\n\n{moment.description}\n\n{hashtags_line}"
