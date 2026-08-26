import pytest

from fifa_content_engine.publishing_engine import tiktok_stats
from fifa_content_engine.publishing_engine.errors import TikTokUploadError


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict:
        return self._json_data


def test_get_video_stats_returns_parsed_counts(monkeypatch):
    monkeypatch.setattr(
        tiktok_stats.requests,
        "post",
        lambda *a, **kw: FakeResponse(
            200,
            {
                "data": {
                    "videos": [
                        {
                            "view_count": 1000,
                            "like_count": 100,
                            "comment_count": 10,
                            "share_count": 5,
                        }
                    ]
                },
                "error": {"code": "ok"},
            },
        ),
    )

    stats = tiktok_stats.get_video_stats(video_id="v1", access_token="token")

    assert stats == {
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 10,
        "share_count": 5,
    }


def test_get_video_stats_raises_when_video_not_found(monkeypatch):
    monkeypatch.setattr(
        tiktok_stats.requests,
        "post",
        lambda *a, **kw: FakeResponse(200, {"data": {"videos": []}, "error": {"code": "ok"}}),
    )

    with pytest.raises(TikTokUploadError):
        tiktok_stats.get_video_stats(video_id="missing", access_token="token")


def test_get_video_stats_raises_on_api_error(monkeypatch):
    monkeypatch.setattr(
        tiktok_stats.requests,
        "post",
        lambda *a, **kw: FakeResponse(401, {"error": {"code": "access_token_invalid"}}),
    )

    with pytest.raises(TikTokUploadError):
        tiktok_stats.get_video_stats(video_id="v1", access_token="bad-token")
