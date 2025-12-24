import asyncio


def test_get_settings_reads_env_and_caches(monkeypatch):
    from app.core import config

    # Ensure fresh cache and provide env var
    config.get_settings.cache_clear()
    monkeypatch.setenv("CURRENCY_API_KEY", "test-key")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")

    s1 = config.get_settings()
    assert s1.currency_api_key == "test-key"
    assert s1.gcp_project_id == "test-project"

    # Cached instance should be identical
    s2 = config.get_settings()
    assert s1 is s2
