import sys, msgpack, urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8001"
LUA = 'local ws=game:GetService("Workspace"); local n=0; for _,d in ws:GetDescendants() do if d:IsA("MeshPart") then n=n+1 end end; return "MESH_PARTS="..n'

body = msgpack.packb({"code": LUA, "focus": False}, use_bin_type=True)
req = urllib.request.Request(f"http://localhost:{PORT}/exec", data=body,
    headers={"Content-Type": "application/msgpack"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
        print("STATUS", r.status)
        print("HEADERS", dict(r.headers))
        print("RAW_LEN", len(raw))
        print("RAW_REPR", repr(raw[:2000]))
        # try to unpack as msgpack
        try:
            print("UNPACKED", msgpack.unpackb(raw, raw=False))
        except Exception as e:
            print("UNPACK_ERR", e)
except Exception as e:
    print("ERROR", repr(e))