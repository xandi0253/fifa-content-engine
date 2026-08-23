"""Minimal command-line entry point for the foundation."""

from .config import get_settings


def main() -> None:
    settings = get_settings()
    print(f"{settings.app_name} | ambiente={settings.app_env}")


if __name__ == "__main__":
    main()
