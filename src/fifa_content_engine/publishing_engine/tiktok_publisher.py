"""Publica clipes no TikTok usando a Content Posting API (Direct Post).

Nota sobre o valor de retorno: diferente do YouTube e do Instagram, a
TikTok Content Posting API não retorna uma URL pública do post no fluxo
de status. O que ela garante é o publish_id, usado para rastrear a
publicação. Por isso publish() retorna uma referência no formato
"tiktok:publish_id=<id>" em vez de uma URL de fato — documentado aqui
para não gerar expectativa equivocada sobre o retorno.
"""

from __future__ import annotations

import os
import time

from fifa_content_engine.content_engine.content_piece import ContentPiece

from . import tiktok_client as client
from .errors import TikTokUploadError
from .media_hosting import MediaHoster
from .publisher import VideoPublisher

STATUS_COMPLETE = "PUBLISH_COMPLETE"
STATUS_FAILED = "FAILED"

DEFAULT_PRIVACY_LEVEL = "PUBLIC_TO_EVERYONE"
DEFAULT_POLL_INTERVAL_SECONDS = 5.0
DEFAULT_POLL_TIMEOUT_SECONDS = 120.0


class TikTokPublisher(VideoPublisher):
    """Implementação de VideoPublisher usando a TikTok Content Posting API.

    Requer um MediaHoster para expor o clipe local em uma URL pública
    (fonte PULL_FROM_URL) — mesmo contrato usado pelo InstagramPublisher.
    """

    def __init__(
        self,
        media_hoster: MediaHoster,
        access_token: str | None = None,
        privacy_level: str = DEFAULT_PRIVACY_LEVEL,
        poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
        poll_timeout_seconds: float = DEFAULT_POLL_TIMEOUT_SECONDS,
    ):
        self.media_hoster = media_hoster
        self.access_token = access_token or os.getenv("TIKTOK_ACCESS_TOKEN")
        self.privacy_level = privacy_level
        self.poll_interval_seconds = poll_interval_seconds
        self.poll_timeout_seconds = poll_timeout_seconds

    def publish(self, content_piece: ContentPiece) -> str:
        if not self.access_token:
            raise TikTokUploadError("TIKTOK_ACCESS_TOKEN não configurado.")

        video_url = self.media_hoster.host(content_piece.clip_path)

        publish_id = client.init_video_post(
            self.access_token,
            video_url,
            title=content_piece.moment.title,
            privacy_level=self.privacy_level,
        )

        self._wait_until_ready(publish_id)

        return f"tiktok:publish_id={publish_id}"

    def _wait_until_ready(self, publish_id: str) -> None:
        elapsed_seconds = 0.0

        while elapsed_seconds < self.poll_timeout_seconds:
            status_data = client.get_post_status(self.access_token, publish_id)
            status = status_data.get("status")

            if status == STATUS_COMPLETE:
                return
            if status == STATUS_FAILED:
                fail_reason = status_data.get("fail_reason", "motivo não informado")
                raise TikTokUploadError(f"Publicação {publish_id} falhou no TikTok: {fail_reason}")

            time.sleep(self.poll_interval_seconds)
            elapsed_seconds += self.poll_interval_seconds

        raise TikTokUploadError(
            f"Timeout aguardando processamento da publicação {publish_id} no TikTok"
        )
