"""Analisa uma sequência de frames ao redor de um momento."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path

from .errors import ModelResponseError
from .frame_extraction import extract_frame


@dataclass(frozen=True)
class ContextAnalysis:
    """Leitura editorial de uma sequência temporal de frames."""

    setup: str
    tension: str
    climax: str
    outcome: str
    reaction: str
    confidence: float


class ContextAnalyzer:
    """Contrato para análise multimodal de contexto."""

    def analyze(self, frame_paths: list[Path]) -> ContextAnalysis:
        raise NotImplementedError


class OpenAIContextAnalyzer(ContextAnalyzer):
    """Analisa vários frames com visão da OpenAI em uma única solicitação."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise ModelResponseError("OPENAI_API_KEY não configurada.")
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def analyze(self, frame_paths: list[Path]) -> ContextAnalysis:
        if not frame_paths:
            raise ModelResponseError("Nenhum frame foi fornecido para análise de contexto.")

        content = [{
            "type": "text",
            "text": (
                "Analise esta sequência de frames na ordem temporal em que foi enviada. "
                "Ela representa um momento candidato de um vídeo. Identifique o que está "
                "acontecendo antes, durante e depois do evento. Não invente acontecimentos. "
                "Se a sequência não permitir concluir algo, diga 'incerto'. Responda somente "
                "JSON com setup, tension, climax, outcome, reaction e confidence. "
                "confidence deve ser número entre 0 e 1."
            ),
        }]
        for index, frame_path in enumerate(frame_paths):
            image = base64.b64encode(frame_path.read_bytes()).decode("utf-8")
            content.append({"type": "text", "text": f"Frame temporal {index + 1}"})
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
            })

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": content}],
        )
        choices = getattr(response, "choices", None) or []
        message = getattr(choices[0], "message", None) if choices else None
        raw = getattr(message, "content", None) if message else None
        if not raw:
            raise ModelResponseError("A análise multimodal retornou conteúdo vazio.")

        try:
            data = json.loads(raw)
            confidence = float(data.get("confidence", 0.0))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ModelResponseError("A análise multimodal retornou JSON inválido.") from exc

        if not 0.0 <= confidence <= 1.0:
            raise ModelResponseError("confidence da análise multimodal fora do intervalo [0, 1].")

        return ContextAnalysis(
            setup=str(data.get("setup", "incerto")),
            tension=str(data.get("tension", "incerto")),
            climax=str(data.get("climax", "incerto")),
            outcome=str(data.get("outcome", "incerto")),
            reaction=str(data.get("reaction", "incerto")),
            confidence=confidence,
        )


def build_context_timestamps(
    timestamp_seconds: float,
    video_duration: float,
    offsets: tuple[float, ...] = (-4.0, 0.0, 4.0),
) -> list[float]:
    """Cria timestamps antes/durante/depois, limitados à duração do vídeo."""
    return [max(0.0, min(video_duration, timestamp_seconds + offset)) for offset in offsets]


def extract_context_frames(
    video_path: Path,
    timestamp_seconds: float,
    video_duration: float,
    output_dir: Path,
) -> list[Path]:
    """Extrai uma amostra pequena e ordenada do contexto temporal."""
    paths: list[Path] = []
    for timestamp in build_context_timestamps(timestamp_seconds, video_duration):
        path = extract_frame(video_path, timestamp, output_dir)
        if path not in paths:
            paths.append(path)
    return paths


def context_strength(value: str) -> float:
    """Converte sinais textuais em intensidade conservadora para edição."""
    text = value.strip().lower()
    if text == "incerto":
        return 0.5

    # Negação/ausência deve ser avaliada antes de sinais positivos como "reação".
    weak = ("sem reação", "nenhuma", "fraco", "baixa", "baixo", "calmo")
    if any(word in text for word in weak):
        return 0.25

    strong = ("forte", "alta", "alto", "clímax", "decisivo", "intenso", "reação")
    if any(word in text for word in strong):
        return 1.0
    return 0.65
