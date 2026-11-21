#!/usr/bin/env python3
"""Idea2World 7.0 local studio app (stdlib HTTP server, no build step).

Screens are served by `templates/index.html` and backed by this JSON API:

    GET  /api/status                     brain + Studio + project status
    GET  /api/projects                   project list
    POST /api/create                     run the full pipeline as a background job
    GET  /api/projects/<id>              project detail + artifacts + versions
    GET  /api/projects/<id>/preview.svg   top-down world plan
    GET  /api/projects/<id>/artifact/<n>  world_spec, art_direction, qa, visual_qa, ...
    GET  /api/projects/<id>/luau/<file>   generated module source
    POST /api/projects/<id>/build         build in Studio (or the simulator)
    POST /api/projects/<id>/capture       screenshots + visual review
    POST /api/projects/<id>/playtest      run the place and read the console
    POST /api/projects/<id>/validate      static Luau + spec validation
    POST /api/projects/<id>/restore       roll back to a version
    GET  /api/projects/<id>/download      export zip
    GET  /api/jobs/<id>                  job status + event stream

Legacy 5.0 endpoints (`/api/generate`, `/download/luau`, `/download/blueprint`) remain available so
existing Hermes callers keep working.
"""
from __future__ import annotations

import json
import os
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = Path(os.environ.get("IDEA2WORLD_PROJECTS", ROOT_DIR / "projects"))

from agents import creative_director  # noqa: E402
from codegen import luau_generator, luau_validator, module_assembler  # noqa: E402
from core.jobs import JobManager  # noqa: E402
from core.orchestrator import DEFAULT_SETTINGS, Pipeline, normalize_settings  # noqa: E402
from core.project_memory import ProjectStore, read_json  # noqa: E402
from core.provider_router import ProviderRouter, extract_json  # noqa: E402
from qa import visual_qa  # noqa: E402
from studio import build_executor, playtest_manager, screenshot_manager, studio_mcp_client  # noqa: E402
from world.preview import plan_svg  # noqa: E402
from world.world_spec import WorldSpec  # noqa: E402

# Legacy 5.0 engine (kept for backwards compatibility with existing Hermes prompts).
try:
    import legacy_api
except Exception:  # noqa: BLE001 - legacy support is optional
    legacy_api = None

STORE = ProjectStore(PROJECTS_DIR)
JOBS = JobManager()
BRAIN = ProviderRouter()


def load_dotenv() -> None:
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError:
        pass


load_dotenv()
BRAIN = ProviderRouter()


def project_spec(project) -> WorldSpec:
    data = project.load_artifact("world_spec")
    if not data:
        raise FileNotFoundError("this project has no WorldSpec yet")
    return WorldSpec.from_dict(data)


def studio_status() -> dict:
    binary = studio_mcp_client.discover_binary()
    return {
        "binary": binary,
        "available": bool(binary),
        "configured": bool(os.environ.get("IDEA2WORLD_STUDIO_MCP")),
        "hint": ("Enable it in Studio: Assistant → Manage MCP Servers → Enable Studio as MCP server. "
                 "Then restart Studio and press Probe."),
    }


def slim_result(result: dict) -> dict:
    """Keep the API response small; full data stays in project artifacts."""
    keep = ("project", "title", "idea", "settings", "brain", "design", "art_direction", "references",
            "world", "plan", "preview_svg", "navigation", "assets", "codegen", "world_engine", "ui_studio",
            "visual", "performance",
            "structural", "gameplay", "qa", "studio", "screenshots", "repair", "export", "approval",
            "decisions", "timeline", "seconds")
    return {key: result.get(key) for key in keep}


