"""Rollback: project snapshots on disk plus the in-Studio archive the build itself keeps.

Two independent safety nets:
  * `Project.snapshot()` copies the whole project (spec, Luau, reports) into `versions/vNNN`;
  * the generated MapBootstrap moves the previous world into `ServerStorage/Idea2World_Backups`
    before rebuilding, keeping the three most recent worlds.

So a bad iteration is recoverable with or without the app running.
"""
from __future__ import annotations

from pathlib import Path


class RollbackManager:
    def __init__(self, project):
        self.project = project

    def checkpoint(self, label: str, include_screenshots: bool = False) -> dict:
        version = self.project.snapshot(label, include_screenshots=include_screenshots)
        return {"version": version, "label": label, "versions": len(self.project.versions())}

    def history(self) -> list[dict]:
        return self.project.versions()

    def restore(self, version_id: str) -> dict:
        return self.project.restore(version_id)

    def restore_latest(self) -> dict:
        versions = self.project.versions()
        if len(versions) < 2:
            raise FileNotFoundError("no earlier version to restore")
        return self.project.restore(versions[-2]["version"])

    def prune(self, keep: int = 10) -> dict:
        versions = self.project.versions()
        removed = []
        for entry in versions[:-keep] if len(versions) > keep else []:
            target = self.project.versions_dir / entry["version"]
            if target.exists():
                for child in target.iterdir():
                    if child.is_dir():
                        import shutil
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
                target.rmdir()
                removed.append(entry["version"])
        return {"removed": removed, "kept": min(len(versions), keep)}


def studio_rollback_code(steps: int = 1) -> str:
    """Luau that restores the most recent archived world inside Studio."""
    return f'''-- Restore the previous Idea2World build from ServerStorage
local storage = game:GetService("ServerStorage")
local backups = storage:FindFirstChild("Idea2World_Backups")
if not backups then return {{ restored = false, reason = "no backups" }} end
local archives = {{}}
for _, child in ipairs(backups:GetChildren()) do table.insert(archives, child) end
table.sort(archives, function(a, b) return a.Name > b.Name end)
if #archives == 0 then return {{ restored = false, reason = "no backups" }} end
local target = archives[{max(1, steps)}]
local root = workspace:FindFirstChild("Idea2World_Generated")
if root then root:Destroy() end
local restored = Instance.new("Folder")
restored.Name = "Idea2World_Generated"
for _, child in ipairs(target:GetChildren()) do child.Parent = restored end
restored.Parent = workspace
return {{ restored = true, from = target.Name, objects = #restored:GetChildren() }}'''


def restore_in_studio(client, steps: int = 1) -> dict:
    result = client.execute_luau(studio_rollback_code(steps))
    return result.get("json") or {"restored": False, "error": result.get("text", "")}


def cleanup_old_projects(root, keep: int = 20) -> list[str]:
    base = Path(root)
    if not base.exists():
        return []
    projects = sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True)
    removed = []
    for project in projects[keep:]:
        import shutil
        shutil.rmtree(project, ignore_errors=True)
        removed.append(project.name)
    return removed
