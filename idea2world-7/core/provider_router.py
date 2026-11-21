"""Provider-agnostic brain layer (OpenAI-compatible, Anthropic, Gemini).

Design rules:
  * no third-party SDKs -- stdlib `urllib` only, so the app stays pip-free;
  * every provider is optional; with none configured the pipeline still runs deterministically and
    reports `brain = "offline"` instead of pretending an LLM made the decisions;
  * structured output is requested, then *validated* by the caller. A malformed model answer never
    corrupts the WorldSpec: it falls back to the deterministic planner.
"""
from __future__ import annotations

import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "openai_compatible": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-5",
    "gemini": "gemini-2.5-flash",
}

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta",
}


class BrainUnavailable(RuntimeError):
    pass


@dataclass
class BrainResult:
    text: str
    data: dict | None = None
    provider: str = ""
    model: str = ""
    latency_ms: int = 0
    tokens: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)


@dataclass
class ProviderConfig:
    kind: str
    api_key: str
    base_url: str
    model: str
    vision_model: str = ""

    @property
    def label(self) -> str:
        return f"{self.kind}:{self.model}"


def _env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def discover_provider() -> ProviderConfig | None:
    """Find the first configured provider, honouring explicit Idea2World settings first."""
    explicit = _env("IDEA2WORLD_PROVIDER").lower()
    key = _env("IDEA2WORLD_API_KEY")
    url = _env("IDEA2WORLD_API_URL")
    model = _env("IDEA2WORLD_MODEL")
    if key and url:
        kind = explicit or ("anthropic" if "anthropic" in url else "gemini" if "generativelanguage" in url
                            else "openai_compatible")
        return ProviderConfig(kind=kind, api_key=key, base_url=url.rstrip("/"),
                              model=model or DEFAULT_MODELS.get(kind, "gpt-4o-mini"),
                              vision_model=model or DEFAULT_MODELS.get(kind, ""))
    if key and explicit:
        kind = explicit
        return ProviderConfig(kind=kind, api_key=key, base_url=_env("IDEA2WORLD_BASE_URL") or DEFAULT_BASE_URLS.get(kind, ""),
                              model=model or DEFAULT_MODELS.get(kind, ""),
                              vision_model=_env("IDEA2WORLD_VISION_MODEL") or model or DEFAULT_MODELS.get(kind, ""))
    openai_key = _env("OPENAI_API_KEY")
    if openai_key:
        is_anthropic = bool(_env("ANTHROPIC_API_KEY")) and explicit == "anthropic"
        kind = "anthropic" if is_anthropic else "openai_compatible" if _env("OPENAI_BASE_URL") else "openai"
        base = _env("OPENAI_BASE_URL") or DEFAULT_BASE_URLS[kind]
        return ProviderConfig(kind=kind, api_key=openai_key, base_url=base,
                              model=model or _env("OPENAI_MODEL") or DEFAULT_MODELS[kind],
                              vision_model=_env("OPENAI_VISION_MODEL") or model or DEFAULT_MODELS[kind])
    anthropic_key = _env("ANTHROPIC_API_KEY")
    if anthropic_key:
        return ProviderConfig(kind="anthropic", api_key=anthropic_key,
                              base_url=_env("ANTHROPIC_BASE_URL") or DEFAULT_BASE_URLS["anthropic"],
                              model=model or _env("ANTHROPIC_MODEL") or DEFAULT_MODELS["anthropic"],
                              vision_model=_env("ANTHROPIC_VISION_MODEL") or model or DEFAULT_MODELS["anthropic"])
    gemini_key = _env("GEMINI_API_KEY", "GOOGLE_API_KEY")
    if gemini_key:
        return ProviderConfig(kind="gemini", api_key=gemini_key,
                              base_url=_env("GEMINI_BASE_URL") or DEFAULT_BASE_URLS["gemini"],
                              model=model or _env("GEMINI_MODEL") or DEFAULT_MODELS["gemini"],
                              vision_model=_env("GEMINI_VISION_MODEL") or model or DEFAULT_MODELS["gemini"])
    return None


