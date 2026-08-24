import pytest

from fifa_content_engine.publishing_engine import tiktok_client
from fifa_content_engine.publishing_engine.errors import TikTokUploadError


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict:
        return self._json_data


def test_init_video_post_success(monkeypatch):
    monkeypatch.setattr(
        tiktok_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(
            200, {"data": {"publish_id": "publish123"}, "error": {"code": "ok"}}
        ),
    )

    publish_id = tiktok_client.init_video_post(
        access_token="token",
        video_url="https://x/video.mp4",
        title="Gol de placa",
        privacy_level="PUBLIC_TO_EVERYONE",
    )

    assert publish_id == "publish123"


def test_init_video_post_raises_on_error_code(monkeypatch):
    monkeypatch.setattr(
        tiktok_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(
            200, {"data": {}, "error": {"code": "invalid_param", "message": "bad video_url"}}
        ),
    )

    with pytest.raises(TikTokUploadError):
        tiktok_client.init_video_post(
            access_token="token",
            video_url="bad-url",
            title="x",
            privacy_level="PUBLIC_TO_EVERYONE",
        )


def test_get_post_status_returns_data(monkeypatch):
    monkeypatch.setattr(
        tiktok_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(
            200, {"data": {"status": "PUBLISH_COMPLETE"}, "error": {"code": "ok"}}
        ),
    )

    status_data = tiktok_client.get_post_status(access_token="token", publish_id="publish123")

    assert status_data["status"] == "PUBLISH_COMPLETE"


def test_get_post_status_raises_on_http_error(monkeypatch):
    monkeypatch.setattr(
        tiktok_client.requests,
        "post",
        lambda *a, **kw: FakeResponse(401, {"error": {"code": "access_token_invalid"}}),
    )

    with pytest.raises(TikTokUploadError):
        tiktok_client.get_post_status(access_token="bad-token", publish_id="publish123")
