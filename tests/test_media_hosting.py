import pytest

from fifa_content_engine.publishing_engine.media_hosting import MediaHoster


def test_media_hoster_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        MediaHoster()


def test_concrete_subclass_can_be_instantiated_and_used(tmp_path):
    class ConcreteHoster(MediaHoster):
        def host(self, clip_path):
            return f"https://example.com/{clip_path.name}"

    hoster = ConcreteHoster()
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake video bytes")

    url = hoster.host(clip_path)

    assert url == "https://example.com/clip.mp4"
