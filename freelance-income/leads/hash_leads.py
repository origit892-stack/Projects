#!/usr/bin/env python3
"""Canonical leads-array hash for the leads console change detection.

Usage: python3 hash_leads.py [STATE.json path]
Prints the sha256 of the leads array serialized canonically:
json.dumps(leads, sort_keys=True, separators=(",", ":")) — utf-8.

This is THE algorithm for .last_check.json "hash". Do not use any other
serialization (the 2026-11-14 drift between cron runs made change
detection useless; this pins it).
"""
import hashlib
import json
import sys


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else (
        "/Users/Ori/Documents/Projects/freelance-income/leads/STATE.json"
    )
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    blob = json.dumps(state["leads"], sort_keys=True, separators=(",", ":")).encode("utf-8")
    print(hashlib.sha256(blob).hexdigest())


if __name__ == "__main__":
    main()
