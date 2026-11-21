"""Lua serialisation helpers for the generated project.

Readability matters here: a person must be able to open `MapConfig.lua` and change a colour or a
landmark without reading generated code. So keys become identifiers, defaults are omitted, and
numeric arrays stay on one line.
"""
from __future__ import annotations

import json
import math

_LUA_KEYWORDS = {
    "and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto", "if", "in",
    "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while",
}


def num(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    if isinstance(value, int):
        return str(value)
    f = float(value)
    if not math.isfinite(f):
        return "0"
    if abs(f - round(f)) < 1e-9:
        return str(int(round(f)))
    return f"{f:.4f}".rstrip("0").rstrip(".")


def string(value: str) -> str:
    out = []
    for ch in str(value):
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 32:
            out.append(f"\\{ord(ch)}")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _key(key: str) -> str:
    if key.isidentifier() and key not in _LUA_KEYWORDS:
        return key
    return f"[{string(key)}]"


def value(v, indent: int = 0) -> str:
    pad = "  " * indent
    inner = "  " * (indent + 1)
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "nil"
    if isinstance(v, (int, float)):
        return num(v)
    if isinstance(v, str):
        return string(v)
    if isinstance(v, (list, tuple)):
        if not v:
            return "{}"
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            return "{" + ", ".join(num(x) for x in v) + "}"
        if all(isinstance(x, str) for x in v):
            return "{" + ", ".join(string(x) for x in v) + "}"
        items = [f"{inner}{value(x, indent + 1)}," for x in v]
        return "{\n" + "\n".join(items) + f"\n{pad}}}"
    if isinstance(v, dict):
        if not v:
            return "{}"
        items = []
        for k, val in v.items():
            items.append(f"{inner}{_key(str(k))} = {value(val, indent + 1)},")
        return "{\n" + "\n".join(items) + f"\n{pad}}}"
    return string(json.dumps(str(v)))


def table(name: str, data, comment: str = "") -> str:
    header = f"-- {comment}\n" if comment else ""
    return f"{header}{name} = {value(data, 0)}\n"


def long_string(source: str) -> str:
    """Embed arbitrary Lua source in a Lua long string, choosing a safe delimiter."""
    level = 0
    while True:
        delim = "[" + ("=" * level) + "["
        if delim not in source and ("]" + ("=" * level) + "]") not in source:
            break
        level += 1
    return delim + source + "]" + ("=" * level) + "]"
