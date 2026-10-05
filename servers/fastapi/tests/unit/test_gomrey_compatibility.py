from types import SimpleNamespace

from utils.get_env import (
    get_fastembed_icon_cache_directory_env,
    get_gomrey_public_url,
    get_presenton_public_url,
    is_community_enabled,
    is_gomrey_electron_desktop,
    is_presenton_electron_desktop,
)
from utils.mcp_public_urls import (
    LEGACY_MCP_REQUEST_HEADER,
    MCP_REQUEST_HEADER,
    is_mcp_request,
)


def _request(headers: dict[str, str]):
    return SimpleNamespace(headers=headers, url=SimpleNamespace(scheme="http", netloc="localhost"))


def test_public_url_canonical_precedence_including_explicit_empty(monkeypatch):
    monkeypatch.setenv("PRESENTON_PUBLIC_URL", "https://legacy.example/")
    monkeypatch.setenv("GOMREY_PUBLIC_URL", "")
    assert get_gomrey_public_url() is None
    assert get_presenton_public_url() is None
    monkeypatch.setenv("GOMREY_PUBLIC_URL", "https://gomrey.example/root/")
    assert get_gomrey_public_url() == "https://gomrey.example/root"


def test_public_url_legacy_fallback(monkeypatch):
    monkeypatch.delenv("GOMREY_PUBLIC_URL", raising=False)
    monkeypatch.setenv("PRESENTON_PUBLIC_URL", "https://legacy.example/")
    assert get_gomrey_public_url() == "https://legacy.example"


def test_community_and_electron_canonical_precedence(monkeypatch):
    monkeypatch.setenv("PRESENTON_COMMUNITY_ENABLED", "false")
    monkeypatch.setenv("GOMREY_COMMUNITY_ENABLED", "")
    assert is_community_enabled()
    monkeypatch.setenv("PRESENTON_ELECTRON", "true")
    monkeypatch.setenv("GOMREY_ELECTRON", "")
    assert not is_gomrey_electron_desktop()
    assert not is_presenton_electron_desktop()


def test_fastembed_cache_canonical_precedence(monkeypatch):
    monkeypatch.setenv("PRESENTON_FASTEMBED_ICON_CACHE_DIR", "/legacy")
    monkeypatch.setenv("GOMREY_FASTEMBED_ICON_CACHE_DIR", "")
    assert get_fastembed_icon_cache_directory_env() == ""
    monkeypatch.setenv("GOMREY_FASTEMBED_ICON_CACHE_DIR", "/gomrey")
    assert get_fastembed_icon_cache_directory_env() == "/gomrey"


def test_mcp_header_canonical_precedence_and_legacy_fallback():
    assert MCP_REQUEST_HEADER == "X-Gomrey-MCP-Request"
    assert LEGACY_MCP_REQUEST_HEADER == "X-Presenton-MCP-Request"
    assert not is_mcp_request(_request({MCP_REQUEST_HEADER: "0", LEGACY_MCP_REQUEST_HEADER: "1"}))
    assert is_mcp_request(_request({MCP_REQUEST_HEADER: "1"}))
    assert is_mcp_request(_request({LEGACY_MCP_REQUEST_HEADER: "1"}))
