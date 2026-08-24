from pathlib import Path

from fifa_content_engine.ai_engine.moments import Moment
from fifa_content_engine.content_engine.content_piece import ContentPiece
from fifa_content_engine.publishing_engine.errors import YouTubeUploadError
from fifa_content_engine.publishing_engine.publisher import VideoPublisher
from fifa_content_engine.publishing_engine.queue import PublishingQueue


class FakePublisher(VideoPublisher):
    """Publicador falso para testes: nunca chama a API do YouTube de verdade."""

    def __init__(self, should_fail_on: set[int] | None = None):
        self.should_fail_on = should_fail_on or set()
        self.calls = 0

    def publish(self, content_piece: ContentPiece) -> str:
        index = self.calls
        self.calls += 1
        if index in self.should_fail_on:
            raise YouTubeUploadError(f"Falha simulada no item {index}")
        return f"https://www.youtube.com/watch?v=fake{index}"


def _content_piece(title: str) -> ContentPiece:
    moment = Moment(
        timestamp_seconds=10.0,
        is_relevant=True,
        moment_type="gol",
        score=0.9,
        title=title,
        description="Descrição de teste.",
    )
    return ContentPiece(moment=moment, clip_path=Path("/tmp/clip.mp4"), caption="Legenda")


def test_publish_all_returns_success_result_for_each_piece():
    publisher = FakePublisher()
    queue = PublishingQueue(publisher=publisher)
    pieces = [_content_piece("Gol 1"), _content_piece("Gol 2")]

    results = queue.publish_all(pieces)

    assert len(results) == 2
    assert all(r.success for r in results)
    assert results[0].url == "https://www.youtube.com/watch?v=fake0"


def test_publish_all_isolates_failure_without_stopping_batch():
    publisher = FakePublisher(should_fail_on={1})
    queue = PublishingQueue(publisher=publisher)
    pieces = [_content_piece("Gol 1"), _content_piece("Gol 2"), _content_piece("Gol 3")]

    results = queue.publish_all(pieces)

    assert len(results) == 3
    assert results[0].success is True
    assert results[1].success is False
    assert results[1].error_message is not None
    assert results[2].success is True
    # Confirma que o publisher tentou publicar TODOS os itens, mesmo após a falha.
    assert publisher.calls == 3


def test_publish_all_with_empty_list_returns_empty():
    publisher = FakePublisher()
    queue = PublishingQueue(publisher=publisher)

    results = queue.publish_all([])

    assert results == []