class Handler(BaseHTTPRequestHandler):
    server_version = "Idea2World/7.0"

    # -- plumbing ---------------------------------------------------------------------
    def log_message(self, fmt, *args):
        if os.environ.get("IDEA2WORLD_VERBOSE"):
            print("[Idea2World] " + fmt % args)

    def send_json(self, payload, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body: bytes, mime: str, status: int = 200, filename: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def error(self, message: str, status: int = 400) -> None:
        self.send_json({"error": message, "status": status}, status)

    # -- routing ----------------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        try:
            if path in ("/", "/index.html"):
                return self.serve_static("index.html", "text/html; charset=utf-8")
            if path.startswith("/static/"):
                return self.serve_static(path[len("/static/"):])
            if path == "/api/status":
                return self.send_json({
                    "app": "Idea2World", "version": "7.0.0",
                    "brain": BRAIN.describe(), "studio": studio_status(),
                    "projects": len(STORE.list()),
                    "defaults": DEFAULT_SETTINGS,
                    "jobs": JOBS.list(5),
                    "quality_threshold": visual_qa.TARGET_SCORE,
                })
            if path == "/api/projects":
                return self.send_json({"projects": STORE.list()})
            if path == "/api/jobs":
                return self.send_json({"jobs": JOBS.list()})
            if path.startswith("/api/jobs/"):
                job = JOBS.get(path.rsplit("/", 1)[-1])
                if not job:
                    return self.error("job not found", 404)
                cursor = int((query.get("cursor") or ["0"])[0])
                return self.send_json(job.to_dict(event_cursor=cursor))
            if path == "/api/studio/status":
                return self.send_json(studio_status())
            if path.startswith("/api/projects/"):
                return self.project_get(path, query)
            return self.error("not found", 404)
        except Exception as exc:  # noqa: BLE001 - one bad request must not kill the server
            traceback.print_exc()
            return self.error(f"{type(exc).__name__}: {exc}", 500)

    def project_get(self, path: str, query: dict) -> None:
        parts = path.strip("/").split("/")
        # /api/projects/<id>/...
        if len(parts) < 3:
            return self.error("not found", 404)
        project_id = parts[2]
        try:
            project = STORE.get(project_id)
        except FileNotFoundError:
            return self.error("project not found", 404)
        if len(parts) == 3:
            detail = project.summary()
            detail.update({
                "artifacts": project.list_artifacts(),
                "versions": project.versions(),
                "screenshots": project.meta.get("screenshots", []),
                "approval": project.load_artifact("approval"),
                "settings": project.meta.get("settings", {}),
            })
            return self.send_json(detail)
        action = parts[3]
        if action == "preview.svg":
            svg = plan_svg(project_spec(project), 900, 900)
            return self.send_bytes(svg.encode("utf-8"), "image/svg+xml; charset=utf-8")
        if action == "artifact" and len(parts) >= 5:
            name = parts[4]
            data = project.load_artifact(name)
            if data is None:
                return self.error(f"artifact '{name}' not found", 404)
            return self.send_json(data)
        if action == "luau" and len(parts) >= 5:
            filename = Path("/".join(parts[4:])).name
            file_path = project.luau_dir / filename
            if not file_path.exists():
                return self.error("file not found", 404)
            return self.send_bytes(file_path.read_bytes(), "text/plain; charset=utf-8")
        if action == "luau":
            files = []
            if project.luau_dir.exists():
                for item in sorted(project.luau_dir.iterdir()):
                    if item.is_file():
                        files.append({"name": item.name, "bytes": item.stat().st_size,
                                      "lines": item.read_text(encoding="utf-8").count("\n") + 1})
            return self.send_json({"files": files})
        if action == "download":
            archive = project.load_artifact("export")
            if not archive or not Path(archive.get("zip", "")).exists():
                return self.error("no export yet; run the pipeline or POST /export", 404)
            return self.send_bytes(Path(archive["zip"]).read_bytes(), "application/zip",
                                   filename=Path(archive["zip"]).name)
        if action == "screenshot" and len(parts) >= 5:
            file_path = project.screenshots_dir / Path(parts[4]).name
            if not file_path.exists():
                return self.error("screenshot not found", 404)
            return self.send_bytes(file_path.read_bytes(), "image/png")
        return self.error("not found", 404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self.read_json()
        except Exception:  # noqa: BLE001
            return self.error("invalid JSON body")
        try:
            if path == "/api/generate":
                return self.legacy_generate(body)
            if path in ("/download/luau", "/download/blueprint"):
                return self.legacy_download(path, body)
            if path == "/api/projects":
                idea = str(body.get("idea", "")).strip()
                project = STORE.create(idea, str(body.get("title", "")), body.get("settings") or {})
                return self.send_json({"project": project.summary()}, 201)
            if path == "/api/create":
                return self.create_world(body)
            if path == "/api/studio/probe":
                return self.studio_probe()
            if path.startswith("/api/projects/"):
                return self.project_post(path, body)
            return self.error("not found", 404)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self.error(f"{type(exc).__name__}: {exc}", 500)

    def do_DELETE(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path.startswith("/api/projects/"):
            project_id = path.strip("/").split("/")[2]
            try:
                STORE.delete(project_id)
                return self.send_json({"deleted": project_id})
            except Exception as exc:  # noqa: BLE001
                return self.error(str(exc), 400)
        return self.error("not found", 404)

    # -- actions ----------------------------------------------------------------------
    def create_world(self, body: dict) -> None:
        idea = str(body.get("idea", "")).strip()
        if len(idea) < 3:
            return self.error("describe the world idea (at least 3 characters)")
        settings = normalize_settings({**DEFAULT_SETTINGS, **(body.get("settings") or {})})
        title = str(body.get("title", "")).strip()

        def job_fn(job):
            pipeline = Pipeline(root=PROJECTS_DIR, brain=BRAIN, events=job.emit)
            job.meta["idea"] = idea
            result = pipeline.run(idea, settings, title=title)
            job.meta["project"] = result["project"]["id"]
            return slim_result(result)

        job = JOBS.start("create_world", job_fn, {"idea": idea[:160], "settings": settings})
        JOBS.prune()
        return self.send_json({"job": job.to_dict(include_events=False)}, 202)

    def project_post(self, path: str, body: dict) -> None:
        parts = path.strip("/").split("/")
        if len(parts) < 4:
            return self.error("not found", 404)
        project_id, action = parts[2], parts[3]
        try:
            project = STORE.get(project_id)
        except FileNotFoundError:
            return self.error("project not found", 404)

        if action == "validate":
            spec = project_spec(project)
            luau = luau_validator.validate_project(project.luau_dir)
            report = {"spec": spec.validate(), "luau": luau}
            project.save_artifact("validation", report)
            return self.send_json(report)

        if action == "restore":
            version = str(body.get("version", "")).strip()
            if not version:
                return self.error("version is required")
            return self.send_json(project.restore(version))

        if action == "export":
            spec = project_spec(project)
            summary = {"visual_score": (project.meta.get("scores") or {}).get("visual"),
                       "checks": {"luau_simulated_build": False}}
            archive = module_assembler.export_archive(project, spec, summary)
            project.save_artifact("export", archive)
            return self.send_json(archive)

        if action == "build":
            mode = str(body.get("mode", "auto"))
            spec = project_spec(project)
            sources = luau_generator.project_sources(spec)
            luau_generator.write_project(spec, project.luau_dir)

            def job_fn(job):
                client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir),
                                                   allow_mock=(mode == "simulate"),
                                                   force_mock=(mode == "simulate"))
                try:
                    result = build_executor.run_full_build(
                        client, project.dir, spec, sources,
                        enable_meshes=bool(body.get("mesh_generation")))
                    try:
                        result["validation"] = build_executor.validate(client)
                    except Exception as exc:  # noqa: BLE001
                        result["validation"] = {"passed": False, "error": str(exc)[:300]}
                    job.emit({"type": "build_done", "ok": result.get("ok"),
                              "instances": result.get("instances", 0)})
                finally:
                    try:
                        client.close()
                    except Exception:  # noqa: BLE001
                        pass
                project.save_artifact("build_report", result)
                return {"build": result}

            job = JOBS.start("build", job_fn, {"project": project_id, "mode": mode})
            return self.send_json({"job": job.to_dict(include_events=False)}, 202)

        if action == "capture":
            spec = project_spec(project)

            def job_fn(job):
                client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir),
                                                   allow_mock=True)
                try:
                    capture = screenshot_manager.capture_views(client, spec, project.screenshots_dir)
                    for entry in capture.get("captured", []):
                        project.add_screenshot(entry["file"], entry.get("label", ""))
                finally:
                    try:
                        client.close()
                    except Exception:  # noqa: BLE001
                        pass
                shots = [e["file"] for e in capture.get("captured", [])]
                review = visual_qa.evaluate(spec, screenshots=shots,
                                            brain=BRAIN if BRAIN.available else None,
                                            performance=project.load_artifact("performance"))
                project.save_artifact("visual_qa", review)
                job.emit({"type": "capture_done", "captured": len(shots),
                          "score": review.get("total")})
                return {"capture": capture, "visual": review}

            job = JOBS.start("capture", job_fn, {"project": project_id})
            return self.send_json({"job": job.to_dict(include_events=False)}, 202)

        if action == "playtest":
            def job_fn(job):
                client = studio_mcp_client.connect(prefer_mock_project=str(project.luau_dir),
                                                   allow_mock=True)
                try:
                    result = playtest_manager.playtest(client, seconds=int(body.get("seconds", 20)))
                finally:
                    try:
                        client.close()
                    except Exception:  # noqa: BLE001
                        pass
                project.save_artifact("playtest", result)
                job.emit({"type": "playtest_done", "passed": result.get("passed")})
                return {"playtest": result}

            job = JOBS.start("playtest", job_fn, {"project": project_id})
            return self.send_json({"job": job.to_dict(include_events=False)}, 202)

        if action == "approve":
            spec = project_spec(project)
            verdict = creative_director.approve(
                spec,
                design=project.load_artifact("game_design"),
                art=project.load_artifact("art_direction"),
                luau_validation=project.load_artifact("luau_project", {}).get("validation"),
                build_report=project.load_artifact("build_report"),
                playtest=project.load_artifact("playtest"),
                visual=project.load_artifact("visual_qa"),
                qa=project.load_artifact("qa"),
                export=project.load_artifact("export"))
            project.save_artifact("approval", verdict)
            return self.send_json(verdict)

        return self.error("not found", 404)

    def studio_probe(self) -> None:
        binary = studio_mcp_client.discover_binary()
        if not binary:
            return self.send_json({"connected": False, **studio_status()})
        client = studio_mcp_client.StudioMCPClient(binary, timeout=20, startup_timeout=20)
        try:
            client.start()
            return self.send_json({"connected": True, **client.status()})
        except Exception as exc:  # noqa: BLE001
            return self.send_json({"connected": False, "binary": binary, "error": str(exc)})
        finally:
            client.stop()

    # -- legacy 5.0 -------------------------------------------------------------------
    def legacy_generate(self, body: dict) -> None:
        if legacy_api is None:
            return self.error("legacy engine unavailable", 501)
        return self.send_json(legacy_api.generate(body))

    def legacy_download(self, path: str, body: dict) -> None:
        if legacy_api is None:
            return self.error("legacy engine unavailable", 501)
        content, filename, mime = legacy_api.download(path, body)
        return self.send_bytes(content, mime, filename=filename)

    # -- static -----------------------------------------------------------------------
    def serve_static(self, relative: str, mime: str | None = None) -> None:
        relative = relative or "index.html"
        candidates = [ROOT_DIR / "templates" / relative, ROOT_DIR / "static" / relative]
        for candidate in candidates:
            resolved = candidate.resolve()
            allowed = resolved.parent == (ROOT_DIR / "templates").resolve() or \
                (ROOT_DIR / "static").resolve() in resolved.parents
            if not allowed or not resolved.is_file():
                continue
            if mime is None:
                mime = {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
                        ".svg": "image/svg+xml", ".png": "image/png",
                        ".html": "text/html; charset=utf-8"}.get(resolved.suffix, "application/octet-stream")
            return self.send_bytes(resolved.read_bytes(), mime)
        return self.error("file not found", 404)


def main() -> None:
    load_dotenv()
    host = os.environ.get("IDEA2WORLD_HOST", "127.0.0.1")
    port = int(os.environ.get("IDEA2WORLD_PORT", "8765"))
    brain = BRAIN.describe()
    print(f"Idea2World 7.0 studio → http://{host}:{port}")
    print(f"  brain:   {brain['provider'] + ':' + str(brain['model']) if brain['available'] else 'offline deterministic planner'}")
    studio = studio_status()
    print(f"  studio:  {'found ' + str(studio['binary']) if studio['available'] else 'StudioMCP not found'}")
    print(f"  projects: {PROJECTS_DIR}")
    try:
        ThreadingHTTPServer((host, port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
