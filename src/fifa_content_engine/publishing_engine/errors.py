"""Exceções específicas do Publishing Engine."""


class PublishingError(Exception):
    """Erro base para qualquer falha no Publishing Engine."""


class YouTubeAuthError(PublishingError):
    """Falha na autenticação OAuth com a API do YouTube."""


class YouTubeUploadError(PublishingError):
    """Falha ao fazer upload do vídeo para o YouTube."""
