"""Script de teste: valida se a autenticação OAuth com o YouTube funciona.

Não publica nada — só confirma que as credenciais estão certas e que o
token é gerado com sucesso. Rode isto na raiz do projeto fifa-content-engine,
com o ambiente virtual ativado.
"""

import os
from pathlib import Path


def load_env_file(path: Path) -> None:
    """Lê um arquivo .env simples e coloca as variáveis no ambiente do processo."""
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

client_id = os.getenv("YOUTUBE_CLIENT_ID")
client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
token_path = Path(".youtube_token.json")

print("Client ID configurado:", "sim" if client_id else "NÃO - verifique o .env")
print("Client Secret configurado:", "sim" if client_secret else "NÃO - verifique o .env")

if not client_id or not client_secret:
    print("\nPare aqui e confira o arquivo .env antes de continuar.")
else:
    print("\nAbrindo o navegador para autorização (se for a primeira vez)...")
    credentials = get_credentials(client_id, client_secret, token_path)
    print("\n✅ Autenticação bem-sucedida!")
    print(f"Token salvo em: {token_path.absolute()}")
