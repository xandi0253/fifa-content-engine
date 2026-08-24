"""Publica clipes no Instagram (Reels) usando a Instagram Graph API."""

from __future__ import annotations

import os
import time

from fifa_content_engine.content_engine.content_piece import ContentPiece

from . import instagram_client as client
from .errors import InstagramUploadError
from .media_hosting import MediaHoster
from .publisher import VideoPublisher

CONTAINER_STATUS_FINISHED = "FINISHED"
CONTAINER_STATUS_ERROR = "ERROR"

DEFAULT_POLL_INTERVAL_SECONDS = 5.0
DEFAULT_POLL_TIMEOUT_SECONDS = 120.0


class InstagramPublisher(VideoPublisher):
    """Implementação de VideoPublisher usando a Instagram Graph API.

    Requer um MediaHoster para expor o clipe local em uma URL pública
    antes de publicar — a API do Instagram busca o vídeo pela URL, não
    aceita upload direto de arquivo.
    """

    def __init__(
        self,
        media_hoster: MediaHoster,
        access_token: str | None = None,
        ig_user_id: str | None = None,
        poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
        poll_timeout_seconds: float = DEFAULT_POLL_TIMEOUT_SECONDS,
    ):
        self.media_hoster = media_hoster
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_user_id = ig_user_id or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        self.poll_interval_seconds = poll_interval_seconds
        self.poll_timeout_seconds = poll_timeout_seconds

    def publish(self, content_piece: ContentPiece) -> str:
        if not self.access_token or not self.ig_user_id:
            raise InstagramUploadError(
                "INSTAGRAM_ACCESS_TOKEN/INSTAGRAM_BUSINESS_ACCOUNT_ID não configurados."
            )

        video_url = self.media_hoster.host(content_piece.clip_path)

        container_id = client.create_media_container(
            self.ig_user_id, self.access_token, video_url, content_piece.caption
        )

        self._wait_until_ready(container_id)

        media_id = client.publish_container(self.ig_user_id, self.access_token, container_id)

        return client.get_media_permalink(media_id, self.access_token)

    def _wait_until_ready(self, container_id: str) -> None:
        elapsed_seconds = 0.0

        while elapsed_seconds < self.poll_timeout_seconds:
            status = client.get_container_status(container_id, self.access_token)

            if status == CONTAINER_STATUS_FINISHED:
                return
            if status == CONTAINER_STATUS_ERROR:
                raise InstagramUploadError(
                    f"Processamento do contêiner {container_id} falhou no Instagram"
                )

            time.sleep(self.poll_interval_seconds)
            elapsed_seconds += self.poll_interval_seconds

        raise InstagramUploadError(
            f"Timeout aguardando processamento do contêiner {container_id} no Instagram"
        )
