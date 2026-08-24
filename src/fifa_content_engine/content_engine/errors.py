"""Exceções específicas do Content Engine."""


class ContentGenerationError(Exception):
    """Erro base para qualquer falha no Content Engine."""


class ClipExtractionError(ContentGenerationError):
    """Falha ao cortar o clipe de vídeo com ffmpeg."""
