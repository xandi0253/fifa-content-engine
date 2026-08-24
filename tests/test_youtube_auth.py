from pathlib import Path

import pytest

from fifa_content_engine.publishing_engine.errors import YouTubeAuthError
from fifa_content_engine.publishing_engine.youtube_auth import get_credentials


def test_get_credentials_raises_without_client_id_or_secret(tmp_path: Path):
    token_path = tmp_path / "token.json"

    with pytest.raises(YouTubeAuthError):
        get_credentials(client_id=None, client_secret=None, token_path=token_path)


def test_get_credentials_raises_without_client_secret(tmp_path: Path):
    token_path = tmp_path / "token.json"

    with pytest.raises(YouTubeAuthError):
        get_credentials(client_id="fake-id", client_secret=None, token_path=token_path)
