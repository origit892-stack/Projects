import sys, msgpack, urllib.request, json

PORT = sys.argv[1] if len(sys.argv) > 1 else "8001"

def try_req(path, method="POST", body=None, ctype="application/msgpack"):
    data = None
    headers = {}
    if body is not None:
        data = body if isinstance(body, bytes) else msgpack.packb(body, use_bin_type=True)
        headers["Content-Type"] = ctype
    req = urllib.request.Request(f"http://localhost:{PORT}/{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            print(f"[{method} /{path}] HTTP {r.status} len={len(raw)}")
            print("  HEADERS", {k:v for k,v in r.headers.items() if k.lower() in ('content-type','content-length')})
            print("  RAW[:600]", repr(raw[:600]))
            return raw
    except urllib.error.HTTPError as e:
        print(f"[{method} /{path}] HTTPError {e.code}", e.read()[:200])
    except Exception as e:
        print(f"[{method} /{path}] ERROR", repr(e))
    return None

# Try snapshot and details with various methods
for path in ["snapshot", "details"]:
    print(f"===== {path} =====")
    try_req(path, "GET")
    try_req(path, "POST", body={})
    try_req(path, "POST", body={"focus": False})
