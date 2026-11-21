"""The brain layer must degrade gracefully: no key means the deterministic planner, not an error."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.provider_router import (BrainUnavailable, ProviderRouter, discover_provider,  # noqa: E402
                                  extract_json)


def test_extract_json_from_fences_and_prose():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Sure! Here is the plan:\n{"title": "Cove", "regions": []}\nHope that helps.') == {
        "title": "Cove", "regions": []}
    assert extract_json('{"nested": {"ok": true}}') == {"nested": {"ok": True}}


def test_extract_json_rejects_non_objects():
    assert extract_json("") is None
    assert extract_json("no json at all") is None
    assert extract_json("[1, 2, 3]") is None
    assert extract_json("{broken: true}") is None


def test_offline_router_is_honest():
    router = ProviderRouter(config=None)
    assert router.available is False
    described = router.describe()
    assert described["available"] is False
    assert described["provider"] is None
    try:
        router.complete([{"role": "user", "content": "hi"}])
    except BrainUnavailable:
        pass
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"offline router raised the wrong error: {type(exc).__name__}")
    else:
        raise AssertionError("offline router must not fabricate a completion")


def test_provider_discovery_reads_the_environment():
    import os
    saved = {k: os.environ.pop(k, None) for k in
             ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "IDEA2WORLD_API_KEY")}
    try:
        assert discover_provider() is None
        os.environ["OPENAI_API_KEY"] = "sk-test"
        config = discover_provider()
        assert config and config.kind == "openai" and config.api_key == "sk-test"
    finally:
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print("ok", name)
