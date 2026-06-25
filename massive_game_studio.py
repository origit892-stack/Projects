#!/usr/bin/env python3
"""
Massive Game Studio - CrewAI multi-agent 2D/3D game builder.

Installation:
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade "crewai[google-genai]" pydantic python-dotenv

Environment:
    export GEMINI_API_KEY="your-gemini-api-key"
    export CREWAI_MANAGER_MODEL="gemini/gemini-2.5-flash"  # optional
    export CREWAI_WORKER_MODEL="gemini/gemini-2.5-flash"   # optional

Run:
    python massive_game_studio.py
    python massive_game_studio.py --engine three
    python massive_game_studio.py --output-dir ./generated_games --milestones 6
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Type

from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency guard
    load_dotenv = None

try:
    from crewai import Agent, Crew, Process, Task
    from crewai.tools import BaseTool
except ImportError as exc:  # pragma: no cover - friendly setup error
    raise SystemExit(
        "CrewAI is not installed. Run:\n"
        '  pip install --upgrade "crewai[google-genai]" pydantic python-dotenv\n'
    ) from exc


DEFAULT_MILESTONES = [
    "Project Architecture & Engine Scaffold",
    "Core Game Loop, Scene Flow, and Global State",
    "Player Controller, Camera, and Input System",
    "Physics, Collision, Boundaries, and Interaction Rules",
    "UI/HUD, Menus, Save System, and Accessibility",
    "Content Systems, Juice, Playtest Fixes, and Final Packaging",
]

DEFAULT_GEMINI_MODEL = "gemini/gemini-2.5-flash"

SAFE_COMMANDS = {
    ("npm", "install"),
    ("npm", "run", "build"),
    ("npm", "run", "test"),
    ("npm", "test"),
}


def slugify(value: str, fallback: str = "massive-game") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or fallback


def normalize_relative_path(path: str) -> Path:
    cleaned = path.strip().replace("\\", "/")
    candidate = Path(cleaned)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe relative path: {path!r}")
    return candidate


def fenced_block(language: str, body: str) -> str:
    return f"```{language}\n{body.strip()}\n```"


class ScaffoldProjectInput(BaseModel):
    game_title: str = Field(..., description="The human-readable game title.")
    game_slug: str = Field(..., description="Filesystem-safe project slug.")
    engine: str = Field("phaser", description="Game engine: phaser for 2D, three for 3D.")


class ScaffoldProjectTool(BaseTool):
    name: str = "scaffold_game_project"
    description: str = (
        "Create a production-oriented Phaser or Three.js/Vite project scaffold with organized "
        "folders such as src/scenes, src/objects, src/systems, src/ui, src/data, "
        "src/styles, public/assets, tests, and docs."
    )
    args_schema: Type[BaseModel] = ScaffoldProjectInput
    output_root: str

    def _run(self, game_title: str, game_slug: str, engine: str = "phaser") -> str:
        engine = engine.strip().lower()
        if engine not in {"phaser", "three"}:
            raise ValueError("engine must be either 'phaser' or 'three'")
        root = Path(self.output_root).expanduser().resolve() / slugify(game_slug)
        folders = [
            "src/scenes",
            "src/objects",
            "src/systems",
            "src/ui",
            "src/data",
            "src/styles",
            "public/assets",
            "tests",
            "docs",
        ]
        for folder in folders:
            (root / folder).mkdir(parents=True, exist_ok=True)

        files = self._three_files(game_title) if engine == "three" else self._phaser_files(game_title)
        files["docs/global-memory.json"] = json.dumps(
            {
                "gameTitle": game_title,
                "engine": engine,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "milestones": [],
                "systems": {},
                "openRisks": [],
            },
            indent=2,
        ) + "\n"
        for rel_path, content in files.items():
            path = root / rel_path
            if not path.exists():
                path.write_text(content, encoding="utf-8")
        return f"{engine.capitalize()} scaffold ready at {root}"

    def _phaser_files(self, game_title: str) -> dict[str, str]:
        return {
            "package.json": json.dumps(
                {
                    "scripts": {
                        "dev": "vite --host 0.0.0.0",
                        "build": "vite build",
                        "preview": "vite preview",
                        "test": "playwright test",
                    },
                    "dependencies": {
                        "@vitejs/plugin-basic-ssl": "^1.2.0",
                        "phaser": "^3.90.0",
                        "vite": "^6.0.0",
                    },
                    "devDependencies": {
                        "@playwright/test": "^1.50.0",
                        "eslint": "^9.0.0",
                    },
                },
                indent=2,
            )
            + "\n",
            "index.html": textwrap.dedent(
                f"""\
                <!doctype html>
                <html lang="en">
                  <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>{game_title}</title>
                  </head>
                  <body>
                    <main id="game-root" aria-label="{game_title}"></main>
                    <script type="module" src="/src/main.js"></script>
                  </body>
                </html>
                """
            ),
            "src/main.js": textwrap.dedent(
                """\
                import Phaser from 'phaser';
                import './styles/global.css';
                import BootScene from './scenes/BootScene.js';
                import GameScene from './scenes/GameScene.js';
                import UIScene from './scenes/UIScene.js';

                const config = {
                  type: Phaser.AUTO,
                  parent: 'game-root',
                  width: 1280,
                  height: 720,
                  backgroundColor: '#14151f',
                  pixelArt: false,
                  physics: {
                    default: 'arcade',
                    arcade: {
                      gravity: { y: 0 },
                      debug: false
                    }
                  },
                  scene: [BootScene, GameScene, UIScene],
                  scale: {
                    mode: Phaser.Scale.FIT,
                    autoCenter: Phaser.Scale.CENTER_BOTH
                  }
                };

                window.__GAME_STATE__ = window.__GAME_STATE__ || {};
                new Phaser.Game(config);
                """
            ),
            "src/scenes/BootScene.js": textwrap.dedent(
                """\
                export default class BootScene extends Phaser.Scene {
                  constructor() {
                    super('BootScene');
                  }

                  create() {
                    this.scene.start('GameScene');
                    this.scene.launch('UIScene');
                  }
                }
                """
            ),
            "src/scenes/GameScene.js": textwrap.dedent(
                """\
                import Player from '../objects/Player.js';
                import { createWorldBounds } from '../systems/world.js';

                export default class GameScene extends Phaser.Scene {
                  constructor() {
                    super('GameScene');
                  }

                  create() {
                    this.player = new Player(this, 640, 360);
                    createWorldBounds(this);
                    this.cameras.main.startFollow(this.player.sprite, true, 0.08, 0.08);
                  }

                  update(time, delta) {
                    this.player?.update(time, delta);
                  }
                }
                """
            ),
            "src/scenes/UIScene.js": textwrap.dedent(
                """\
                export default class UIScene extends Phaser.Scene {
                  constructor() {
                    super('UIScene');
                  }

                  create() {
                    this.add.text(24, 20, 'HP 100  |  Score 0', {
                      fontFamily: 'Inter, system-ui, sans-serif',
                      fontSize: '20px',
                      color: '#f5f7fb'
                    }).setScrollFactor(0);
                  }
                }
                """
            ),
            "src/objects/Player.js": textwrap.dedent(
                """\
                export default class Player {
                  constructor(scene, x, y) {
                    this.scene = scene;
                    this.speed = 260;
                    this.sprite = scene.add.rectangle(x, y, 34, 42, 0x6ee7b7);
                    scene.physics.add.existing(this.sprite);
                    this.sprite.body.setCollideWorldBounds(true);
                    this.cursors = scene.input.keyboard.createCursorKeys();
                    this.keys = scene.input.keyboard.addKeys('W,A,S,D,SPACE');
                  }

                  update() {
                    const body = this.sprite.body;
                    const left = this.cursors.left.isDown || this.keys.A.isDown;
                    const right = this.cursors.right.isDown || this.keys.D.isDown;
                    const up = this.cursors.up.isDown || this.keys.W.isDown;
                    const down = this.cursors.down.isDown || this.keys.S.isDown;

                    body.setVelocity(0);
                    if (left) body.setVelocityX(-this.speed);
                    if (right) body.setVelocityX(this.speed);
                    if (up) body.setVelocityY(-this.speed);
                    if (down) body.setVelocityY(this.speed);
                    body.velocity.normalize().scale(this.speed);
                  }
                }
                """
            ),
            "src/systems/world.js": textwrap.dedent(
                """\
                export function createWorldBounds(scene) {
                  scene.physics.world.setBounds(0, 0, 2400, 1600);
                  scene.add.grid(1200, 800, 2400, 1600, 80, 80, 0x24283b, 0.32, 0x3b4261, 0.4);
                }
                """
            ),
            "src/styles/global.css": textwrap.dedent(
                """\
                html, body, #game-root {
                  margin: 0;
                  width: 100%;
                  height: 100%;
                  overflow: hidden;
                  background: #0e1018;
                  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                }

                canvas {
                  display: block;
                }
                """
            ),
            "tests/smoke.spec.js": textwrap.dedent(
                """\
                import { test, expect } from '@playwright/test';

                test('game boots and canvas renders', async ({ page }) => {
                  await page.goto('/');
                  const canvas = page.locator('canvas');
                  await expect(canvas).toBeVisible();
                  await page.keyboard.press('KeyD');
                  await page.waitForTimeout(250);
                });
                """
            ),
            "playwright.config.js": textwrap.dedent(
                """\
                export default {
                  testDir: './tests',
                  webServer: {
                    command: 'npm run dev',
                    url: 'http://127.0.0.1:5173',
                    reuseExistingServer: !process.env.CI
                  },
                  use: {
                    baseURL: 'http://127.0.0.1:5173'
                  }
                };
                """
            ),
        }

    def _three_files(self, game_title: str) -> dict[str, str]:
        return {
            "package.json": json.dumps(
                {
                    "scripts": {
                        "dev": "vite --host 0.0.0.0",
                        "build": "vite build",
                        "preview": "vite preview",
                        "test": "playwright test",
                    },
                    "dependencies": {
                        "three": "^0.170.0",
                        "vite": "^6.0.0",
                    },
                    "devDependencies": {
                        "@playwright/test": "^1.50.0",
                        "eslint": "^9.0.0",
                    },
                },
                indent=2,
            )
            + "\n",
            "index.html": textwrap.dedent(
                f"""\
                <!doctype html>
                <html lang="en">
                  <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>{game_title}</title>
                  </head>
                  <body>
                    <main id="game-root" aria-label="{game_title}"></main>
                    <script type="module" src="/src/main.js"></script>
                  </body>
                </html>
                """
            ),
            "src/main.js": textwrap.dedent(
                """\
                import { GameApp } from './systems/GameApp.js';
                import './styles/global.css';

                window.__GAME_STATE__ = window.__GAME_STATE__ || {};
                const app = new GameApp(document.querySelector('#game-root'));
                app.start();
                """
            ),
            "src/systems/GameApp.js": textwrap.dedent(
                """\
                import * as THREE from 'three';
                import PlayerController from '../objects/PlayerController.js';
                import { createArena } from '../scenes/ArenaScene.js';
                import { createHud } from '../ui/hud.js';

                export class GameApp {
                  constructor(root) {
                    this.root = root;
                    this.clock = new THREE.Clock();
                    this.scene = new THREE.Scene();
                    this.scene.background = new THREE.Color(0x11131c);
                    this.camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
                    this.camera.position.set(0, 7, 10);
                    this.renderer = new THREE.WebGLRenderer({ antialias: true });
                    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                    this.root.appendChild(this.renderer.domElement);
                    this.world = createArena(this.scene);
                    this.player = new PlayerController(this.scene);
                    this.hud = createHud();
                    this.root.appendChild(this.hud);
                    window.addEventListener('resize', () => this.resize());
                    this.resize();
                  }

                  start() {
                    this.renderer.setAnimationLoop(() => this.update());
                  }

                  update() {
                    const delta = Math.min(this.clock.getDelta(), 0.05);
                    this.player.update(delta, this.world.bounds);
                    const target = this.player.mesh.position;
                    this.camera.position.lerp(new THREE.Vector3(target.x, 7, target.z + 10), 0.08);
                    this.camera.lookAt(target.x, 0, target.z);
                    this.renderer.render(this.scene, this.camera);
                  }

                  resize() {
                    const width = window.innerWidth;
                    const height = window.innerHeight;
                    this.camera.aspect = width / height;
                    this.camera.updateProjectionMatrix();
                    this.renderer.setSize(width, height);
                  }
                }
                """
            ),
            "src/scenes/ArenaScene.js": textwrap.dedent(
                """\
                import * as THREE from 'three';

                export function createArena(scene) {
                  const bounds = { minX: -12, maxX: 12, minZ: -12, maxZ: 12 };
                  const floor = new THREE.Mesh(
                    new THREE.PlaneGeometry(28, 28, 28, 28),
                    new THREE.MeshStandardMaterial({ color: 0x202436, roughness: 0.82 })
                  );
                  floor.rotation.x = -Math.PI / 2;
                  scene.add(floor);

                  const grid = new THREE.GridHelper(28, 28, 0x7dd3fc, 0x3b4261);
                  grid.position.y = 0.01;
                  scene.add(grid);

                  const ambient = new THREE.HemisphereLight(0xbfd7ff, 0x161720, 1.5);
                  scene.add(ambient);
                  const key = new THREE.DirectionalLight(0xffffff, 2.5);
                  key.position.set(5, 10, 7);
                  scene.add(key);

                  return { bounds };
                }
                """
            ),
            "src/objects/PlayerController.js": textwrap.dedent(
                """\
                import * as THREE from 'three';
                import { KeyboardInput } from '../systems/input.js';

                export default class PlayerController {
                  constructor(scene) {
                    this.speed = 7;
                    this.input = new KeyboardInput();
                    this.mesh = new THREE.Mesh(
                      new THREE.BoxGeometry(1, 1.4, 1),
                      new THREE.MeshStandardMaterial({ color: 0x6ee7b7, roughness: 0.35 })
                    );
                    this.mesh.position.y = 0.7;
                    scene.add(this.mesh);
                  }

                  update(delta, bounds) {
                    const direction = this.input.direction();
                    this.mesh.position.x += direction.x * this.speed * delta;
                    this.mesh.position.z += direction.z * this.speed * delta;
                    this.mesh.position.x = THREE.MathUtils.clamp(this.mesh.position.x, bounds.minX, bounds.maxX);
                    this.mesh.position.z = THREE.MathUtils.clamp(this.mesh.position.z, bounds.minZ, bounds.maxZ);
                    if (direction.lengthSq() > 0) {
                      this.mesh.rotation.y = Math.atan2(direction.x, direction.z);
                    }
                  }
                }
                """
            ),
            "src/systems/input.js": textwrap.dedent(
                """\
                import * as THREE from 'three';

                export class KeyboardInput {
                  constructor() {
                    this.keys = new Set();
                    window.addEventListener('keydown', (event) => this.keys.add(event.code));
                    window.addEventListener('keyup', (event) => this.keys.delete(event.code));
                  }

                  direction() {
                    const vector = new THREE.Vector3();
                    if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) vector.x -= 1;
                    if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) vector.x += 1;
                    if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) vector.z -= 1;
                    if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) vector.z += 1;
                    return vector.lengthSq() > 0 ? vector.normalize() : vector;
                  }
                }
                """
            ),
            "src/ui/hud.js": textwrap.dedent(
                """\
                export function createHud() {
                  const hud = document.createElement('section');
                  hud.className = 'hud';
                  hud.textContent = 'HP 100 | Energy 100 | WASD / Arrows';
                  return hud;
                }
                """
            ),
            "src/styles/global.css": textwrap.dedent(
                """\
                html, body, #game-root {
                  margin: 0;
                  width: 100%;
                  height: 100%;
                  overflow: hidden;
                  background: #0e1018;
                  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                }

                canvas {
                  display: block;
                }

                .hud {
                  position: fixed;
                  top: 16px;
                  left: 16px;
                  padding: 10px 12px;
                  color: #f5f7fb;
                  background: rgba(9, 11, 18, 0.72);
                  border: 1px solid rgba(255, 255, 255, 0.12);
                  font-size: 15px;
                }
                """
            ),
            "tests/smoke.spec.js": textwrap.dedent(
                """\
                import { test, expect } from '@playwright/test';

                test('3D game boots, canvas renders, and keyboard input is accepted', async ({ page }) => {
                  await page.goto('/');
                  const canvas = page.locator('canvas');
                  await expect(canvas).toBeVisible();
                  await page.keyboard.down('KeyW');
                  await page.waitForTimeout(400);
                  await page.keyboard.up('KeyW');
                });
                """
            ),
            "playwright.config.js": textwrap.dedent(
                """\
                export default {
                  testDir: './tests',
                  webServer: {
                    command: 'npm run dev',
                    url: 'http://127.0.0.1:5173',
                    reuseExistingServer: !process.env.CI
                  },
                  use: {
                    baseURL: 'http://127.0.0.1:5173'
                  }
                };
                """
            ),
        }


class WriteFileInput(BaseModel):
    relative_path: str = Field(..., description="Relative file path inside the game project.")
    content: str = Field(..., description="Complete file content to write.")


class WriteGameFileTool(BaseTool):
    name: str = "write_game_file"
    description: str = (
        "Write a complete source file inside the active generated game project. Use this "
        "for modular files in src/scenes, src/objects, src/systems, src/ui, src/data, "
        "src/styles, tests, or docs."
    )
    args_schema: Type[BaseModel] = WriteFileInput
    project_root: str

    def _run(self, relative_path: str, content: str) -> str:
        root = Path(self.project_root).expanduser().resolve()
        path = root / normalize_relative_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {path.relative_to(root)} ({len(content)} bytes)"


class ReadFileInput(BaseModel):
    relative_path: str = Field(..., description="Relative file path inside the game project.")


class ReadGameFileTool(BaseTool):
    name: str = "read_game_file"
    description: str = "Read a file inside the active generated game project."
    args_schema: Type[BaseModel] = ReadFileInput
    project_root: str

    def _run(self, relative_path: str) -> str:
        root = Path(self.project_root).expanduser().resolve()
        path = root / normalize_relative_path(relative_path)
        if not path.exists():
            return f"Missing file: {path.relative_to(root)}"
        return path.read_text(encoding="utf-8")


class ListProjectInput(BaseModel):
    subdir: str = Field(".", description="Relative subdirectory to list.")


class ListProjectTool(BaseTool):
    name: str = "list_project_files"
    description: str = "List the current generated game project files."
    args_schema: Type[BaseModel] = ListProjectInput
    project_root: str

    def _run(self, subdir: str = ".") -> str:
        root = Path(self.project_root).expanduser().resolve()
        base = root / normalize_relative_path(subdir)
        if not base.exists():
            return f"Missing directory: {subdir}"
        files = sorted(
            str(path.relative_to(root))
            for path in base.rglob("*")
            if path.is_file() and "node_modules" not in path.parts and "dist" not in path.parts
        )
        return "\n".join(files) or "No files found."


class UpdateMemoryInput(BaseModel):
    key: str = Field(..., description="Top-level memory key to update.")
    value_json: str = Field(..., description="JSON-encoded value for this key.")


class UpdateGlobalMemoryTool(BaseTool):
    name: str = "update_global_memory"
    description: str = (
        "Update docs/global-memory.json with durable module decisions, variable names, "
        "scene names, entity contracts, risks, and completed milestones."
    )
    args_schema: Type[BaseModel] = UpdateMemoryInput
    project_root: str

    def _run(self, key: str, value_json: str) -> str:
        root = Path(self.project_root).expanduser().resolve()
        memory_path = root / "docs" / "global-memory.json"
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory: dict[str, Any] = {}
        if memory_path.exists():
            memory = json.loads(memory_path.read_text(encoding="utf-8"))
        try:
            value = json.loads(value_json)
        except json.JSONDecodeError:
            value = value_json
        memory[key] = value
        memory["updatedAt"] = datetime.now(timezone.utc).isoformat()
        memory_path.write_text(json.dumps(memory, indent=2) + "\n", encoding="utf-8")
        return f"Updated global memory key: {key}"


class CommandInput(BaseModel):
    command_json: str = Field(
        ...,
        description='JSON array command, e.g. ["npm", "run", "build"]. Only safe npm commands are allowed.',
    )


class SafeCommandTool(BaseTool):
    name: str = "run_safe_project_command"
    description: str = (
        "Run a whitelisted project command for validation: npm install, npm run build, "
        "npm run test, or npm test."
    )
    args_schema: Type[BaseModel] = CommandInput
    project_root: str

    def _run(self, command_json: str) -> str:
        try:
            command = json.loads(command_json)
        except json.JSONDecodeError as exc:
            return f"Invalid command JSON: {exc}"
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            return "Command must be a JSON array of strings."
        if tuple(command[:3]) not in SAFE_COMMANDS and tuple(command[:2]) not in SAFE_COMMANDS:
            return f"Command not allowed: {command}"
        process = subprocess.run(
            command,
            cwd=self.project_root,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        return "\n".join(
            [
                f"exit_code={process.returncode}",
                "--- stdout ---",
                process.stdout[-6000:],
                "--- stderr ---",
                process.stderr[-6000:],
            ]
        )


def create_agents(llm: str | None = None) -> dict[str, Agent]:
    common = {"verbose": True}
    if llm:
        common["llm"] = llm

    manager = Agent(
        role="Modular Project Orchestrator & Router",
        goal=(
            "Break down massive, large-scale game concepts into small, modular milestones "
            "(e.g., Engine, Physics, UI, Save System). Manage the flow, route tasks "
            "dynamically, and maintain a shared global memory state so no features or "
            "variables are lost across iterations."
        ),
        backstory=(
            "You are the ultimate tech lead. You never write code all at once; you divide "
            "a giant vision into bulletproof components and orchestrate the team to build "
            "them iteratively."
        ),
        allow_delegation=True,
        **common,
    )
    designer = Agent(
        role="UI/UX & Visual Theme Architect",
        goal=(
            "Define the art style, color palettes, screen layouts, camera effects (shake, "
            "flash), and structural UI placements. Provide visual design specifications "
            "and placeholder guidelines for every game module."
        ),
        backstory=(
            'You are a creative genius who understands "Game Feel" and "Juice". You '
            "ensure that even with basic shapes or assets, the game looks polished, "
            "professional, and visually engaging."
        ),
        allow_delegation=False,
        **common,
    )
    builder = Agent(
        role="Senior Phaser.js & Core Programmer",
        goal=(
            "Write high-quality, clean, and modular HTML5/Phaser.js code based on the "
            "technical specifications provided by the Manager and Designer. Focus on one "
            "module at a time."
        ),
        backstory=(
            "You are a legendary game programmer. You write highly optimized, scalable, "
            "and beautifully commented code, keeping architecture separated into clean "
            "components and scenes."
        ),
        allow_delegation=False,
        **common,
    )
    player = Agent(
        role="Autonomous Playtester & Simulator",
        goal=(
            "Simulate 30-second gameplay sessions using automated scripting concepts "
            "(like Playwright). Simulate keyboard inputs (WASD, Arrows, Space) to test "
            "player movement, boundaries, collision detection, and mechanics."
        ),
        backstory=(
            "You are a professional QA tester. Your job is to try and break the game by "
            "testing edge cases, walking into walls, and ensuring mechanics trigger perfectly."
        ),
        allow_delegation=False,
        **common,
    )
    debugger = Agent(
        role="Runtime Console Auditing & Bug Fixer",
        goal=(
            "Actively monitor the simulated outputs, catch syntax errors, logic flaws, and "
            "runtime console logs. Analyze exactly where the code broke and output precise, "
            "working code corrections back to the Builder."
        ),
        backstory=(
            "You have eagle eyes for bugs. You don't just find mistakes; you pinpoint the "
            "exact line in the Update loop or Event listener and solve it instantly."
        ),
        allow_delegation=False,
        **common,
    )
    summariser = Agent(
        role="Game Feel Critic & Feedback Compiler",
        goal=(
            'Review the final state of each built module. Compile full progress reports, '
            'analyze the "Vibe" and "Juice", suggest macro-level improvements, and present '
            "the final structured code files neatly organized in folders to the User."
        ),
        backstory=(
            "You are a senior game critic and data aggregator. You turn chaotic development "
            "logs into beautiful, structured summaries and decide when a module is 100% "
            "complete and ready."
        ),
        allow_delegation=False,
        **common,
    )
    return {
        "manager": manager,
        "designer": designer,
        "builder": builder,
        "player": player,
        "debugger": debugger,
        "summariser": summariser,
    }


def create_tasks(
    agents: dict[str, Agent],
    game_description: str,
    game_title: str,
    game_slug: str,
    engine: str,
    milestone: str,
    project_root: Path,
    milestone_number: int,
    milestone_total: int,
) -> list[Task]:
    project_tools = [
        ReadGameFileTool(project_root=str(project_root)),
        WriteGameFileTool(project_root=str(project_root)),
        ListProjectTool(project_root=str(project_root)),
        UpdateGlobalMemoryTool(project_root=str(project_root)),
    ]
    validation_tools = project_tools + [SafeCommandTool(project_root=str(project_root))]
    context = textwrap.dedent(
        f"""\
        Game title: {game_title}
        Game slug: {game_slug}
        Engine target: {engine}
        Project root: {project_root}
        Massive game description:
        {game_description}

        Current milestone {milestone_number}/{milestone_total}: {milestone}

        Non-negotiable output architecture:
        - Keep files modular.
        - Prefer src/scenes, src/objects, src/systems, src/ui, src/data, src/styles, tests, docs.
        - Maintain docs/global-memory.json with scene names, system contracts, variables, risks, and completed milestone notes.
        - Do not collapse the project into one giant file.
        - If engine target is "phaser", use Phaser 3, ES modules, Arcade Physics, and Vite-compatible browser code.
        - If engine target is "three", use Three.js, ES modules, WebGLRenderer, modular scene/object/system files, and Vite-compatible browser code.
        - For 3D games, keep the primary scene full-screen, ensure the camera is controllable/following, include lighting, and avoid blank canvas states.
        """
    )
    return [
        Task(
            description=context
            + "\nManager: define the exact implementation scope and acceptance criteria for this milestone. "
            "Route the work to the right specialists and make sure the global memory contract is honored.",
            expected_output="A milestone implementation brief with acceptance criteria and module boundaries.",
            agent=agents["manager"],
        ),
        Task(
            description=context
            + "\nDesigner: produce concrete visual, UI, camera, and juice specs for only this milestone. "
            "Include color usage, layout placement, placeholder asset guidance, and any game-feel effects.",
            expected_output="A concise design spec that Builder can implement immediately.",
            agent=agents["designer"],
        ),
        Task(
            description=context
            + "\nBuilder: implement this milestone in the project folder using the filesystem tools. "
            "Read existing files first, update or add modular files, and preserve compatibility with prior milestones.",
            expected_output="A list of files written plus a short explanation of implemented systems.",
            agent=agents["builder"],
            tools=project_tools,
        ),
        Task(
            description=context
            + "\nPlayer: create or refine Playwright-style smoke tests for a 30-second automated session. "
            "Cover WASD, arrows, Space, boundary pushing, collision checks, and mechanic triggers relevant to this milestone.",
            expected_output="Automated playtest coverage notes and any test files written.",
            agent=agents["player"],
            tools=project_tools,
        ),
        Task(
            description=context
            + "\nDebugger: inspect the code, run safe validation commands when useful, identify runtime or syntax issues, "
            "and write exact corrections back into the project files.",
            expected_output="Bug audit with precise fixes applied, or confirmation that validation passed.",
            agent=agents["debugger"],
            tools=validation_tools,
        ),
        Task(
            description=context
            + "\nSummariser: review the finished milestone, update global memory, and write a milestone report under docs/. "
            "Judge whether the module is complete, and document remaining macro improvements without derailing the current build.",
            expected_output="Structured milestone report, file tree summary, completion status, and Vibe/Juice critique.",
            agent=agents["summariser"],
            tools=project_tools,
        ),
    ]


def create_crew(
    agents: dict[str, Agent],
    tasks: list[Task],
    manager_llm: str | None,
    planning: bool = True,
    max_rpm: int | None = None,
) -> Crew:
    crew_kwargs: dict[str, Any] = {
        "agents": [
            agents["designer"],
            agents["builder"],
            agents["player"],
            agents["debugger"],
            agents["summariser"],
        ],
        "tasks": tasks,
        "manager_agent": agents["manager"],
        "process": Process.hierarchical,
        "memory": True,
        "planning": planning,
        "verbose": True,
        "output_log_file": "massive_game_studio_logs.json",
    }
    if max_rpm:
        crew_kwargs["max_rpm"] = max_rpm
    if manager_llm:
        crew_kwargs["manager_llm"] = manager_llm
        if planning:
            crew_kwargs["planning_llm"] = manager_llm
    return Crew(**crew_kwargs)


def is_quota_error(error: Exception) -> bool:
    text = str(error).lower()
    return "429" in text and ("quota" in text or "resource_exhausted" in text or "rate" in text)


def uses_local_or_custom_model(*models: str | None) -> bool:
    local_prefixes = ("ollama/", "lm_studio/", "openrouter/", "azure/", "bedrock/", "vertex_ai/")
    return any(model and model.startswith(local_prefixes) for model in models)


def resolve_default_models(args: argparse.Namespace) -> tuple[str | None, str | None]:
    worker_model = args.worker_model or os.getenv("CREWAI_WORKER_MODEL")
    manager_model = args.manager_model or os.getenv("CREWAI_MANAGER_MODEL")

    if not worker_model and not manager_model and os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        worker_model = DEFAULT_GEMINI_MODEL
        manager_model = DEFAULT_GEMINI_MODEL

    return worker_model, manager_model or worker_model


def ensure_environment(worker_model: str | None = None, manager_model: str | None = None) -> None:
    if load_dotenv:
        load_dotenv()
    if sys.version_info < (3, 10):
        raise SystemExit("CrewAI requires Python >=3.10. Please run this with Python 3.10 or newer.")
    has_common_key = any(
        os.getenv(name)
        for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "AZURE_API_KEY")
    )
    if not has_common_key and not uses_local_or_custom_model(worker_model, manager_model):
        raise SystemExit(
            "No common LLM API key was found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, "
            "GEMINI_API_KEY, or pass a configured local/custom model such as "
            "--worker-model ollama/llama3.1 --manager-model ollama/llama3.1."
        )


def prompt_multiline() -> str:
    print("\nDescribe the massive game you want the swarm to build.")
    print("Press Enter twice when finished.\n")
    lines: list[str] = []
    while True:
        line = input("> ")
        if not line and lines:
            break
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def extract_prompt_cli_overrides(raw_description: str) -> tuple[str, dict[str, str]]:
    """Recover gracefully when CLI flags are pasted into the interactive prompt."""
    text = raw_description.strip()
    if not text.startswith("--"):
        return text, {}

    try:
        tokens = shlex.split(text)
    except ValueError:
        return text, {}

    overrides: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {"--description", "--title", "--slug", "--engine"} and index + 1 < len(tokens):
            overrides[token[2:]] = tokens[index + 1]
            index += 2
            continue
        index += 1

    return overrides.get("description", text), overrides


def select_milestones(limit: int | None) -> list[str]:
    if limit is None or limit <= 0:
        return DEFAULT_MILESTONES
    return DEFAULT_MILESTONES[: min(limit, len(DEFAULT_MILESTONES))]


def build_game(args: argparse.Namespace) -> None:
    worker_llm, manager_llm = resolve_default_models(args)
    ensure_environment(worker_model=worker_llm, manager_model=manager_llm)
    raw_description = args.description or prompt_multiline()
    game_description, prompt_overrides = extract_prompt_cli_overrides(raw_description)
    if not game_description:
        raise SystemExit("No game description provided.")

    engine = (prompt_overrides.get("engine") or args.engine or "phaser").strip().lower()
    if engine not in {"phaser", "three"}:
        raise SystemExit("--engine must be either 'phaser' or 'three'.")

    first_line = game_description.splitlines()[0]
    game_title = args.title or prompt_overrides.get("title") or first_line[:80].strip().title()
    game_slug = slugify(args.slug or prompt_overrides.get("slug") or game_title)
    output_root = Path(args.output_dir).expanduser().resolve()
    project_root = output_root / game_slug
    output_root.mkdir(parents=True, exist_ok=True)

    scaffold_tool = ScaffoldProjectTool(output_root=str(output_root))
    print(scaffold_tool._run(game_title=game_title, game_slug=game_slug, engine=engine))

    agents = create_agents(llm=worker_llm)
    milestones = select_milestones(args.milestones)

    print(f"\nStarting hierarchical CrewAI swarm for {len(milestones)} milestone(s).")
    print(f"Project root: {project_root}\n")

    for index, milestone in enumerate(milestones, start=1):
        print(f"\n=== Milestone {index}/{len(milestones)}: {milestone} ===\n")
        tasks = create_tasks(
            agents=agents,
            game_description=game_description,
            game_title=game_title,
            game_slug=game_slug,
            engine=engine,
            milestone=milestone,
            project_root=project_root,
            milestone_number=index,
            milestone_total=len(milestones),
        )
        crew = create_crew(
            agents=agents,
            tasks=tasks,
            manager_llm=manager_llm,
            planning=not args.no_planning,
            max_rpm=args.max_rpm,
        )
        try:
            result = crew.kickoff(
                inputs={
                    "game_description": game_description,
                    "game_title": game_title,
                    "game_slug": game_slug,
                    "engine": engine,
                    "milestone": milestone,
                    "project_root": str(project_root),
                }
            )
        except Exception as exc:
            if is_quota_error(exc):
                raise SystemExit(
                    "\nGemini returned a 429 quota/rate-limit error. This is an account/project quota issue, "
                    "not a Python bug.\n"
                    "Fix options:\n"
                    "  1. Open https://ai.dev/rate-limit and confirm this API key's Google AI Studio project has quota.\n"
                    "  2. Enable/link billing for the project, or create a new API key under a project with Gemini quota.\n"
                    "  3. Retry with a lighter model and fewer calls:\n"
                    "     python massive_game_studio.py --engine phaser --milestones 1 --no-planning --max-rpm 2 "
                    "--worker-model gemini/gemini-2.5-flash --manager-model gemini/gemini-2.5-flash ...\n"
                    "  4. Wait if the dashboard shows temporary per-minute limits, then retry.\n"
                ) from exc
            raise
        print("\nMilestone result:")
        print(str(result))

    print("\nSwarm run complete.")
    print(f"Generated project: {project_root}")
    print("Next local commands:")
    print(f"  cd {project_root}")
    print("  npm install")
    print("  npm run dev")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CrewAI multi-agent swarm for building modular Phaser 2D or Three.js 3D games from scratch."
    )
    parser.add_argument("--description", help="Massive game concept. If omitted, opens an interactive prompt.")
    parser.add_argument("--title", help="Human-readable game title.")
    parser.add_argument("--slug", help="Filesystem-safe project slug.")
    parser.add_argument(
        "--engine",
        choices=["phaser", "three"],
        default="phaser",
        help="Game engine: phaser for 2D games, three for 3D games.",
    )
    parser.add_argument("--output-dir", default="./generated_games", help="Root folder for generated games.")
    parser.add_argument("--milestones", type=int, default=len(DEFAULT_MILESTONES), help="Number of milestones to run.")
    parser.add_argument("--manager-model", help="CrewAI manager/planning model name.")
    parser.add_argument("--worker-model", help="CrewAI worker model name.")
    parser.add_argument("--max-rpm", type=int, help="Optional maximum LLM requests per minute for CrewAI.")
    parser.add_argument("--no-planning", action="store_true", help="Disable CrewAI planning to reduce LLM calls.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    build_game(parse_args())
