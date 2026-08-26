import pytest

from fifa_content_engine.publishing_engine import instagram_stats
from fifa_content_engine.publishing_engine.errors import InstagramUploadError


class FakeResponse:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> dict:
        return self._json_data


def test_get_media_insights_returns_parsed_counts(monkeypatch):
    monkeypatch.setattr(
        instagram_stats.requests,
        "get",
        lambda *a, **kw: FakeResponse(200, {"like_count": 42, "comments_count": 7}),
    )

    stats = instagram_stats.get_media_insights(media_id="media123", access_token="token")

    assert stats == {"like_count": 42, "comment_count": 7}


def test_get_media_insights_raises_on_error_response(monkeypatch):
    monkeypatch.setattr(
        instagram_stats.requests,
        "get",
        lambda *a, **kw: FakeResponse(400, {"error": {"message": "Invalid media_id"}}),
    )

    with pytest.raises(InstagramUploadError):
        instagram_stats.get_media_insights(media_id="bad", access_token="token")
