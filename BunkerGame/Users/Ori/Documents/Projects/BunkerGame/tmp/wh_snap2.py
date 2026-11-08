import sys, msgpack, urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8001"

def req(path, method, body_bytes, ctype="application/msgpack"):
    headers = {}
    if body_bytes is not None:
        headers["Content-Type"] = ctype
    r = urllib.request.Request(f"http://localhost:{PORT}/{path}", data=body_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            raw = resp.read()
            ct = resp.headers.get("content-type", "")
            tag = ""
            if b"Home Page" in raw:
                tag = "(HOME FALLBACK)"
            print(f"{method} /{path} body={body_bytes!r:.40} -> {resp.status} len={len(raw)} ct={ct} {tag} {raw[:120]!r}")
            return raw
    except urllib.error.HTTPError as e:
        print(f"{method} /{path} body={body_bytes!r:.40} -> HTTPError {e.code} {e.read()[:80]!r}")
    except Exception as e:
        print(f"{method} /{path} body={body_bytes!r:.40} -> ERR {e!r}")
    return None

# Try snapshot with many body formats
print("=== int bodies ===")
for i in range(0, 16):
    req("snapshot", "POST", msgpack.packb(i, use_bin_type=True))
print("=== map type bodies ===")
for i in range(0, 16):
    req("snapshot", "POST", msgpack.packb({"type": i}, use_bin_type=True))
print("=== array bodies ===")
for i in range(0, 8):
    req("snapshot", "POST", msgpack.packb([i], use_bin_type=True))
print("=== empty / other ===")
req("snapshot", "POST", b"")
req("snapshot", "POST", msgpack.packb({}, use_bin_type=True))
req("snapshot", "POST", msgpack.packb({"focus": False}, use_bin_type=True))
req("snapshot", "GET", None)
