import os, json, math, random, urllib.request, urllib.error, html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from pathlib import Path
from engine_v2 import blueprint as blueprint_v2, luau as luau_v2

def load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path): return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line: continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('\"').strip("'"))
    except OSError: pass
load_dotenv()

DEFAULT_SETTINGS = {"size": 1800, "grid": 64, "seed": 42, "style": "Stylized Low Poly", "detail": "high", "relief": 1.0, "decor": 70, "visual_theme":"auto", "vfx_density":65, "cosmetic_detail":85, "game_style":"auto"}
BIOME_PALETTE = {
    "forest": ["Forest", "Dense forest", "Woodlands"],
    "desert": ["Desert", "Dunes", "Drylands"],
    "snow": ["Snow", "Tundra", "Frozen"],
    "mountain": ["Mountain", "Alpine", "Highlands"],
    "grass": ["Grassland", "Meadow", "Plains"],
    "swamp": ["Swamp", "Wetlands", "Marsh"],
    "coast": ["Coast", "Beach", "Ocean"],
}


def call_ai(idea, settings):
    url = os.environ.get("IDEA2WORLD_API_URL", "").strip()
    key = os.environ.get("IDEA2WORLD_API_KEY", "").strip()
    model = os.environ.get("IDEA2WORLD_MODEL", "gpt-4o-mini").strip()
    if not (url and key):
        return None
    prompt = f'''Design a Roblox map blueprint for this user idea: {idea}\nSettings: {json.dumps(settings)}\nReturn ONLY valid JSON with fields: title (string), overview (string), style (string), biomes (array of strings), landmarks (array of 5-12 objects with name, type, x, z, scale, description; x and z are normalized -1..1), routes (array of objects with name and type), palette (array of hex colors). Make a strong deliberate map composition, clear focal point, distinct zones, gameplay-readable traversal, and varied elevation. Landmark type values can be: tower, village, temple, cave, waterfall, bridge, castle, volcano, ruins, lake, portal, giant_tree, factory, arena, monument, dock. Keep this blueprint buildable with Roblox primitives.''' 
    payload = {"model": model, "messages": [{"role": "system", "content": "You are a professional procedural game-world designer. Output valid JSON only."}, {"role": "user", "content": prompt}], "temperature": 0.75}
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json", "Authorization":"Bearer " + key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
        content = data["choices"][0]["message"]["content"]
        content = content.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(content)
    except Exception as e:
        return {"_error": str(e)}


def fallback_blueprint(idea, settings):
    low = idea.lower()
    if any(k in low for k in ["volcano", "lava", "הר געש", "לבה"]):
        title, biomes = "Volcanic Frontier", ["Mountain", "Lava Fields", "Ash Forest"]
        types = ["volcano", "ruins", "bridge", "cave", "arena", "monument", "village", "waterfall"]
    elif any(k in low for k in ["forest", "jungle", "יער", "ג'ונגל"]):
        title, biomes = "Wildwood Expedition", ["Dense Forest", "River Valley", "Ancient Grove"]
        types = ["giant_tree", "waterfall", "village", "bridge", "ruins", "cave", "temple", "lake"]
    elif any(k in low for k in ["desert", "מדבר"]):
        title, biomes = "Dune Sea", ["Sand Dunes", "Oasis", "Rocky Canyon"]
        types = ["monument", "temple", "village", "cave", "bridge", "ruins", "lake", "tower"]
    elif any(k in low for k in ["city", "town", "עיר", "כפר"]):
        title, biomes = "Frontier City", ["City Center", "Residential District", "Parklands", "Industrial Quarter"]
        types = ["castle", "factory", "monument", "bridge", "village", "arena", "tower", "dock"]
    else:
        title, biomes = "Adventure Realm", ["Wild Highlands", "River Basin", "Ancient Ruins", "Woodlands"]
        types = ["tower", "village", "temple", "waterfall", "bridge", "cave", "ruins", "giant_tree", "monument"]
    names = {
        "volcano": ["The Ember Crown", "Magma Observatory"], "ruins": ["Forgotten Gate", "Broken Citadel"],
        "bridge": ["Skyspan Crossing", "Old Stone Bridge"], "cave": ["Echo Caverns", "Crystal Hollow"],
        "waterfall": ["Silverfall", "Hidden Cascade"], "castle": ["Highkeep", "Royal Citadel"],
        "village": ["Pinewatch", "Traveler's Rest"], "lake": ["Mirror Lake", "Blue Basin"],
        "tower": ["Lookout Spire", "Beacon Tower"], "portal": ["Rift Nexus"], "giant_tree": ["Elderwood"],
        "factory": ["Old Works"], "arena": ["Stone Ring"], "monument": ["World Pillar"], "temple": ["Sunken Shrine"], "dock": ["Harbor Point"]}
    rng = random.Random(int(settings.get("seed", 42)))
    # Locations deliberately use a loose radial layout, with a center focal landmark.
    positions = [(0,0),(-.65,-.42),(.62,-.52),(-.65,.48),(.66,.42),(-.05,.78),(.05,-.8),(-.9,.05),(.9,-.05),(-.35,.15)]
    landmarks = []
    for i, typ in enumerate(types[:10]):
        x,z = positions[i]
        if i: x += rng.uniform(-.12,.12); z += rng.uniform(-.12,.12)
        name = rng.choice(names.get(typ, [typ.title()]))
        landmarks.append({"name":name,"type":typ,"x":round(max(-.92,min(.92,x)),3),"z":round(max(-.92,min(.92,z)),3),"scale":round(rng.uniform(0.8,1.5),2),"description":f"Explore the {name} landmark."})
    return {"title": title, "overview": f"A large {settings.get('style','stylized')} adventure world inspired by: {idea}. Designed with distinct biomes, landmarks, exploration routes, and a readable central focal point.", "style":settings.get("style","Stylized Low Poly"), "biomes":biomes, "landmarks":landmarks, "routes":[{"name":"Main exploration trail","type":"trail"},{"name":"Scenic overlook route","type":"ridge path"}], "palette":["#507b48","#8bbf65","#6f9ec6","#d7b878","#625b73"]}


