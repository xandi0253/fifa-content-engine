"""Orquestra a análise de momentos: extrai frames, classifica e retorna resultados."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path

from .classifier import FrameClassifier
from .frame_extraction import extract_frame
from .moments import Moment, parse_model_response


class MomentAnalyzer(ABC):
    """Contrato para qualquer analisador de momentos do pipeline."""

    @abstractmethod
    def analyze(self, video_path: Path, timestamps: Sequence[float]) -> list[Moment]:
        """Analisa os timestamps candidatos e retorna os momentos classificados."""


class AIMomentAnalyzer(MomentAnalyzer):
    """Analisador que extrai um frame por timestamp e usa um FrameClassifier
    (ex: OpenAIFrameClassifier) para classificar cada um.
    """

    def __init__(self, classifier: FrameClassifier, frame_output_dir: Path):
        self.classifier = classifier
        self.frame_output_dir = frame_output_dir

    def analyze(self, video_path: Path, timestamps: Sequence[float]) -> list[Moment]:
        moments: list[Moment] = []

        for timestamp in timestamps:
            frame_path = extract_frame(video_path, timestamp, self.frame_output_dir)
            raw_response = self.classifier.classify(frame_path)
            moment = parse_model_response(raw_response, timestamp)
            moments.append(moment)

        return moments

    def analyze_relevant_only(self, video_path: Path, timestamps: Sequence[float]) -> list[Moment]:
        """Atalho para obter apenas os momentos marcados como relevantes."""
        return [m for m in self.analyze(video_path, timestamps) if m.is_relevant]
