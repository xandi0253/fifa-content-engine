"""Exceções específicas do AI Engine."""


class AIAnalysisError(Exception):
    """Erro base para qualquer falha no AI Engine."""


class FrameExtractionError(AIAnalysisError):
    """Falha ao extrair um frame do vídeo com ffmpeg."""


class ModelResponseError(AIAnalysisError):
    """A resposta do modelo de IA não veio no formato esperado."""