def normalize_blueprint(bp, idea, settings):
    if not isinstance(bp, dict): bp = fallback_blueprint(idea, settings)
    fb = fallback_blueprint(idea, settings)
    bp.setdefault("title", fb["title"]); bp.setdefault("overview", fb["overview"]); bp.setdefault("style", settings.get("style"))
    if not isinstance(bp.get("landmarks"), list) or not bp["landmarks"] or any(not isinstance(lm, dict) for lm in bp["landmarks"]): bp["landmarks"] = fb["landmarks"]
    bp["landmarks"] = bp["landmarks"][:14]
    for lm in bp["landmarks"]:
        lm.setdefault("type", "monument"); lm.setdefault("name", str(lm.get("type", "Landmark").title())); lm.setdefault("scale", 1)
        lm["x"] = max(-.95, min(.95, float(lm.get("x", 0))))
        lm["z"] = max(-.95, min(.95, float(lm.get("z", 0))))
        lm["scale"] = max(.4, min(2.8, float(lm.get("scale", 1))))
    bp.setdefault("biomes", fb["biomes"]); bp.setdefault("routes", fb["routes"]); bp.setdefault("palette", fb["palette"])
    return bp


def luau_value(value):
    if value is None: return "nil"
    if value is True: return "true"
    if value is False: return "false"
    if isinstance(value, (int, float)): return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        return '"' + escaped + '"' 
    if isinstance(value, list): return "{" + ",".join(luau_value(v) for v in value) + "}"
    if isinstance(value, dict): return "{" + ",".join("[" + luau_value(str(k)) + "]=" + luau_value(v) for k,v in value.items()) + "}"
    return "nil"

