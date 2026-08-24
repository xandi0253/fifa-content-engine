"""Exceções específicas do Publishing Engine."""


class PublishingError(Exception):
    """Erro base para qualquer falha no Publishing Engine."""


class YouTubeAuthError(PublishingError):
    """Falha na autenticação OAuth com a API do YouTube."""


class YouTubeUploadError(PublishingError):
    """Falha ao fazer upload do vídeo para o YouTube."""


class MediaHostingError(PublishingError):
    """Falha ao hospedar o clipe em uma URL pública."""


class InstagramUploadError(PublishingError):
    """Falha ao publicar o clipe no Instagram (container ou publicação)."""
