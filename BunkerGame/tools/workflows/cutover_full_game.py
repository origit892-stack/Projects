#!/usr/bin/env python3
"""Perform the journaled FG-GREENFIELD-001 source cutover.

The two source roots stay on the same filesystem and are promoted only with
rename operations. The temporary journal retains the prior mapped project until
post-cutover source and Studio validation are complete. The immutable full-game
backup remains the recovery source after journal finalization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_ROOT = ROOT / "artifacts" / "full_game_candidate"
JOURNAL_ROOT = ROOT / "artifacts" / "full_game_cutover_journal"
RECEIPT_PATH = ROOT / "artifacts" / "full_game_cutover_receipt.json"
BACKUP_MANIFEST = (
    ROOT
    / "backups"
    / "full_game"
    / "20260826_174739_pre_full_greenfield_rebuild"
    / "BACKUP_MANIFEST.md"
)
STATUS_PATH = ROOT / "docs" / "director" / "FULL-GAME-STATUS.md"
REQUIRED_POST_CUTOVER_EVIDENCE_MARKERS = (
    "FULL_GAME_POST_CUTOVER_STATIC=PASS",
    "FULL_GAME_STUDIO_EDIT=PASS",
    "FULL_GAME_PLAY_FOUNDATION=PASS",
)
REQUIRED_FINALIZATION_EVIDENCE_MARKERS = (
    *REQUIRED_POST_CUTOVER_EVIDENCE_MARKERS,
    "FULL_GAME_TECHNICAL_QA=PASS",
    "FULL_GAME_GAMEPLAY_UX_QA=PASS",
    "FULL_GAME_VISUAL_QA=PASS",
    "FULL_GAME_INTEGRATION_REVIEW=PASS",
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_digest(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        fail(f"expected directory is missing: {root}")

    digest = hashlib.sha256()
    files = 0
    bytes_total = 0
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            target = os.readlink(path)
            encoded = f"L\0{relative}\0{target}".encode("utf-8")
            digest.update(encoded)
            files += 1
            continue
        if not path.is_file():
            fail(f"unsupported source entry in cutover scope: {path}")
        size = path.stat().st_size
        digest.update(f"F\0{relative}\0{size}\0".encode("utf-8"))
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        files += 1
        bytes_total += size
    return {"sha256": digest.hexdigest(), "files": files, "bytes": bytes_total}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)
    directory_descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def read_journal() -> dict[str, Any]:
    transaction_path = JOURNAL_ROOT / "transaction.json"
    if not transaction_path.is_file():
        fail(f"cutover journal is missing: {transaction_path}")
    with transaction_path.open("r", encoding="utf-8") as source:
        journal = json.load(source)
    if not isinstance(journal, dict):
        fail("cutover journal is invalid")
    return journal


def update_journal(journal: dict[str, Any], state: str) -> None:
    journal["state"] = state
    journal["updatedAtUnix"] = int(time.time())
    write_json(JOURNAL_ROOT / "transaction.json", journal)


def source_paths() -> dict[str, Path]:
    return {
        "active_src": ROOT / "src",
        "active_project": ROOT / "default.project.json",
        "candidate_src": CANDIDATE_ROOT / "src",
        "candidate_project": CANDIDATE_ROOT / "default.project.json",
        "legacy_src": JOURNAL_ROOT / "legacy_src",
        "legacy_project": JOURNAL_ROOT / "legacy_default.project.json",
    }


def relative_to_root(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        fail(f"path must stay inside the project root: {path}")


def current_snapshot(src: Path, project: Path) -> dict[str, Any]:
    return {
        "projectSha256": file_digest(project),
        "src": tree_digest(src),
    }


def validate_evidence_file(path: Path) -> dict[str, Any]:
    expanded = path.expanduser()
    resolved = (ROOT / expanded).resolve() if not expanded.is_absolute() else expanded.resolve()
    if not resolved.is_file():
        fail(f"post-cutover evidence is missing: {resolved}")
    relative = relative_to_root(resolved)
    if resolved.is_relative_to(JOURNAL_ROOT):
        fail("post-cutover evidence cannot live inside the removable cutover journal")
    content = resolved.read_text(encoding="utf-8")
    evidence_lines = {line.strip() for line in content.splitlines()}
    missing = [marker for marker in REQUIRED_POST_CUTOVER_EVIDENCE_MARKERS if marker not in evidence_lines]
    if missing:
        fail(f"post-cutover evidence is missing required markers: {', '.join(missing)}")
    return {
        "path": relative,
        "sha256": file_digest(resolved),
        "markers": list(REQUIRED_POST_CUTOVER_EVIDENCE_MARKERS),
    }


def verify_finalization_readiness(evidence_path: Path) -> None:
    content = evidence_path.read_text(encoding="utf-8")
    evidence_lines = {line.strip() for line in content.splitlines()}
    missing = [marker for marker in REQUIRED_FINALIZATION_EVIDENCE_MARKERS if marker not in evidence_lines]
    if missing:
        fail(f"post-cutover evidence is not ready for journal finalization: {', '.join(missing)}")
    if not STATUS_PATH.is_file():
        fail(f"full-game status is missing: {STATUS_PATH}")
    status = STATUS_PATH.read_text(encoding="utf-8")
    try:
        current_status = status.split("## Current status", 1)[1].split("##", 1)[0]
    except IndexError:
        fail("full-game status has no Current status section")
    status_lines = [line.strip() for line in current_status.splitlines() if line.strip()]
    if status_lines != ["`DIRECTOR_REVIEW`"]:
        fail("journal finalization requires FULL-GAME-STATUS.md to be DIRECTOR_REVIEW")


def verified_post_cutover_validation(journal: dict[str, Any], paths: dict[str, Path]) -> dict[str, Any]:
    validation = journal.get("postCutoverValidation")
    if not isinstance(validation, dict):
        fail("post-cutover validation was not recorded; refusing journal finalization")
    expected_active = validation.get("active")
    expected_legacy = validation.get("legacy")
    evidence = validation.get("evidence")
    if not isinstance(expected_active, dict) or not isinstance(expected_legacy, dict) or not isinstance(evidence, dict):
        fail("post-cutover validation record is malformed")

    actual_active = current_snapshot(paths["active_src"], paths["active_project"])
    if actual_active != expected_active:
        fail("active source changed after post-cutover validation; revalidate and record it before finalization")
    actual_legacy = current_snapshot(paths["legacy_src"], paths["legacy_project"])
    if actual_legacy != expected_legacy or actual_legacy != journal.get("activeBefore"):
        fail("parked legacy source no longer matches the cutover journal")

    evidence_path = ROOT / evidence.get("path", "")
    validated_evidence = validate_evidence_file(evidence_path)
    if validated_evidence != evidence:
        fail("post-cutover evidence changed after validation was recorded")
    return validation


def verify_backup_marker() -> None:
    if not BACKUP_MANIFEST.is_file():
        fail(f"immutable backup manifest is missing: {BACKUP_MANIFEST}")
    manifest = BACKUP_MANIFEST.read_text(encoding="utf-8")
    if "FULL_GAME_BACKUP=PASS" not in manifest:
        fail("immutable backup marker FULL_GAME_BACKUP=PASS is missing")


def preflight() -> dict[str, Path]:
    verify_backup_marker()
    paths = source_paths()
    required = ("active_src", "active_project", "candidate_src", "candidate_project")
    for key in required:
        if not paths[key].exists():
            fail(f"required cutover path is missing: {paths[key]}")
    if not paths["active_src"].is_dir() or not paths["candidate_src"].is_dir():
        fail("active and candidate src paths must be directories")
    if not paths["active_project"].is_file() or not paths["candidate_project"].is_file():
        fail("active and candidate default.project.json paths must be files")
    if JOURNAL_ROOT.exists():
        fail(f"refusing to overwrite existing cutover journal: {JOURNAL_ROOT}")

    for path in (ROOT, CANDIDATE_ROOT, JOURNAL_ROOT.parent):
        if path.stat().st_dev != ROOT.stat().st_dev:
            fail(f"cutover paths must share one filesystem: {path}")

    required_candidate_paths = (
        paths["candidate_src"] / "ServerScriptService/Game/ServerBootstrap.server.luau",
        paths["candidate_src"] / "StarterPlayer/StarterPlayerScripts/GameClient/ClientBootstrap.client.luau",
        paths["candidate_src"] / "Workspace/GameWorld.model.json",
        paths["candidate_src"] / "Workspace/Runtime.model.json",
    )
    for path in required_candidate_paths:
        if not path.is_file():
            fail(f"candidate is incomplete: {path}")
    if '"StreamingEnabled": false' not in paths["candidate_project"].read_text(encoding="utf-8"):
        fail("candidate project must explicitly disable streaming")
    return paths


def rollback(paths: dict[str, Path], journal: dict[str, Any]) -> None:
    active_src = paths["active_src"]
    active_project = paths["active_project"]
    candidate_src = paths["candidate_src"]
    candidate_project = paths["candidate_project"]
    legacy_src = paths["legacy_src"]
    legacy_project = paths["legacy_project"]

    if active_src.exists() and not candidate_src.exists():
        os.rename(active_src, candidate_src)
    if active_project.exists() and not candidate_project.exists():
        os.rename(active_project, candidate_project)
    if legacy_src.exists() and not active_src.exists():
        os.rename(legacy_src, active_src)
    if legacy_project.exists() and not active_project.exists():
        os.rename(legacy_project, active_project)

    if not active_src.is_dir() or not active_project.is_file():
        fail("rollback could not restore the original active source")
    if not candidate_src.is_dir() or not candidate_project.is_file():
        fail("rollback could not restore the candidate source")
    update_journal(journal, "rolled_back")


def execute_cutover() -> None:
    paths = preflight()
    active_before = {
        "projectSha256": file_digest(paths["active_project"]),
        "src": tree_digest(paths["active_src"]),
    }
    candidate_before = {
        "projectSha256": file_digest(paths["candidate_project"]),
        "src": tree_digest(paths["candidate_src"]),
    }
    JOURNAL_ROOT.mkdir(parents=True)
    journal = {
        "task": "FG-GREENFIELD-001",
        "state": "prepared",
        "createdAtUnix": int(time.time()),
        "root": str(ROOT),
        "candidate": str(CANDIDATE_ROOT),
        "activeBefore": active_before,
        "candidateBefore": candidate_before,
    }
    update_journal(journal, "prepared")

    try:
        os.rename(paths["active_src"], paths["legacy_src"])
        update_journal(journal, "active_src_parked")
        os.rename(paths["active_project"], paths["legacy_project"])
        update_journal(journal, "active_project_parked")
        os.rename(paths["candidate_src"], paths["active_src"])
        update_journal(journal, "candidate_src_promoted")
        os.rename(paths["candidate_project"], paths["active_project"])
        update_journal(journal, "committed")
    except BaseException:
        rollback(paths, journal)
        raise

    print(json.dumps({"state": "committed", "journal": str(JOURNAL_ROOT)}, sort_keys=True))


def finalize_cutover() -> None:
    journal = read_journal()
    if journal.get("state") != "committed":
        fail(f"only a committed journal can be finalized, got {journal.get('state')!r}")
    paths = source_paths()
    if not paths["active_src"].is_dir() or not paths["active_project"].is_file():
        fail("active full-game source is missing; refusing journal finalization")
    if not paths["legacy_src"].is_dir() or not paths["legacy_project"].is_file():
        fail("legacy cutover payload is incomplete; refusing journal finalization")
    validation = verified_post_cutover_validation(journal, paths)
    verify_finalization_readiness(ROOT / validation["evidence"]["path"])

    receipt = dict(journal)
    receipt["state"] = "finalized"
    receipt["finalizedAtUnix"] = int(time.time())
    write_json(RECEIPT_PATH, receipt)
    shutil.rmtree(JOURNAL_ROOT)
    print(json.dumps({"state": "finalized", "receipt": str(RECEIPT_PATH)}, sort_keys=True))


def record_post_cutover_validation(evidence_path: Path | None) -> None:
    if evidence_path is None:
        fail("--record-validation requires --evidence <project-relative path>")
    journal = read_journal()
    if journal.get("state") != "committed":
        fail(f"only a committed journal can record validation, got {journal.get('state')!r}")
    paths = source_paths()
    if not paths["active_src"].is_dir() or not paths["active_project"].is_file():
        fail("active full-game source is missing; cannot record validation")
    if not paths["legacy_src"].is_dir() or not paths["legacy_project"].is_file():
        fail("legacy cutover payload is incomplete; cannot record validation")

    legacy = current_snapshot(paths["legacy_src"], paths["legacy_project"])
    if legacy != journal.get("activeBefore"):
        fail("parked legacy source no longer matches the cutover journal")
    validation = {
        "recordedAtUnix": int(time.time()),
        "active": current_snapshot(paths["active_src"], paths["active_project"]),
        "legacy": legacy,
        "evidence": validate_evidence_file(evidence_path),
    }
    journal["postCutoverValidation"] = validation
    update_journal(journal, "committed")
    print(json.dumps({"state": "validation_recorded", "journal": str(JOURNAL_ROOT)}, sort_keys=True))


def rollback_cutover() -> None:
    journal = read_journal()
    if journal.get("state") == "finalized":
        fail("a finalized journal cannot be rolled back; restore from the immutable backup instead")
    paths = source_paths()
    rollback(paths, journal)
    print(json.dumps({"state": "rolled_back", "journal": str(JOURNAL_ROOT)}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--dry-run", action="store_true", help="verify cutover prerequisites without changing source")
    actions.add_argument("--rollback", action="store_true", help="restore the parked legacy source from an existing journal")
    actions.add_argument("--finalize", action="store_true", help="remove a committed legacy journal after all required validation")
    actions.add_argument("--record-validation", action="store_true", help="record validated active hashes before finalization")
    parser.add_argument("--evidence", type=Path, help="project-relative post-cutover evidence with required PASS markers")
    arguments = parser.parse_args()
    if arguments.evidence is not None and not arguments.record_validation:
        parser.error("--evidence is only valid with --record-validation")

    try:
        if arguments.dry_run:
            paths = preflight()
            print(json.dumps({"state": "ready", "candidate": str(paths["candidate_src"]), "root": str(ROOT)}, sort_keys=True))
        elif arguments.rollback:
            rollback_cutover()
        elif arguments.finalize:
            finalize_cutover()
        elif arguments.record_validation:
            record_post_cutover_validation(arguments.evidence)
        else:
            execute_cutover()
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as failure:
        print(f"CUTOVER_ERROR: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
