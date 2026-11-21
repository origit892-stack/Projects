"""Code generation: the emitted Lua must be literal-correct and the project must parse."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from assets.asset_registry import build_manifest  # noqa: E402
from codegen import lua_emit, luau_generator, luau_validator  # noqa: E402
from tests.unit.test_assets import make_spec  # noqa: E402


def test_strings_are_escaped():
    out = lua_emit.string('he said "hi"\nback\\slash\ttab')
    assert out.startswith('"') and out.endswith('"')
    assert '\\n' in out and '\\"' in out and '\\\\' in out
    assert "\n" not in out


def test_literals():
    assert lua_emit.value(True) == "true"
    assert lua_emit.value(False) == "false"
    assert lua_emit.value(None) == "nil"
    assert lua_emit.value(3) == "3"
    assert lua_emit.value(1.5) == "1.5"
    assert lua_emit.value([1, 2]) == "{1, 2}"
    assert "a = 1" in lua_emit.value({"a": 1})
    assert "on = true" in lua_emit.value({"on": True})
    assert '["not-an-id"]' in lua_emit.value({"not-an-id": 2})


def test_project_contains_every_module():
    spec = make_spec()
    build_manifest(spec)
    sources = luau_generator.project_sources(spec)
    for name in luau_validator.REQUIRED_MODULES:
        assert f"{name}.lua" in sources, name
        assert "return " in sources[f"{name}.lua"], f"{name} must return its module"
    assert "MapBootstrap.server.lua" in sources
    bundle = luau_generator.command_bar_bundle(sources)
    assert "MapBootstrap" in bundle and len(bundle) > sum(len(v) for v in sources.values())
    total = sum(len(v) for v in sources.values())
    assert total > 40_000, total


def test_config_carries_the_world_data():
    spec = make_spec()
    build_manifest(spec)
    config = luau_generator.project_sources(spec)["MapConfig.lua"]
    assert str(spec.world["size"]) in config
    assert str(spec.world["seed"]) in config
    for region in spec.regions:
        assert region["id"] in config
    assert "asset_" in config


def test_generated_project_validates():
    spec = make_spec()
    build_manifest(spec)
    report = luau_validator.validate_sources(luau_generator.project_sources(spec))
    assert report["passed"], report["issues"][:4]
    critical = [i for i in report["issues"] if i["severity"] == "critical"]
    assert not critical
    assert report["tools"].get("syntax") in ("luau-compile", "unavailable")


def test_structure_check_catches_a_missing_module():
    report = luau_validator.validate_sources({"MapConfig.lua": "return {}"}, deep=False)
    assert not report["passed"]
    assert any(i["severity"] == "critical" for i in report["issues"])


if __name__ == "__main__":
    for name, fn in sorted(list(globals().items())):
        if name.startswith("test_"):
            fn()
            print("ok", name)
