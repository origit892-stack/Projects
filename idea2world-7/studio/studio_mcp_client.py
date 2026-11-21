"""MCP client for Roblox Studio (stdio JSON-RPC 2.0).

Studio ships an MCP server that speaks JSON-RPC over stdio. This client:
  * discovers the binary (env override, macOS app bundle, PATH);
  * performs the MCP handshake and lists the tools Studio actually exposes;
  * maps Idea2World operations onto whichever tool names exist (aliases, not assumptions);
  * never claims a capability it did not see in `tools/list`.

If Studio is closed or the server is not enabled, `connect()` returns a clear diagnostic instead of
pretending the map was built.
"""
from __future__ import annotations

import json
import os
import select
import shutil
import subprocess
import time
from pathlib import Path

PROTOCOL_VERSION = "2024-11-05"

BINARY_CANDIDATES = [
    "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP",
    "/Applications/Roblox Studio.app/Contents/MacOS/StudioMCP",
    str(Path.home() / "Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"),
    "/Applications/RobloxStudio.app/Contents/MacOS/studio-mcp",
    "StudioMCP",
    "roblox-studio-mcp",
]

TOOL_ALIASES = {
    "execute_luau": ["execute_luau", "executeLuau", "run_luau", "execute_script"],
    "get_console_output": ["get_console_output", "getConsoleOutput", "read_console", "console_output"],
    "screen_capture": ["screen_capture", "capture_screen", "screenshot", "capture_viewport"],
    "start_stop_play": ["start_stop_play", "start_play", "play", "stop_play", "toggle_play"],
    "search_game_tree": ["search_game_tree", "search_instances", "find_instances", "get_tree"],
    "inspect_instance": ["inspect_instance", "get_instance", "inspect"],
    "generate_mesh": ["generate_mesh", "generateMesh", "create_mesh"],
    "generate_material": ["generate_material", "generateMaterial", "create_material"],
    "generate_procedural_model": ["generate_procedural_model", "generateProceduralModel"],
    "search_asset": ["search_asset", "searchAsset", "find_asset"],
    "insert_asset": ["insert_asset", "insertAsset", "import_asset"],
    "read_script": ["read_script", "get_script_source", "readScript"],
    "edit_script": ["edit_script", "set_script_source", "editScript"],
}


class StudioMCPError(RuntimeError):
    pass


def discover_binary() -> str | None:
    explicit = os.environ.get("IDEA2WORLD_STUDIO_MCP", "").strip()
    if explicit:
        return explicit if Path(explicit).exists() or shutil.which(explicit) else explicit
    for candidate in BINARY_CANDIDATES:
        if os.path.sep in candidate:
            if Path(candidate).exists():
                return candidate
        else:
            found = shutil.which(candidate)
            if found:
                return found
    return None


