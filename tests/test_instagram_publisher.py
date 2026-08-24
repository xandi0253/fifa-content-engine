from pathlib import Path

import pytest

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.content_piece import ContentPiece
from fifa_content_engine.publishing_engine import instagram_client
from fifa_content_engine.publishing_engine.errors import InstagramUploadError
from fifa_content_engine.publishing_engine.instagram_publisher import InstagramPublisher
from fifa_content_engine.publishing_engine.media_hosting import MediaHoster


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


def test_publish_raises_without_credentials():
    publisher = InstagramPublisher(
        media_hoster=FakeMediaHoster(), access_token=None, ig_user_id=None
    )

    with pytest.raises(InstagramUploadError):
        publisher.publish(_content_piece())


def test_publish_success_flow(monkeypatch):
    monkeypatch.setattr(instagram_client, "create_media_container", lambda *a, **kw: "container123")
    monkeypatch.setattr(instagram_client, "get_container_status", lambda *a, **kw: "FINISHED")
    monkeypatch.setattr(instagram_client, "publish_container", lambda *a, **kw: "media123")
    monkeypatch.setattr(
        instagram_client,
        "get_media_permalink",
        lambda *a, **kw: "https://www.instagram.com/reel/media123/",
    )

    publisher = InstagramPublisher(
        media_hoster=FakeMediaHoster(),
        access_token="fake-token",
        ig_user_id="fake-ig-id",
        poll_interval_seconds=0.01,
    )

    url = publisher.publish(_content_piece())

    assert url == "https://www.instagram.com/reel/media123/"


def test_publish_raises_when_container_status_is_error(monkeypatch):
    monkeypatch.setattr(instagram_client, "create_media_container", lambda *a, **kw: "container123")
    monkeypatch.setattr(instagram_client, "get_container_status", lambda *a, **kw: "ERROR")

    publisher = InstagramPublisher(
        media_hoster=FakeMediaHoster(),
        access_token="fake-token",
        ig_user_id="fake-ig-id",
        poll_interval_seconds=0.01,
    )

    with pytest.raises(InstagramUploadError):
        publisher.publish(_content_piece())


def test_publish_raises_on_polling_timeout(monkeypatch):
    monkeypatch.setattr(instagram_client, "create_media_container", lambda *a, **kw: "container123")
    monkeypatch.setattr(instagram_client, "get_container_status", lambda *a, **kw: "IN_PROGRESS")

    publisher = InstagramPublisher(
        media_hoster=FakeMediaHoster(),
        access_token="fake-token",
        ig_user_id="fake-ig-id",
        poll_interval_seconds=0.01,
        poll_timeout_seconds=0.05,
    )

    with pytest.raises(InstagramUploadError):
        publisher.publish(_content_piece())
