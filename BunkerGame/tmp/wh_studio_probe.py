import sys, msgpack, urllib.request, http.server, threading, time, json

PORT = sys.argv[1] if len(sys.argv) > 1 else "8001"
RESULT_PORT = 8810
RESULT_FILE = "/tmp/wh_probe_result.txt"

# Lua: count warehouse MeshParts + SAs, check SpawnRoot + bunker, POST result back
LUA = r'''
local HttpService = game:GetService("HttpService")
local ws = game:GetService("Workspace")
local out = {}
local wh = ws:FindFirstChild("abandoned_warehouse_interior_01")
local mp = 0; local sa = 0; local mats = {}
if wh then
  for _, d in wh:GetDescendants() do
    if d:IsA("MeshPart") then
      mp = mp + 1
      local m = tostring(d.Material)
      mats[m] = (mats[m] or 0) + 1
    elseif d:IsA("SurfaceAppearance") then
      sa = sa + 1
    end
  end
end
local spawn = ws:FindFirstChild("SpawnRoot") ~= nil
local bunker = ws:FindFirstChild("bunker-rooms") ~= nil
local matstr = {}
for k,v in pairs(mats) do table.insert(matstr, k.."="..v) end
local result = json_encode({
  warehouse_present = wh ~= nil,
  mesh_parts = mp,
  surface_appearances = sa,
  materials = matstr,
  spawnroot_present = spawn,
  bunker_rooms_present = bunker
})
pcall(function()
  HttpService:RequestAsync({
    Url = "http://localhost:8810/result",
    Method = "POST",
    Body = result
  })
end)
return "done"
'''

# json_encode helper must be defined in Studio; prepend a simple one
LUA = r'''
local function json_encode(t)
  local parts = {}
  for k,v in pairs(t) do
    if type(v) == "table" then
      local inner = {}
      for _,x in ipairs(v) do table.insert(inner, '"'..tostring(x)..'"') end
      table.insert(parts, '"'..tostring(k)..'":['..table.concat(inner,",")..']')
    else
      table.insert(parts, '"'..tostring(k)..'":'..tostring(v))
    end
  end
  return "{"..table.concat(parts,",").."}"
end
''' + LUA

received = []
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode("utf-8", "replace")
        received.append(body)
        with open(RESULT_FILE, "w") as f:
            f.write(body)
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

srv = http.server.HTTPServer(("127.0.0.1", RESULT_PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
print("RESULT_SERVER_LISTENING", RESULT_PORT, flush=True)

body = msgpack.packb({"code": LUA, "focus": False}, use_bin_type=True)
req = urllib.request.Request(f"http://localhost:{PORT}/exec", data=body,
    headers={"Content-Type": "application/msgpack"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        print("EXEC_HTTP", r.status, r.read().decode()[:200], flush=True)
except Exception as e:
    print("EXEC_ERROR", e, flush=True)

# wait for result
for _ in range(30):
    if received:
        break
    time.sleep(0.5)
if received:
    print("RESULT:", received[0], flush=True)
else:
    print("RESULT: NONE (no POST received)", flush=True)
srv.shutdown()