def extract_json(text: str) -> dict | None:
    """Pull a JSON object out of a model answer, tolerating fences and prose."""
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    for candidate in (cleaned,):
        try:
            data = json.loads(candidate)
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            pass
    start = cleaned.find("{")
    while start != -1:
        depth = 0
        for index in range(start, len(cleaned)):
            char = cleaned[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    chunk = cleaned[start:index + 1]
                    try:
                        data = json.loads(chunk)
                        return data if isinstance(data, dict) else None
                    except json.JSONDecodeError:
                        break
        start = cleaned.find("{", start + 1)
    return None


class ProviderRouter:
    """A single entry point for text and vision calls across providers."""

    def __init__(self, config: ProviderConfig | None = None, timeout: int = 120, retries: int = 2):
        self.config = config if config is not None else discover_provider()
        self.timeout = timeout
        self.retries = retries
        self.calls: list[dict] = []

    # -- status ----------------------------------------------------------------------
    @property
    def available(self) -> bool:
        return self.config is not None

    def describe(self) -> dict:
        if not self.config:
            return {"available": False, "provider": None, "model": None,
                    "note": "No AI provider configured. Deterministic planner is active. "
                            "Set ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY or IDEA2WORLD_API_KEY + IDEA2WORLD_API_URL."}
        return {"available": True, "provider": self.config.kind, "model": self.config.model,
                "vision_model": self.config.vision_model or self.config.model,
                "calls": len(self.calls)}

    # -- text -------------------------------------------------------------------------
    def complete(self, messages: list[dict], json_mode: bool = True, temperature: float = 0.7,
                 max_tokens: int = 2400) -> BrainResult:
        if not self.config:
            raise BrainUnavailable("no provider configured")
        started = time.time()
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                if self.config.kind == "anthropic":
                    result = self._anthropic(messages, temperature, max_tokens)
                elif self.config.kind == "gemini":
                    result = self._gemini(messages, temperature, max_tokens)
                else:
                    result = self._openai_compatible(messages, json_mode, temperature, max_tokens)
                result.latency_ms = int((time.time() - started) * 1000)
                result.provider = self.config.kind
                result.model = self.config.model
                self.calls.append({"kind": "text", "latency_ms": result.latency_ms,
                                   "tokens": result.tokens, "model": result.model})
                return result
            except Exception as exc:  # noqa: BLE001 - network errors are provider-specific
                last_error = exc
                if attempt < self.retries:
                    time.sleep(1.2 * (attempt + 1))
        raise BrainUnavailable(f"{self.config.kind} call failed: {last_error}")

    def complete_json(self, system: str, prompt: str, temperature: float = 0.6,
                      max_tokens: int = 2400) -> tuple[dict | None, BrainResult | None]:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        result = self.complete(messages, json_mode=True, temperature=temperature, max_tokens=max_tokens)
        data = extract_json(result.text)
        result.data = data
        return data, result

    # -- vision -----------------------------------------------------------------------
    def vision(self, prompt: str, image_paths: list[str | Path], temperature: float = 0.3) -> BrainResult:
        if not self.config:
            raise BrainUnavailable("no provider configured")
        paths = [Path(p) for p in image_paths]
        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"image not found: {path}")
        images = [(path.name, base64.b64encode(path.read_bytes()).decode("ascii"))
                  for path in paths]
        started = time.time()
        if self.config.kind == "anthropic":
            content = [{"type": "text", "text": prompt}]
            for name, data in images:
                content.append({"type": "image", "source": {"type": "base64", "media_type": _mime(name),
                                                            "data": data}})
            result = self._anthropic([{"role": "user", "content": content}], temperature, 2000)
        elif self.config.kind == "gemini":
            parts = [{"text": prompt}] + [{"inline_data": {"mime_type": _mime(name), "data": data}}
                                          for name, data in images]
            result = self._gemini([{"role": "user", "content": parts}], temperature, 2000)
        else:
            content = [{"type": "text", "text": prompt}]
            for name, data in images:
                content.append({"type": "image_url",
                                "image_url": {"url": f"data:{_mime(name)};base64,{data}"}})
            result = self._openai_compatible([{"role": "user", "content": content}], False, temperature, 2000)
        result.latency_ms = int((time.time() - started) * 1000)
        result.provider = self.config.kind
        result.model = self.config.vision_model or self.config.model
        result.data = extract_json(result.text)
        self.calls.append({"kind": "vision", "latency_ms": result.latency_ms, "images": len(images)})
        return result

    # -- transports -------------------------------------------------------------------
    def _post(self, url: str, payload: dict, headers: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:600]
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc

    def _openai_compatible(self, messages, json_mode, temperature, max_tokens) -> BrainResult:
        assert self.config
        url = self.config.base_url.rstrip("/") + "/chat/completions"
        payload = {"model": self.config.model, "messages": messages, "temperature": temperature,
                   "max_tokens": max_tokens}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        data = self._post(url, payload, {"Content-Type": "application/json",
                                         "Authorization": "Bearer " + self.config.api_key})
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
        return BrainResult(text=text, raw=data,
                           tokens={"prompt": usage.get("prompt_tokens", 0),
                                   "completion": usage.get("completion_tokens", 0)})

    def _anthropic(self, messages, temperature, max_tokens) -> BrainResult:
        assert self.config
        system = "\n".join(m["content"] for m in messages if m.get("role") == "system")
        turns = [m for m in messages if m.get("role") != "system"]
        payload = {"model": self.config.model, "max_tokens": max_tokens, "temperature": temperature,
                   "messages": turns}
        if system:
            payload["system"] = system
        data = self._post(self.config.base_url.rstrip("/") + "/messages", payload,
                          {"Content-Type": "application/json", "x-api-key": self.config.api_key,
                           "anthropic-version": "2023-06-01"})
        blocks = data.get("content") or []
        text = "".join(block.get("text", "") for block in blocks if isinstance(block, dict))
        usage = data.get("usage") or {}
        return BrainResult(text=text, raw=data,
                           tokens={"prompt": usage.get("input_tokens", 0),
                                   "completion": usage.get("output_tokens", 0)})

    def _gemini(self, messages, temperature, max_tokens) -> BrainResult:
        assert self.config
        system = "\n".join(m["content"] for m in messages if m.get("role") == "system")
        contents = []
        for message in messages:
            if message.get("role") == "system":
                continue
            role = "model" if message.get("role") == "assistant" else "user"
            content = message.get("content")
            parts = content if isinstance(content, list) else [{"text": str(content)}]
            contents.append({"role": role, "parts": parts})
        payload = {"contents": contents, "generationConfig": {
            "temperature": temperature, "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json"}}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        url = (f"{self.config.base_url.rstrip('/')}/models/{self.config.model}:generateContent"
               f"?key={self.config.api_key}")
        data = self._post(url, payload, {"Content-Type": "application/json"})
        candidates = data.get("candidates") or [{}]
        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
        usage = data.get("usageMetadata") or {}
        return BrainResult(text=text, raw=data,
                           tokens={"prompt": usage.get("promptTokenCount", 0),
                                   "completion": usage.get("candidatesTokenCount", 0)})


def _mime(name: str) -> str:
    suffix = Path(name).suffix.lower()
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(suffix.lstrip("."), "image/png")