class StudioMCPClient:
    def __init__(self, binary: str | None = None, timeout: float = 120.0, startup_timeout: float = 60.0):
        self.binary = binary or discover_binary()
        self.timeout = timeout
        self.startup_timeout = startup_timeout
        self.process: subprocess.Popen | None = None
        self.next_id = 1
        self.tools: list[dict] = []
        self.tool_map: dict[str, str] = {}
        self.server_info: dict = {}
        self.last_error = ""
        self._buffer = b""

    # -- lifecycle --------------------------------------------------------------------
    @property
    def connected(self) -> bool:
        return bool(self.process and self.process.poll() is None)

    def start(self) -> "StudioMCPClient":
        if self.connected:
            return self
        if not self.binary:
            raise StudioMCPError(
                "Roblox Studio MCP binary not found. In Studio open Assistant -> Manage MCP Servers -> "
                "Enable Studio as MCP server, then set IDEA2WORLD_STUDIO_MCP to the StudioMCP path.")
        if os.path.sep in self.binary and not Path(self.binary).exists():
            raise StudioMCPError(f"Studio MCP binary not found at {self.binary}")
        try:
            self.process = subprocess.Popen(
                [self.binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, bufsize=0)
        except OSError as exc:
            raise StudioMCPError(f"could not launch Studio MCP ({self.binary}): {exc}") from exc
        try:
            self._handshake()
        except Exception:
            self.stop()
            raise
        return self

    def _handshake(self) -> None:
        result = self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"roots": {"listChanged": False}, "sampling": {}},
            "clientInfo": {"name": "idea2world", "version": "6.0.0"},
        }, timeout=self.startup_timeout)
        self.server_info = (result or {}).get("serverInfo", {}) or {}
        self.notify("notifications/initialized", {})
        self.refresh_tools()

    def stop(self) -> None:
        if not self.process:
            return
        try:
            if self.process.stdin:
                self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            try:
                self.process.kill()
            except OSError:
                pass
        self.process = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *_exc):
        self.stop()

    # -- transport --------------------------------------------------------------------
    def _send(self, message: dict) -> None:
        if not self.process or not self.process.stdin:
            raise StudioMCPError("Studio MCP process is not running")
        payload = json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"
        self.process.stdin.write(payload)
        self.process.stdin.flush()

    def notify(self, method: str, params: dict) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _read_message(self, deadline: float) -> dict:
        if not self.process or not self.process.stdout:
            raise StudioMCPError("Studio MCP stdout is unavailable")
        fd = self.process.stdout.fileno()
        while True:
            line, consumed = self._extract_message()
            if line is not None:
                self._buffer = self._buffer[consumed:]
                return line
            remaining = deadline - time.time()
            if remaining <= 0:
                raise StudioMCPError("timed out waiting for Studio MCP response")
            ready, _, _ = select.select([fd], [], [], min(remaining, 1.0))
            if not ready:
                if self.process.poll() is not None:
                    stderr = self.process.stderr.read().decode("utf-8", "replace")[:800] if self.process.stderr else ""
                    raise StudioMCPError(f"Studio MCP exited unexpectedly. {stderr}")
                continue
            chunk = os.read(fd, 65536)
            if not chunk:
                raise StudioMCPError("Studio MCP closed the connection")
            self._buffer += chunk

    def _extract_message(self) -> tuple[dict | None, int]:
        if not self._buffer:
            return None, 0
        if self._buffer.lstrip()[:1] == b"C":
            header_end = self._buffer.find(b"\r\n\r\n")
            separator = 4
            if header_end == -1:
                header_end = self._buffer.find(b"\n\n")
                separator = 2
            if header_end == -1:
                return None, 0
            header = self._buffer[:header_end].decode("ascii", "replace")
            length = 0
            for line in header.splitlines():
                if line.lower().startswith("content-length:"):
                    length = int(line.split(":", 1)[1].strip() or 0)
            start = header_end + separator
            if length <= 0:
                self._buffer = b""
                return None, 0
            if len(self._buffer) < start + length:
                return None, 0
            chunk = self._buffer[start:start + length]
            try:
                return json.loads(chunk.decode("utf-8")), start + length
            except json.JSONDecodeError:
                self._buffer = b""
                return None, 0
        newline = self._buffer.find(b"\n")
        if newline == -1:
            return None, 0
        raw = self._buffer[:newline].strip()
        if not raw:
            return None, newline + 1
        try:
            return json.loads(raw.decode("utf-8")), newline + 1
        except json.JSONDecodeError:
            return None, newline + 1

    def request(self, method: str, params: dict | None = None, timeout: float | None = None) -> dict:
        if not self.process:
            raise StudioMCPError("Studio MCP process is not running")
        request_id = self.next_id
        self.next_id += 1
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}})
        deadline = time.time() + (timeout if timeout is not None else self.timeout)
        while True:
            message = self._read_message(deadline)
            if message.get("id") == request_id:
                if "error" in message:
                    error = message["error"] or {}
                    raise StudioMCPError(f"{method} failed: {error.get('message', error)}")
                return message.get("result", {}) or {}
            # Server-initiated request: answer politely so the server does not stall.
            if message.get("method") and message.get("id") is not None:
                self._send({"jsonrpc": "2.0", "id": message["id"],
                            "result": {"capabilities": {}}})

    # -- tools ------------------------------------------------------------------------
    def refresh_tools(self) -> list[dict]:
        result = self.request("tools/list", {}, timeout=self.startup_timeout)
        self.tools = result.get("tools", []) or []
        available = {tool.get("name"): tool for tool in self.tools}
        self.tool_map = {}
        for canonical, aliases in TOOL_ALIASES.items():
            for alias in aliases:
                if alias in available:
                    self.tool_map[canonical] = alias
                    break
            else:
                lowered = {name.lower(): name for name in available if isinstance(name, str)}
                for alias in aliases:
                    if alias.lower() in lowered:
                        self.tool_map[canonical] = lowered[alias.lower()]
                        break
        return self.tools

    def has(self, canonical: str) -> bool:
        return canonical in self.tool_map

    def call(self, canonical: str, arguments: dict | None = None) -> dict:
        if canonical not in self.tool_map:
            raise StudioMCPError(f"Studio MCP does not expose '{canonical}'. Available: "
                                 f"{', '.join(sorted(self.tool_map)) or 'none'}")
        result = self.request("tools/call", {"name": self.tool_map[canonical],
                                             "arguments": arguments or {}})
        return self._normalise(result)

    @staticmethod
    def _normalise(result: dict) -> dict:
        content = result.get("content")
        text_parts: list[str] = []
        images: list[str] = []
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text":
                    text_parts.append(str(item.get("text", "")))
                elif item.get("type") == "image":
                    images.append(item.get("data", ""))
        combined = "\n".join(text_parts).strip()
        parsed = None
        if combined:
            try:
                parsed = json.loads(combined)
            except json.JSONDecodeError:
                parsed = None
        return {"text": combined, "json": parsed, "images": images,
                "isError": bool(result.get("isError")), "raw": result}

    # -- convenience ------------------------------------------------------------------
    def tool_schema(self, canonical: str) -> dict:
        name = self.tool_map.get(canonical)
        tool = next((t for t in self.tools if t.get("name") == name), None)
        return (tool or {}).get("inputSchema") or {}

    def _arguments(self, canonical: str, arguments: dict) -> dict:
        """Fill required schema fields Studio insists on (e.g. datamodel_type) with sane defaults."""
        schema = self.tool_schema(canonical)
        required = schema.get("required") or []
        defaults = {"datamodel_type": os.environ.get("IDEA2WORLD_DATAMODEL", "Edit"),
                    "datamodel": os.environ.get("IDEA2WORLD_DATAMODEL", "Edit"),
                    "target": "Edit"}
        filled = dict(arguments)
        for key in required:
            if key not in filled and key in defaults:
                filled[key] = defaults[key]
        return filled

    def execute_luau(self, code: str, timeout: float | None = None) -> dict:
        arguments = self._arguments("execute_luau", {"code": code})
        result = self.request("tools/call", {
            "name": self.tool_map.get("execute_luau", "execute_luau"),
            "arguments": arguments,
        }, timeout=timeout or self.timeout)
        return self._normalise(result)

    def console_output(self) -> str:
        result = self.call("get_console_output")
        return result["text"]

    def capture(self, label: str = "") -> dict:
        return self.call("screen_capture", {"label": label} if label else {})

    def play(self, action: str = "start") -> dict:
        return self.call("start_stop_play", {"action": action})

    def status(self) -> dict:
        return {"available": self.connected, "binary": self.binary,
                "server": self.server_info, "tools": sorted(self.tool_map),
                "missing": sorted(set(TOOL_ALIASES) - set(self.tool_map)),
                "error": self.last_error}


def connect(prefer_mock_project: str | None = None, allow_mock: bool = False,
            force_mock: bool = False):
    """Return a live client, or a MockStudio when allowed and Studio is unavailable.

    `force_mock` is used for the "simulate" mode: it must never touch a live Studio session.
    """
    if force_mock and prefer_mock_project:
        from .mock_studio import MockStudio
        return MockStudio(prefer_mock_project).start()
    binary = discover_binary()
    error = ""
    if binary:
        client = StudioMCPClient(binary)
        try:
            client.start()
            return client
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
    else:
        error = "StudioMCP binary not found"
    if allow_mock and prefer_mock_project:
        from .mock_studio import MockStudio
        mock = MockStudio(prefer_mock_project)
        mock.last_error = error
        return mock.start()
    raise StudioMCPError(error)
