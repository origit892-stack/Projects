"""Test runner with no dependencies (pytest is optional).

    python3 tests/run_tests.py            # unit + integration
    python3 tests/run_tests.py unit       # unit only
    python3 tests/run_tests.py -k assets  # filter by name

Integration tests execute the generated Luau project in the DataModel simulator, so they need the
`luau` CLI on PATH. Without it those checks are reported as skipped, never as passed.
"""
from __future__ import annotations

import importlib.util
import inspect
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))


def load(path: Path):
    name = f"i2w_{path.parent.name}_{path.stem}".replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def main(argv: list[str]) -> int:
    selection = "all"
    keyword = ""
    rest = [a for a in argv if not a.startswith("-")]
    if rest and rest[0] in ("unit", "integration", "all"):
        selection = rest[0]
    if "-k" in argv:
        keyword = argv[argv.index("-k") + 1]

    folders = []
    if selection in ("all", "unit"):
        folders.append(HERE / "unit")
    if selection in ("all", "integration"):
        folders.append(HERE / "integration")

    have_luau = bool(shutil.which("luau"))
    passed = failed = skipped = 0
    failures: list[tuple[str, str]] = []
    started = time.time()

    for folder in folders:
        for path in sorted(folder.glob("test_*.py")):
            if keyword and keyword not in path.stem:
                continue
            if folder.name == "integration" and not have_luau:
                print(f"SKIP {path.name} (luau CLI not installed)")
                skipped += 1
                continue
            module = load(path)
            tests = [(n, f) for n, f in sorted(vars(module).items())
                     if n.startswith("test_") and callable(f)]
            if not tests:
                continue
            print(f"\n{path.relative_to(ROOT)}")
            for name, fn in tests:
                if keyword and keyword not in name and keyword not in path.stem:
                    continue
                params = inspect.signature(fn).parameters
                kwargs = {}
                if "tmp_path" in params:
                    kwargs["tmp_path"] = Path(tempfile.mkdtemp(prefix="i2w-test-"))
                t0 = time.time()
                try:
                    fn(**kwargs)
                except AssertionError as exc:
                    failed += 1
                    print(f"  FAIL {name} — {exc or 'assertion failed'}")
                    failures.append((f"{path.name}::{name}", str(exc) or "assertion failed"))
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    print(f"  ERROR {name} — {type(exc).__name__}: {exc}")
                    failures.append((f"{path.name}::{name}", traceback.format_exc(limit=6)))
                else:
                    passed += 1
                    print(f"  ok   {name} ({time.time() - t0:.2f}s)")

    elapsed = time.time() - started
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped in {elapsed:.1f}s")
    if failures:
        print("\nfailures:")
        for name, detail in failures:
            print(f"- {name}: {detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
