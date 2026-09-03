"""Script utilitário: muda a visibilidade de um vídeo já publicado no YouTube.

Uso:
    python set_video_public.py VIDEO_ID [--privacy public|unlisted|private]

Exemplo:
    python set_video_public.py HfJ90tUcpgk --privacy public
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_env_file(Path(".env"))

from fifa_content_engine.publishing_engine.youtube_auth import get_credentials  # noqa: E402

parser = argparse.ArgumentParser(description="Muda a visibilidade de um vídeo do YouTube.")
parser.add_argument("video_id", help="O ID do vídeo (a parte depois de watch?v= na URL)")
parser.add_argument(
    "--privacy",
    default="public",
    choices=["public", "unlisted", "private"],
    help="Nova visibilidade (padrão: public)",
)
args = parser.parse_args()

client_id = os.getenv("YOUTUBE_CLIENT_ID")
client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
token_path = Path(".youtube_token.json")

from googleapiclient.discovery import build  # noqa: E402

credentials = get_credentials(client_id, client_secret, token_path)
client = build("youtube", "v3", credentials=credentials)

print(f"Alterando vídeo {args.video_id} para '{args.privacy}'...")

response = (
    client.videos()
    .update(
        part="status",
        body={"id": args.video_id, "status": {"privacyStatus": args.privacy}},
    )
    .execute()
)

new_status = response["status"]["privacyStatus"]
print(f"\n✅ Feito! Nova visibilidade: {new_status}")
print(f"URL: https://www.youtube.com/watch?v={args.video_id}")
