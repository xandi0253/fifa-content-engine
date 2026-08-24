"""Publica clipes no YouTube usando a YouTube Data API v3."""

from __future__ import annotations

import os
from pathlib import Path

from fifa_content_engine.content_engine.content_piece import ContentPiece

from .errors import YouTubeUploadError
from .publisher import VideoPublisher
from .video_metadata import DEFAULT_PRIVACY_STATUS, build_video_metadata
from .youtube_auth import get_credentials

DEFAULT_TOKEN_PATH = Path(".youtube_token.json")


class YouTubePublisher(VideoPublisher):
    """Implementação de VideoPublisher usando a YouTube Data API v3.

    As credenciais e o cliente da API são construídos de forma preguiçosa
    (lazy) — só na primeira chamada de publish() — para que o restante do
    pipeline (e os testes que usam um publisher falso) não precise ter as
    dependências do Google configuradas.
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_path: Path = DEFAULT_TOKEN_PATH,
        privacy_status: str = DEFAULT_PRIVACY_STATUS,
    ):
        self.client_id = client_id or os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("YOUTUBE_CLIENT_SECRET")
        self.token_path = token_path
        self.privacy_status = privacy_status
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from googleapiclient.discovery import build

            credentials = get_credentials(self.client_id, self.client_secret, self.token_path)
            self._client = build("youtube", "v3", credentials=credentials)
        return self._client

    def publish(self, content_piece: ContentPiece) -> str:
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaFileUpload

        metadata = build_video_metadata(content_piece, privacy_status=self.privacy_status)
        media = MediaFileUpload(str(content_piece.clip_path), chunksize=-1, resumable=True)

        try:
            request = self.client.videos().insert(
                part="snippet,status", body=metadata, media_body=media
            )
            response = request.execute()
        except HttpError as exc:
            raise YouTubeUploadError(
                f"Falha ao publicar {content_piece.clip_path} no YouTube: {exc}"
            ) from exc

        video_id = response.get("id")
        if not video_id:
            raise YouTubeUploadError(f"YouTube retornou resposta sem id de vídeo: {response}")

        return f"https://www.youtube.com/watch?v={video_id}"
