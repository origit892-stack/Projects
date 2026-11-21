"""Project memory: projects, artifacts, versions and rollback.

Layout under `projects/<project_id>/`:

    project.json          metadata + settings
    world_spec.json       the contract
    art_direction.json    visual language
    game_design.json      research-informed brief
    luau/                 generated modular project
    screenshots/          Studio captures
    reports/              qa.json, visual_qa.json, build_report.json, validation.json
    decisions.json        decision log
    versions/v001/...     full snapshots for rollback

Writes are atomic (write to .tmp then rename) so an interrupted build cannot corrupt a project.
"""
from __future__ import annotations

import json
import re
import shutil
import time
from pathlib import Path

ARTIFACTS = ("world_spec", "art_direction", "game_design", "assets", "luau_project", "visual_qa",
             "qa", "build_report", "validation", "export")


def slugify(text: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", (text or "world").strip().lower()).strip("_")
    return (base[:40] or "world")


def atomic_write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


class Project:
    def __init__(self, root: Path, project_id: str, meta: dict):
        self.root = root
        self.id = project_id
        self.meta = meta

    # -- paths ------------------------------------------------------------------------
    @property
    def dir(self) -> Path:
        return self.root / self.id

    @property
    def luau_dir(self) -> Path:
        return self.dir / "luau"

    @property
    def screenshots_dir(self) -> Path:
        return self.dir / "screenshots"

    @property
    def reports_dir(self) -> Path:
        return self.dir / "reports"

    @property
    def versions_dir(self) -> Path:
        return self.dir / "versions"

    @property
    def spec_path(self) -> Path:
        return self.dir / "world_spec.json"

    def artifact_path(self, name: str) -> Path:
        if name == "world_spec":
            return self.spec_path
        return self.reports_dir / f"{name}.json" if name in ("qa", "visual_qa", "build_report", "validation") \
            else self.dir / f"{name}.json"

    # -- io ---------------------------------------------------------------------------
    def save(self) -> None:
        atomic_write_json(self.dir / "project.json", self.meta)

    def save_artifact(self, name: str, data) -> Path:
        path = self.artifact_path(name)
        atomic_write_json(path, data)
        stamps = self.meta.setdefault("artifacts", {})
        stamps[name] = {"saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "path": str(path.relative_to(self.dir))}
        self.save()
        return path

    def load_artifact(self, name: str, default=None):
        return read_json(self.artifact_path(name), default)

    def list_artifacts(self) -> dict:
        return dict(self.meta.get("artifacts", {}))

    # -- versions ---------------------------------------------------------------------
    def snapshot(self, label: str = "checkpoint", include_screenshots: bool = False) -> str:
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        existing = sorted(p.name for p in self.versions_dir.iterdir() if (p / "snapshot.json").exists())
        number = len(existing) + 1
        version_id = f"v{number:03d}"
        target = self.versions_dir / version_id
        target.mkdir(parents=True, exist_ok=True)
        for item in self.dir.iterdir():
            if item.name in ("versions", "screenshots"):
                continue
            if item.is_file():
                shutil.copy2(item, target / item.name)
            elif item.is_dir() and item.name in ("luau", "reports"):
                shutil.copytree(item, target / item.name, dirs_exist_ok=True)
        if include_screenshots and self.screenshots_dir.exists():
            shutil.copytree(self.screenshots_dir, target / "screenshots", dirs_exist_ok=True)
        atomic_write_json(target / "snapshot.json", {
            "version": version_id, "label": label,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "project": self.id, "title": self.meta.get("title", ""),
        })
        history = self.meta.setdefault("versions", [])
        history.append({"id": version_id, "label": label})
        self.save()
        # Keep ten versions on disk; older checkpoints are pruned oldest-first.
        for stale in existing[:max(0, len(existing) + 1 - 10)]:
            shutil.rmtree(self.versions_dir / stale, ignore_errors=True)
        return version_id

    def restore(self, version_id: str) -> dict:
        source = self.versions_dir / version_id
        if not (source / "snapshot.json").exists():
            raise FileNotFoundError(f"unknown version {version_id}")
        for item in source.iterdir():
            if item.name == "snapshot.json":
                continue
            destination = self.dir / item.name
            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(item, destination)
        self.meta = read_json(self.dir / "project.json", self.meta)
        self.meta.setdefault("versions", []).append({
            "id": version_id, "label": "restored", "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        self.save()
        return {"restored": version_id, "files": [p.name for p in source.iterdir()]}

    def versions(self) -> list[dict]:
        if not self.versions_dir.exists():
            return []
        out = []
        for item in sorted(self.versions_dir.iterdir()):
            meta = read_json(item / "snapshot.json")
            if meta:
                out.append(meta)
        return out

    def add_screenshot(self, path: str | Path, view: str = "") -> str:
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        source = Path(path)
        stamp = time.strftime("%H%M%S", time.gmtime())
        name = f"{stamp}_{slugify(view or source.stem)}{source.suffix or '.png'}"
        target = self.screenshots_dir / name
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        shots = self.meta.setdefault("screenshots", [])
        shots.append({"file": name, "view": view, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        self.save()
        return name

    def summary(self) -> dict:
        return {"id": self.id, "title": self.meta.get("title"), "idea": self.meta.get("idea"),
                "created_at": self.meta.get("created_at"), "updated_at": self.meta.get("updated_at"),
                "stage": self.meta.get("stage", "created"), "artifacts": list(self.meta.get("artifacts", {})),
                "versions": len(self.meta.get("versions", [])),
                "screenshots": len(self.meta.get("screenshots", [])),
                "scores": self.meta.get("scores", {})}


class ProjectStore:
    def __init__(self, root: str | Path = "projects"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, idea: str, title: str = "", settings: dict | None = None) -> Project:
        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        base_id = f"{stamp}_{slugify(title or idea)}"
        project_id = base_id
        counter = 2
        while (self.root / project_id).exists():
            project_id = f"{base_id}_{counter}"
            counter += 1
        meta = {
            "id": project_id, "title": title or idea[:60], "idea": idea,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "stage": "created", "settings": settings or {}, "artifacts": {}, "versions": [],
        }
        project = Project(self.root, project_id, meta)
        project.dir.mkdir(parents=True, exist_ok=True)
        project.save()
        return project

    def get(self, project_id: str) -> Project:
        directory = self.root / project_id
        meta = read_json(directory / "project.json")
        if meta is None:
            raise FileNotFoundError(f"project '{project_id}' not found")
        return Project(self.root, project_id, meta)

    def list(self) -> list[dict]:
        out = []
        for item in sorted(self.root.iterdir(), reverse=True):
            if not item.is_dir():
                continue
            meta = read_json(item / "project.json")
            if meta:
                project = Project(self.root, item.name, meta)
                out.append(project.summary())
        return out

    def delete(self, project_id: str) -> None:
        target = self.root / project_id
        if target.exists():
            shutil.rmtree(target)
