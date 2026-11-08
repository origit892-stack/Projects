#!/usr/bin/env python3

import sys
import os
import json
import time
import shutil
from pathlib import Path

import obsws_python as obs

HOST = "localhost"
PORT = 4455

ROOT = Path("/Users/Ori/Documents/Projects/BunkerGame")
CAPTURE_DIR = ROOT / "visual-qa" / "captures"
STATE_FILE = ROOT / "visual-qa" / ".obs_capture_state.json"

CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def client():
    return obs.ReqClient(host=HOST, port=PORT, timeout=5)


def safe_label(value):
    cleaned = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in value
    )
    return cleaned.strip("_") or "playtest"


def save_state(data):
    STATE_FILE.write_text(json.dumps(data, indent=2))


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def clear_state():
    try:
        STATE_FILE.unlink()
    except FileNotFoundError:
        pass


def verify():
    try:
        cl = client()
        version = cl.get_version()
        status = cl.get_record_status()

        print("VISUAL_QA_OBS_VERIFY=PASS")
        print(f"OBS_VERSION={version.obs_version}")
        print(f"OBS_WEBSOCKET_VERSION={version.obs_web_socket_version}")
        print(f"OBS_RECORDING={status.output_active}")
        print(f"CAPTURE_DIR={CAPTURE_DIR}")
        return 0
    except Exception as exc:
        print("VISUAL_QA_OBS_VERIFY=FAIL")
        print(f"ERROR={type(exc).__name__}: {exc}")
        return 1


def status():
    try:
        cl = client()
        result = cl.get_record_status()

        print("VISUAL_QA_OBS_STATUS=PASS")
        print(f"OBS_RECORDING={result.output_active}")

        state = load_state()
        if state:
            print(f"LABEL={state.get('label', '')}")
            print(f"STARTED_AT={state.get('started_at', '')}")

        return 0
    except Exception as exc:
        print("VISUAL_QA_OBS_STATUS=FAIL")
        print(f"ERROR={type(exc).__name__}: {exc}")
        return 1


def start(label):
    label = safe_label(label)

    try:
        cl = client()
        current = cl.get_record_status()

        if current.output_active:
            print("VISUAL_QA_OBS_START=FAIL")
            print("ERROR=OBS_ALREADY_RECORDING")
            return 2

        cl.start_record()

        save_state({
            "label": label,
            "started_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
        })

        print("VISUAL_QA_OBS_START=PASS")
        print(f"LABEL={label}")
        return 0

    except Exception as exc:
        print("VISUAL_QA_OBS_START=FAIL")
        print(f"ERROR={type(exc).__name__}: {exc}")
        return 1


def stop():
    try:
        cl = client()
        current = cl.get_record_status()

        if not current.output_active:
            print("VISUAL_QA_OBS_STOP=FAIL")
            print("ERROR=OBS_NOT_RECORDING")
            return 2

        result = cl.stop_record()
        source_path = Path(result.output_path)

        state = load_state()
        label = safe_label(state.get("label", "playtest"))
        stamp = state.get(
            "started_at",
            time.strftime("%Y-%m-%d_%H-%M-%S")
        )

        if not source_path.exists():
            print("VISUAL_QA_OBS_STOP=FAIL")
            print(f"ERROR=OUTPUT_NOT_FOUND:{source_path}")
            return 3

        extension = source_path.suffix or ".mkv"
        destination = CAPTURE_DIR / f"{stamp}_{label}{extension}"

        if source_path.resolve() != destination.resolve():
            shutil.move(str(source_path), str(destination))

        clear_state()

        size = destination.stat().st_size

        print("VISUAL_QA_OBS_STOP=PASS")
        print(f"VISUAL_QA_RECORD_PATH={destination}")
        print(f"VISUAL_QA_RECORD_BYTES={size}")
        return 0

    except Exception as exc:
        print("VISUAL_QA_OBS_STOP=FAIL")
        print(f"ERROR={type(exc).__name__}: {exc}")
        return 1


def latest():
    files = [
        p for p in CAPTURE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {
            ".mp4", ".mov", ".mkv"
        }
    ]

    if not files:
        print("VISUAL_QA_LATEST=NONE")
        return 1

    newest = max(files, key=lambda p: p.stat().st_mtime)

    print("VISUAL_QA_LATEST=PASS")
    print(f"VISUAL_QA_LATEST_PATH={newest}")
    print(f"VISUAL_QA_LATEST_BYTES={newest.stat().st_size}")
    print(
        "VISUAL_QA_LATEST_MTIME="
        + time.strftime(
            "%Y-%m-%d_%H-%M-%S",
            time.localtime(newest.stat().st_mtime)
        )
    )
    return 0


def main():
    if len(sys.argv) < 2:
        print(
            "usage: obs_capture.py "
            "verify|status|start LABEL|stop|latest"
        )
        return 2

    command = sys.argv[1].lower()

    if command == "verify":
        return verify()

    if command == "status":
        return status()

    if command == "start":
        if len(sys.argv) < 3:
            print("ERROR=LABEL_REQUIRED")
            return 2
        return start(sys.argv[2])

    if command == "stop":
        return stop()

    if command == "latest":
        return latest()

    print(f"ERROR=UNKNOWN_COMMAND:{command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
