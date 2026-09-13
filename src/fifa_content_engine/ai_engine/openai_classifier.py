"""Classificador de frames usando a visão da OpenAI."""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path

from .classifier import FrameClassifier
from .errors import ModelResponseError
from .moments import MOMENT_TYPES

DEFAULT_MODEL = "gpt-4o"
DEFAULT_FALLBACK_MODEL = "gpt-5.6-luna"
DEFAULT_MAX_RETRIES = 1

_MOMENT_TYPES_LIST = ", ".join(f'"{t}"' for t in sorted(MOMENT_TYPES))


def build_system_prompt(game_context: str | None = None) -> str:
    """Monta o prompt do sistema, opcionalmente mencionando o jogo específico."""
    game_phrase = f" de uma gravação de {game_context}" if game_context else " de uma gravação de gameplay"
    return (
        f"Você analisa um frame de vídeo{game_phrase} e identifica se ele "
        "representa um momento relevante para gerar conteúdo de highlights "
        "(uma vitória/pontuação, um momento de tensão, uma comemoração, uma "
        "falha dramática, ou uma sequência de ação notável). Responda SOMENTE "
        "com um objeto JSON, sem nenhum texto adicional, com exatamente estas "
        "chaves:\n"
        '- "is_relevant": true ou false\n'
        f'- "moment_type": um de {_MOMENT_TYPES_LIST}\n'
        '- "score": número entre 0 e 1 indicando a relevância do momento\n'
        '- "title": título curto (até 8 palavras) para o momento\n'
        '- "description": descrição de 1 a 2 frases sobre o que acontece na cena'
    )


SYSTEM_PROMPT = build_system_prompt()


class OpenAIFrameClassifier(FrameClassifier):
    """Classifica frames usando OpenAI, com fallback moderno e controlado.

    O caminho existente via Chat Completions é preservado. Se ele falhar ou
    devolver conteúdo vazio, o classificador pode tentar a Responses API com
    saída JSON estruturada. Isso evita deixar o pipeline preso a uma única
    forma de chamada do provedor.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        game_context: str | None = None,
        max_retries: int | None = None,
        fallback_enabled: bool | None = None,
        fallback_model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.fallback_model = fallback_model or os.getenv("OPENAI_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
        self.max_retries = (
            max(0, max_retries)
            if max_retries is not None
            else max(0, int(os.getenv("OPENAI_MAX_RETRIES", DEFAULT_MAX_RETRIES)))
        )
        self.fallback_enabled = (
            fallback_enabled
            if fallback_enabled is not None
            else os.getenv("OPENAI_FALLBACK_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
        )
        self.system_prompt = build_system_prompt(game_context) if game_context else SYSTEM_PROMPT
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.api_key:
                raise ModelResponseError(
                    "OPENAI_API_KEY não configurada. Defina a variável de ambiente "
                    "ou passe api_key explicitamente."
                )
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _request_chat(self, image_base64: str):
        return self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": [{
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                }]},
            ],
        )

    def _request_responses(self, image_base64: str):
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "is_relevant": {"type": "boolean"},
                "moment_type": {"type": "string", "enum": sorted(MOMENT_TYPES)},
                "score": {"type": "number", "minimum": 0, "maximum": 1},
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["is_relevant", "moment_type", "score", "title", "description"],
        }
        responses = getattr(self.client, "responses", None)
        if responses is None:
            raise RuntimeError("SDK da OpenAI não disponibiliza a Responses API neste ambiente")
        response = responses.create(
            model=self.fallback_model,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": self.system_prompt},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_base64}"},
                ],
            }],
            text={"format": {"type": "json_schema", "name": "moment", "strict": True, "schema": schema}},
        )
        content = getattr(response, "output_text", None)
        if not content:
            raise RuntimeError("Responses API também retornou conteúdo vazio")
        return content

    def classify(self, image_path: Path) -> str:
        image_base64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        attempts = self.max_retries + 1
        last_diagnostic = "motivo desconhecido"

        for attempt in range(1, attempts + 1):
            try:
                response = self._request_chat(image_base64)
                choices = getattr(response, "choices", None) or []
                if not choices:
                    last_diagnostic = "a resposta não contém choices"
                else:
                    choice = choices[0]
                    message = getattr(choice, "message", None)
                    content = getattr(message, "content", None) if message else None
                    if content:
                        return content
                    refusal = getattr(message, "refusal", None) if message else None
                    finish_reason = getattr(choice, "finish_reason", None)
                    last_diagnostic = f"content vazio; finish_reason={finish_reason!r}" + (
                        f"; refusal={refusal!r}" if refusal else ""
                    )
            except Exception as exc:  # noqa: BLE001 -- converte erro do provedor em diagnóstico de domínio
                last_diagnostic = f"{type(exc).__name__}: {exc}"

            if attempt < attempts:
                time.sleep(0.5)

        if self.fallback_enabled:
            try:
                return self._request_responses(image_base64)
            except Exception as exc:  # noqa: BLE001 -- fallback não pode esconder o erro primário
                last_diagnostic += f"; fallback Responses API: {type(exc).__name__}: {exc}"

        raise ModelResponseError(
            f"A OpenAI não retornou conteúdo utilizável (modelo {self.model}): {last_diagnostic}."
        )
