"""Exceções específicas do Video Engine."""


class VideoEngineError(Exception):
    """Erro base para qualquer falha no Video Engine."""


class VideoValidationError(VideoEngineError):
    """O arquivo de vídeo não passou na validação (formato, stream, etc.)."""


class VideoConversionError(VideoEngineError):
    """Falha ao converter/normalizar o vídeo com o ffmpeg."""


class SceneDetectionError(VideoEngineError):
    """Falha ao detectar cenas/momentos no vídeo."""
