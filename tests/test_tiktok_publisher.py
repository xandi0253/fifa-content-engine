from pathlib import Path

import pytest

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.content_piece import ContentPiece
from fifa_content_engine.publishing_engine import tiktok_client
from fifa_content_engine.publishing_engine.errors import TikTokUploadError
from fifa_content_engine.publishing_engine.media_hosting import MediaHoster
from fifa_content_engine.publishing_engine.tiktok_publisher import TikTokPublisher


class FakeMediaHoster(MediaHoster):
    def host(self, clip_path: Path) -> str:
        return f"https://fake-cdn.example.com/{clip_path.name}"


def _content_piece() -> ContentPiece:
    moment = Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type="gol",
        score=0.9,
        title="Gol de placa",
        description="Descrição de teste.",
    )
    return ContentPiece(moment=moment, clip_path=Path("/tmp/clip.mp4"), caption="Legenda")


def test_publish_raises_without_access_token():
    publisher = TikTokPublisher(media_hoster=FakeMediaHoster(), access_token=None)

    with pytest.raises(TikTokUploadError):
        publisher.publish(_content_piece())


def test_publish_success_flow(monkeypatch):
    monkeypatch.setattr(tiktok_client, "init_video_post", lambda *a, **kw: "publish123")
    monkeypatch.setattr(
        tiktok_client, "get_post_status", lambda *a, **kw: {"status": "PUBLISH_COMPLETE"}
    )

    publisher = TikTokPublisher(
        media_hoster=FakeMediaHoster(), access_token="fake-token", poll_interval_seconds=0.01
    )

    result = publisher.publish(_content_piece())

    assert result == "tiktok:publish_id=publish123"


def test_publish_raises_when_status_is_failed(monkeypatch):
    monkeypatch.setattr(tiktok_client, "init_video_post", lambda *a, **kw: "publish123")
    monkeypatch.setattr(
        tiktok_client,
        "get_post_status",
        lambda *a, **kw: {"status": "FAILED", "fail_reason": "video_pull_failed"},
    )

    publisher = TikTokPublisher(
        media_hoster=FakeMediaHoster(), access_token="fake-token", poll_interval_seconds=0.01
    )

    with pytest.raises(TikTokUploadError):
        publisher.publish(_content_piece())


def test_publish_raises_on_polling_timeout(monkeypatch):
    monkeypatch.setattr(tiktok_client, "init_video_post", lambda *a, **kw: "publish123")
    monkeypatch.setattr(
        tiktok_client, "get_post_status", lambda *a, **kw: {"status": "PROCESSING_DOWNLOAD"}
    )

    publisher = TikTokPublisher(
        media_hoster=FakeMediaHoster(),
        access_token="fake-token",
        poll_interval_seconds=0.01,
        poll_timeout_seconds=0.05,
    )

    with pytest.raises(TikTokUploadError):
        publisher.publish(_content_piece())
