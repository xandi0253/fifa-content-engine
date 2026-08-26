import pytest

from fifa_content_engine.publishing_engine.errors import YouTubeUploadError
from fifa_content_engine.publishing_engine.youtube_stats import (
    extract_video_id,
    get_video_statistics,
)


def test_extract_video_id_from_watch_url():
    assert extract_video_id("https://www.youtube.com/watch?v=abc123") == "abc123"


def test_extract_video_id_from_short_url():
    assert extract_video_id("https://youtu.be/abc123") == "abc123"


def test_extract_video_id_returns_none_for_unrelated_url():
    assert extract_video_id("https://example.com/video") is None


class FakeYouTubeClient:
    def __init__(self, statistics: dict):
        self._statistics = statistics

    def videos(self):
        return self

    def list(self, part, id):
        return self

    def execute(self):
        if not self._statistics:
            return {"items": []}
        return {"items": [{"statistics": self._statistics}]}


def test_get_video_statistics_returns_parsed_counts(monkeypatch):
    from fifa_content_engine.publishing_engine import youtube_stats

    monkeypatch.setattr(youtube_stats, "get_credentials", lambda *a, **kw: object())

    fake_client = FakeYouTubeClient({"viewCount": "150", "likeCount": "20", "commentCount": "5"})

    import googleapiclient.discovery

    monkeypatch.setattr(googleapiclient.discovery, "build", lambda *a, **kw: fake_client)

    stats = get_video_statistics(
        video_id="abc123", client_id="id", client_secret="secret", token_path=None
    )

    assert stats == {"view_count": 150, "like_count": 20, "comment_count": 5}


def test_get_video_statistics_raises_when_video_not_found(monkeypatch):
    from fifa_content_engine.publishing_engine import youtube_stats

    monkeypatch.setattr(youtube_stats, "get_credentials", lambda *a, **kw: object())

    fake_client = FakeYouTubeClient({})
    import googleapiclient.discovery

    monkeypatch.setattr(googleapiclient.discovery, "build", lambda *a, **kw: fake_client)

    with pytest.raises(YouTubeUploadError):
        get_video_statistics(
            video_id="missing", client_id="id", client_secret="secret", token_path=None
        )
