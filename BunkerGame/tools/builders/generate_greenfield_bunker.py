#!/usr/bin/env python3
"""Generate the source-controlled greenfield bunker staging or active model.

This builder intentionally does not import the legacy ``new_bunker`` package.
Use staging mode for isolated Studio review. Active mode is reserved for the
atomic source cutover after required review gates pass.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from greenfield_bunker.facility import build_facility


ROOT = Path(__file__).resolve().parents[2]
REBUILD_DIR = ROOT / "src" / "Workspace" / "Rebuild"
STAGING_DIR = ROOT / "artifacts" / "greenfield_bunker"
OUTPUTS = {
    "staging": STAGING_DIR / "GreenfieldBunker.model.json",
    "active": REBUILD_DIR / "NewBunker.model.json",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(OUTPUTS), default="staging")
    parser.add_argument("--output", type=Path, help="Override output path for deterministic validation.")
    arguments = parser.parse_args()

    output = arguments.output or OUTPUTS[arguments.mode]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_facility(arguments.mode), indent=2) + "\n", encoding="utf-8")
    print("generated mode={} output={}".format(arguments.mode, output))


if __name__ == "__main__":
    main()
