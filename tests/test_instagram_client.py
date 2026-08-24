import pytest

from fifa_content_engine.publishing_engine import instagram_client
from fifa_content_engine.publishing_engine.errors import InstagramUploadError


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict:
        return self._json_data


def test_create_media_container_success(monkeypatch):
    monkeypatch.setattr(
        instagram_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(200, {"id": "container123"}),
    )

    container_id = instagram_client.create_media_container(
        ig_user_id="ig1", access_token="token", video_url="https://x/video.mp4", caption="Legenda"
    )

    assert container_id == "container123"


def test_create_media_container_raises_on_error_response(monkeypatch):
    monkeypatch.setattr(
        instagram_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(400, {"error": {"message": "Invalid video_url"}}),
    )

    with pytest.raises(InstagramUploadError):
        instagram_client.create_media_container(
            ig_user_id="ig1", access_token="token", video_url="bad-url", caption="Legenda"
        )


def test_get_container_status_returns_status_code(monkeypatch):
    monkeypatch.setattr(
        instagram_client.requests,
        "get",
        lambda *a, **kw: FakeResponse(200, {"status_code": "FINISHED"}),
    )

    status = instagram_client.get_container_status(container_id="c1", access_token="token")

    assert status == "FINISHED"


def test_publish_container_success(monkeypatch):
    monkeypatch.setattr(
        instagram_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(200, {"id": "media123"}),
    )

    media_id = instagram_client.publish_container(
        ig_user_id="ig1", access_token="token", container_id="c1"
    )

    assert media_id == "media123"


def test_get_media_permalink_success(monkeypatch):
    monkeypatch.setattr(
        instagram_client.requests,
        "get",
        lambda *a, **kw: FakeResponse(
            200, {"permalink": "https://www.instagram.com/reel/media123/"}
        ),
    )

    permalink = instagram_client.get_media_permalink(media_id="media123", access_token="token")

    assert permalink == "https://www.instagram.com/reel/media123/"
