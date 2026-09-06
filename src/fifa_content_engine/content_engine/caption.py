"""Geração de legenda/caption para posts, a partir dos dados já produzidos pela IA.

Não faz nenhuma chamada extra a modelos de IA: reaproveita title/description/
moment_type que o AI Engine já gerou, sem custo adicional.
"""

from __future__ import annotations

from fifa_content_engine.ai_engine.moments import Moment

# Hashtags fixas genéricas, aplicadas a qualquer jogo.
BASE_HASHTAGS = ["#Gameplay", "#Highlights", "#Gaming"]

MOMENT_HASHTAGS: dict[str, list[str]] = {
    "vitoria": ["#Vitória"],
    "comemoracao": ["#Comemoração"],
    "quase": ["#QuaseLá"],
    "acao_intensa": ["#AçãoIntensa"],
    "falha": [],
    "outro": [],
}


def _game_hashtag(game_name: str | None) -> list[str]:
    if not game_name:
        return []
    return ["#" + "".join(game_name.split())]


def build_caption(moment: Moment, game_name: str | None = None) -> str:
    """Monta a legenda do post: título como headline, descrição como corpo,
    e hashtags relacionadas ao tipo do momento e (opcionalmente) ao jogo.
    """
    hashtags = (
        BASE_HASHTAGS + _game_hashtag(game_name) + MOMENT_HASHTAGS.get(moment.moment_type, [])
    )
    hashtags_line = " ".join(hashtags)

    return f"{moment.title}\n\n{moment.description}\n\n{hashtags_line}"
