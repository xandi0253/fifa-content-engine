"""Classificador de frames usando a API de visão da OpenAI (GPT-4o)."""

from __future__ import annotations

import base64
import os
from pathlib import Path

from .classifier import FrameClassifier
from .errors import ModelResponseError

DEFAULT_MODEL = "gpt-4o"

SYSTEM_PROMPT = (
    "Você analisa um frame de vídeo de uma partida de futebol (jogo do "
    "FIFA 26) e identifica se ele representa um momento relevante para "
    "gerar conteúdo de highlights (gol, falta, comemoração, lance de "
    "perigo, defesa importante). Responda SOMENTE com um objeto JSON, "
    "sem nenhum texto adicional, com exatamente estas chaves:\n"
    '- "is_relevant": true ou false\n'
    '- "moment_type": um de "gol", "falta", "comemoracao", "lance_perigoso", '
    '"defesa", "outro"\n'
    '- "score": número entre 0 e 1 indicando a relevância do momento\n'
    '- "title": título curto (até 8 palavras) para o momento\n'
    '- "description": descrição de 1 a 2 frases sobre o que acontece na cena'
)


class OpenAIFrameClassifier(FrameClassifier):
    """Implementação de FrameClassifier usando o modelo de visão da OpenAI."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
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
                {"role": "system", "content": SYSTEM_PROMPT},
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
