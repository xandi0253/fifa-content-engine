"""Autenticação OAuth 2.0 com a YouTube Data API v3.

O fluxo de autorização (abrir o navegador para o usuário conceder acesso)
só roda quando não existe um token salvo. Depois da primeira vez, o token
é reutilizado (e renovado automaticamente quando expira), então este passo
interativo só acontece uma vez por ambiente.
"""

from __future__ import annotations

from pathlib import Path

from .errors import YouTubeAuthError

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_credentials(client_id: str | None, client_secret: str | None, token_path: Path):
    """Retorna credenciais OAuth válidas, renovando ou solicitando login se preciso.

    Levanta YouTubeAuthError se client_id/client_secret não estiverem
    configurados e não houver um token salvo válido para reutilizar.
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    credentials = None

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token_path.write_text(credentials.to_json())
        return credentials

    if not client_id or not client_secret:
        raise YouTubeAuthError(
            "YOUTUBE_CLIENT_ID/YOUTUBE_CLIENT_SECRET não configurados e "
            "nenhum token válido encontrado. Configure as credenciais no "
            ".env para autorizar o acesso ao YouTube."
        )

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    credentials = flow.run_local_server(port=0)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json())

    return credentials
