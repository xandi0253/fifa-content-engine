from fifa_content_engine.config import get_settings


def test_settings_load_defaults():
    settings = get_settings()
    assert settings.app_name == "FIFA Content Engine"
    assert settings.environment in {"development", "test", "production"}


def test_package_imports():
    import fifa_content_engine

    assert fifa_content_engine.__name__ == "fifa_content_engine"