def luau_for(bp, settings):
    data = luau_value(bp)
    size = int(settings.get("size", 900)); grid = max(12, min(64, int(settings.get("grid", 36)))); seed = int(settings.get("seed", 42))
    return f'''-- Idea2World generated map | {bp['title']}\n-- Paste into Roblox Studio Command Bar.\n-- For large builds, run in Studio Edit mode, not during live gameplay.\nlocal Blueprint = {data}\nlocal MAP_SIZE = {size}\nlocal GRID = {grid}\nlocal SEED = {seed}\nlocal TILE = MAP_SIZE / GRID\nlocal ROOT = workspace:FindFirstChild("Idea2World_Generated") or Instance.new("Folder")\nROOT.Name = "Idea2World_Generated"\nROOT.Parent = workspace\nROOT:ClearAllChildren()\nlocal terrainFolder = Instance.new("Folder", ROOT); terrainFolder.Name = "TerrainTiles"\nlocal landmarkFolder = Instance.new("Folder", ROOT); landmarkFolder.Name = "Landmarks"\nlocal decorFolder = Instance.new("Folder", ROOT); decorFolder.Name = "Decoration"\nlocal function hash(x,z)\n  local n = math.sin(x*127.1 + z*311.7 + SEED*0.013)*43758.5453\n  return n - math.floor(n)\nend\nlocal function smoothNoise(x,z)\n  local ix,iz = math.floor(x),math.floor(z); local fx,fz=x-ix,z-iz\n  fx=fx*fx*(3-2*fx); fz=fz*fz*(3-2*fz)\n  local a,b,c,d=hash(ix,iz),hash(ix+1,iz),hash(ix,iz+1),hash(ix+1,iz+1)\n  local ab=a+(b-a)*fx; local cd=c+(d-c)*fx; return ab+(cd-ab)*fz\nend\nlocal function heightAt(x,z)\n  local broad=smoothNoise(x*.018,z*.018); local detail=smoothNoise(x*.055+19,z*.055-8)\n  local radial=1-math.clamp(math.sqrt(x*x+z*z)/(MAP_SIZE*.72),0,1)\n  return math.max(2, 9+broad*38+detail*10+radial*14)\nend\nlocal function makePart(parent,name,size,pos,color,material)\n  local p=Instance.new("Part"); p.Name=name; p.Size=size; p.Position=pos; p.Anchored=true; p.TopSurface=Enum.SurfaceType.Smooth; p.BottomSurface=Enum.SurfaceType.Smooth; p.Material=material or Enum.Material.SmoothPlastic; p.Color=color; p.Parent=parent; return p\nend\nlocal palette={{grass=Color3.fromRGB(92,151,83), forest=Color3.fromRGB(49,112,58), rock=Color3.fromRGB(104,103,100), sand=Color3.fromRGB(199,175,112), snow=Color3.fromRGB(224,231,239)}}\nlocal green=palette[1].grass; local forest=palette[1].forest; local rock=palette[1].rock; local sand=palette[1].sand\n-- Heightfield tiled in anchored parts. Each tile has slight color variation.\nfor ix=1,GRID do for iz=1,GRID do\n  local x=-MAP_SIZE/2+(ix-.5)*TILE; local z=-MAP_SIZE/2+(iz-.5)*TILE; local h=heightAt(x,z)\n  local n=hash(ix,iz); local color=green:Lerp(forest,n*.35)\n  if h>38 then color=color:Lerp(rock,.5) end\n  if n>.91 then color=color:Lerp(sand,.25) end\n  makePart(terrainFolder,"Ground_"..ix.."_"..iz,Vector3.new(TILE+1,h,TILE+1),Vector3.new(x,h/2-2,z),color,Enum.Material.Grass)\nend end\n-- A winding river ribbon with stone banks.\nlocal riverFolder=Instance.new("Folder",ROOT); riverFolder.Name="River"\nfor i=1,45 do local z=-MAP_SIZE*.46+i*(MAP_SIZE*.92/45); local x=math.sin(i*.19+SEED)*MAP_SIZE*.14; local y=heightAt(x,z)+.15\n  local w=TILE*1.05; local water=makePart(riverFolder,"Water_"..i,Vector3.new(w,1.2,TILE*1.15),Vector3.new(x,y,z),Color3.fromRGB(65,147,199),Enum.Material.Glass); water.Transparency=.25\nend\n-- Landmark primitives; each landmark receives a small silhouette built from readable shapes.\nlocal function buildLandmark(lm,index)\n local x,z=lm.x*MAP_SIZE*.43,lm.z*MAP_SIZE*.43; local y=heightAt(x,z); local s=lm.scale*TILE*1.6; local kind=string.lower(lm.type or "monument"); local model=Instance.new("Model",landmarkFolder); model.Name=lm.name or ("Landmark_"..index)\n local stone=Color3.fromRGB(134,125,112); local accent=Color3.fromRGB(206,173,92)\n if kind=="volcano" then\n   makePart(model,"VolcanoBase",Vector3.new(s*3, s*1.3,s*3),Vector3.new(x,y+s*.65,z),Color3.fromRGB(92,61,49),Enum.Material.Rock)\n   makePart(model,"LavaCrater",Vector3.new(s*1.2,2,s*1.2),Vector3.new(x,y+s*1.4,z),Color3.fromRGB(255,85,20),Enum.Material.Neon)\n elseif kind=="waterfall" or kind=="lake" then\n   makePart(model,"Pool",Vector3.new(s*2,1.4,s*2),Vector3.new(x,y+1,z),Color3.fromRGB(55,151,206),Enum.Material.Glass)\n   if kind=="waterfall" then makePart(model,"Fall",Vector3.new(s*.55,s*2.5,2),Vector3.new(x,y+s*1.4,z),Color3.fromRGB(94,184,222),Enum.Material.Glass) end\n elseif kind=="giant_tree" then\n   makePart(model,"Trunk",Vector3.new(s*.38,s*2,s*.38),Vector3.new(x,y+s,z),Color3.fromRGB(105,74,45),Enum.Material.Wood)\n   for k=1,5 do local offset=Vector3.new(math.sin(k*5)*s*.3,s*(1.1+k*.28),math.cos(k*5)*s*.3); local orb=makePart(model,"Canopy_"..k,Vector3.new(s*1.2,s*1.05,s*1.2),Vector3.new(x,y,z)+offset,Color3.fromRGB(55+ k*4,125+k*7,54),Enum.Material.Grass); orb.Shape=Enum.PartType.Ball end\n else\n   local base=makePart(model,"Foundation",Vector3.new(s*1.8,3,s*1.8),Vector3.new(x,y+1.5,z),stone,Enum.Material.Slate)\n   if kind=="tower" or kind=="monument" or kind=="portal" then\n     makePart(model,"MainTower",Vector3.new(s*.7,s*2.8,s*.7),Vector3.new(x,y+s*1.4,z),stone,Enum.Material.Slate)\n     makePart(model,"Crown",Vector3.new(s*1.05,4,s*1.05),Vector3.new(x,y+s*2.9,z),accent,Enum.Material.Metal)\n   elseif kind=="bridge" then\n     makePart(model,"BridgeDeck",Vector3.new(s*3,3,s*.65),Vector3.new(x,y+4,z),stone,Enum.Material.Slate)\n     for side=-1,1,2 do makePart(model,"Pillar",Vector3.new(4,s*1.2,4),Vector3.new(x+side*s*1.2,y+s*.6,z),stone,Enum.Material.Rock) end\n   elseif kind=="village" or kind=="factory" or kind=="castle" then\n     for k=1,5 do local ox=(k-3)*s*.45; local hh=s*(.5+hash(k,index)*.6); makePart(model,"Building_"..k,Vector3.new(s*.4,hh,s*.4),Vector3.new(x+ox,y+hh/2,z+math.cos(k)*s*.5),Color3.fromRGB(157,119,82),Enum.Material.Wood) end\n   else\n     for k=1,4 do local block=makePart(model,"Structure_"..k,Vector3.new(s*.65,s*(.5+k*.25),s*.65),Vector3.new(x+(k-2.5)*s*.55,y+s*.4,z),stone,Enum.Material.Rock) end\n   end\n end\nend\nfor i,lm in ipairs(Blueprint.landmarks) do buildLandmark(lm,i) end\n-- Forest decoration is seeded, spread across the map but kept clear of major focal points.\nlocal rng=Random.new(SEED); local treeCount=math.floor(GRID*GRID*.22)\nfor i=1,treeCount do local x=rng:NextNumber(-MAP_SIZE*.46,MAP_SIZE*.46); local z=rng:NextNumber(-MAP_SIZE*.46,MAP_SIZE*.46); local y=heightAt(x,z); local trunkH=rng:NextNumber(7,15); local trunk=makePart(decorFolder,"TreeTrunk",Vector3.new(2,trunkH,2),Vector3.new(x,y+trunkH/2,z),Color3.fromRGB(101,72,47),Enum.Material.Wood); local crown=makePart(decorFolder,"TreeCrown",Vector3.new(rng:NextNumber(8,14),rng:NextNumber(8,14),rng:NextNumber(8,14)),Vector3.new(x,y+trunkH+4,z),Color3.fromRGB(58,129,62),Enum.Material.Grass); crown.Shape=Enum.PartType.Ball end\nprint("Idea2World created: "..Blueprint.title.." | tiles="..(GRID*GRID).." | landmarks="..#Blueprint.landmarks)\n'''

