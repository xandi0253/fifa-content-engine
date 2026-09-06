"""Classificador de frames usando a API de visão da OpenAI (GPT-4o)."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from .classifier import FrameClassifier
from .errors import ModelResponseError
from .moments import MOMENT_TYPES

DEFAULT_MODEL = "gpt-4o"

_MOMENT_TYPES_LIST = ", ".join(f'"{t}"' for t in sorted(MOMENT_TYPES))


def build_system_prompt(game_context: str | None = None) -> str:
    """Monta o prompt do sistema, opcionalmente mencionando o jogo específico.

    Sem game_context, o prompt é genérico e funciona para qualquer gênero
    de jogo (esportes, FPS, corrida, etc.).
    """
    if game_context:
        game_phrase = f" de uma gravação de {game_context}"
    else:
        game_phrase = " de uma gravação de gameplay"

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
    """Implementação de FrameClassifier usando o modelo de visão da OpenAI."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        game_context: str | None = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.system_prompt = build_system_prompt(game_context) if game_context else SYSTEM_PROMPT
        self._client = None

    @property
    def client(self):
        """Cria o cliente da OpenAI de forma preguiçosa (lazy).

        Evita a dependência ser importada/instanciada em ambientes que
        usam apenas um FrameClassifier mockado (ex: testes).
        """
        if self._client is None:
            if not self.api_key:
                raise ModelResponseError(
                    "OPENAI_API_KEY não configurada. Defina a variável de "
                    "ambiente ou passe api_key explicitamente."
                )
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def classify(self, image_path: Path) -> str:
        image_base64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                },
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise ModelResponseError("Resposta vazia do modelo da OpenAI")

        return content
