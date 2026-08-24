"""Interface base para classificadores de frame (contrato do AI Engine)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class FrameClassifier(ABC):
    """Contrato para qualquer classificador de frame do pipeline.

    Implementações devem retornar o texto bruto da resposta do modelo,
    esperado como um JSON válido (ver ai_engine.moments.parse_model_response).
    """

    @abstractmethod
    def classify(self, image_path: Path) -> str:
        """Analisa a imagem e retorna a resposta bruta do modelo (JSON em texto)."""
