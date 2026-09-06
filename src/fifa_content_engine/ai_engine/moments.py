"""Estrutura de dados para momentos analisados e parsing da resposta do modelo."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .errors import ModelResponseError

# Taxonomia genérica de momentos, pensada para funcionar em qualquer gênero
# de jogo (esportes, FPS, corrida, etc.), não só futebol:
#   - vitoria: um evento de sucesso/pontuação (gol, kill, vitória de round)
#   - quase: um momento de tensão sem resultado definido (quase gol, quase
#     morreu, ultrapassagem na última curva)
#   - comemoracao: celebração, cutscene de vitória, reação do jogador
#   - falha: um erro, morte, falta ou perda que gera contraste dramático
#   - acao_intensa: uma sequência de ação notável sem categoria mais específica
#   - outro: qualquer evento relevante que não se encaixe nas categorias acima
MOMENT_TYPES = {"vitoria", "quase", "comemoracao", "falha", "acao_intensa", "outro"}

_REQUIRED_KEYS = {"is_relevant", "moment_type", "score", "title", "description"}


@dataclass(frozen=True)
class Moment:
    """Um momento candidato da gravação, já analisado pela IA."""

    timestamp_seconds: float
    is_relevant: bool
    moment_type: str
    score: float
    title: str
    description: str


def parse_model_response(raw_response: str, timestamp_seconds: float) -> Moment:
    """Converte a resposta JSON do modelo em um Moment.

    Levanta ModelResponseError se a resposta não for um JSON válido, se
    faltar alguma chave obrigatória, ou se os tipos/valores não fizerem sentido.
    """
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ModelResponseError(
            f"Resposta do modelo não é um JSON válido: {raw_response!r}"
        ) from exc

    if not isinstance(data, dict):
        raise ModelResponseError(f"Resposta do modelo deveria ser um objeto JSON: {raw_response!r}")

    missing_keys = _REQUIRED_KEYS - data.keys()
    if missing_keys:
        raise ModelResponseError(f"Resposta do modelo faltando chaves: {sorted(missing_keys)}")

    moment_type = str(data["moment_type"])
    if moment_type not in MOMENT_TYPES:
        raise ModelResponseError(
            f"moment_type inválido: {moment_type!r} (esperado um de {sorted(MOMENT_TYPES)})"
        )

    try:
        score = float(data["score"])
    except (TypeError, ValueError) as exc:
        raise ModelResponseError(f"score inválido: {data['score']!r}") from exc

    if not 0.0 <= score <= 1.0:
        raise ModelResponseError(f"score fora do intervalo [0, 1]: {score}")

    return Moment(
        timestamp_seconds=timestamp_seconds,
        is_relevant=bool(data["is_relevant"]),
        moment_type=moment_type,
        score=score,
        title=str(data["title"]),
        description=str(data["description"]),
    )