ROOT_DIR = Path(__file__).resolve().parent

class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            file = ROOT_DIR / "templates" / "index.html"
            self.send_file(file, "text/html; charset=utf-8"); return
        if path == "/api/settings":
            self.send_json({"api_configured": bool(os.environ.get("IDEA2WORLD_API_URL") and os.environ.get("IDEA2WORLD_API_KEY")), "model": os.environ.get("IDEA2WORLD_MODEL", "gpt-4o-mini"), "defaults": DEFAULT_SETTINGS}); return
        if path.startswith("/static/"):
            relative = path[len("/static/"):]
            file = (ROOT_DIR / "static" / relative).resolve()
            if ROOT_DIR / "static" not in file.parents: self.send_json({"error":"Not found"},404); return
            mime = "text/javascript; charset=utf-8" if file.suffix == ".js" else "text/css; charset=utf-8" if file.suffix == ".css" else "application/octet-stream"
            self.send_file(file, mime); return
        self.send_json({"error":"Not found"},404)

    def send_file(self, file, mime):
        if not file.exists(): self.send_json({"error":"File missing"},404); return
        body=file.read_bytes(); self.send_response(200); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        path=urlparse(self.path).path
        try: body=self.read_json()
        except Exception: self.send_json({"error":"Invalid JSON request"},400); return
        if path == "/api/generate":
            idea=str(body.get("idea", "")).strip()
            if len(idea)<3: self.send_json({"error":"Please describe a world idea (at least 3 characters)."},400); return
            settings={**DEFAULT_SETTINGS, **(body.get("settings") or {})}
            settings["size"]=max(700,min(4000,int(settings["size"])))
            settings["grid"]=max(24,min(100,int(settings["grid"])))
            settings["relief"]=max(0.6,min(2.0,float(settings.get("relief",1.0))))
            settings["decor"]=max(0,min(100,int(settings.get("decor",70))))
            settings["seed"]=int(settings["seed"])
            settings["game_style"]=str(settings.get("game_style","auto"))
            base_bp=blueprint_v2(idea,settings)
            ai_bp=call_ai(idea,settings); ai_error=ai_bp.get("_error") if isinstance(ai_bp,dict) else None
            # AI is allowed to refine narrative/layout, while the local engine supplies buildable defaults.
            if isinstance(ai_bp,dict) and not ai_error:
                for key in ("title","overview","biomes","landmarks","routes","palette"):
                    if key in ai_bp and ai_bp[key]: base_bp[key]=ai_bp[key]
            try:
                bp=normalize_blueprint(base_bp,idea,settings)
                bp["archetype"]=blueprint_v2(idea,settings)["archetype"]
                bp["settings"]=settings; bp["idea"]=idea; bp["engine"]="AI Architect + Procedural Engine v2" if ai_bp and not ai_error else "Idea2World 5.0 Genre-Aware Architect"
                script=luau_v2(bp,settings)
            except Exception as ex:
                ai_error=str(ex); bp=normalize_blueprint(blueprint_v2(idea,settings),idea,settings); bp["archetype"]=blueprint_v2(idea,settings)["archetype"]; bp["settings"]=settings; bp["idea"]=idea; bp["engine"]="Idea2World 5.0 Genre-Aware Architect"; script=luau_v2(bp,settings)
            self.send_json({"blueprint":bp,"luau":script,"ai_error":ai_error}); return
        if path == "/download/luau":
            content=str(body.get("luau", "")); name=str(body.get("name", "Idea2World_Map").replace(" ","_"))
            self.send_download(content.encode("utf-8"),name+".luau","text/plain; charset=utf-8"); return
        if path == "/download/blueprint":
            content=json.dumps(body.get("blueprint",{}),ensure_ascii=False,indent=2).encode("utf-8")
            self.send_download(content,"Idea2World_Blueprint.json","application/json; charset=utf-8"); return
        self.send_json({"error":"Not found"},404)

    def send_download(self, content, filename, mime):
        self.send_response(200); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(content))); self.send_header("Content-Disposition",f'attachment; filename="{filename}"'); self.end_headers(); self.wfile.write(content)

    def log_message(self, fmt, *args):
        print("[Idea2World] " + fmt % args)

if __name__ == "__main__":
    print("Idea2World running at http://127.0.0.1:8765")
    print("AI planner: configured" if os.environ.get("IDEA2WORLD_API_URL") and os.environ.get("IDEA2WORLD_API_KEY") else "AI planner: off (built-in generation enabled)")
    HTTPServer(("127.0.0.1",8765),Handler).serve_forever()
