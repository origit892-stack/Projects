-- Idea2World generated map | Volcanic Frontier
-- Paste into Roblox Studio Command Bar.
-- For large builds, run in Studio Edit mode, not during live gameplay.
local Blueprint = {["title"]="Volcanic Frontier",["overview"]="A large Stylized Low Poly adventure world inspired by: A volcano with lava rivers and a lost village. Designed with distinct biomes, landmarks, exploration routes, and a readable central focal point.",["style"]="Stylized Low Poly",["biomes"]={"Mountain","Lava Fields","Ash Forest"},["landmarks"]={{["name"]="The Ember Crown",["type"]="volcano",["x"]=0.0,["z"]=0.0,["scale"]=1.06,["description"]="Explore the The Ember Crown landmark."},{["name"]="Forgotten Gate",["type"]="ruins",["x"]=-0.68,["z"]=-0.494,["scale"]=0.86,["description"]="Explore the Forgotten Gate landmark."},{["name"]="Skyspan Crossing",["type"]="bridge",["x"]=0.559,["z"]=-0.4,["scale"]=1.08,["description"]="Explore the Skyspan Crossing landmark."},{["name"]="Crystal Hollow",["type"]="cave",["x"]=-0.763,["z"]=0.477,["scale"]=1.15,["description"]="Explore the Crystal Hollow landmark."},{["name"]="Stone Ring",["type"]="arena",["x"]=0.586,["z"]=0.499,["scale"]=1.14,["description"]="Explore the Stone Ring landmark."},{["name"]="World Pillar",["type"]="monument",["x"]=0.012,["z"]=0.828,["scale"]=1.13,["description"]="Explore the World Pillar landmark."},{["name"]="Traveler's Rest",["type"]="village",["x"]=0.149,["z"]=-0.746,["scale"]=0.87,["description"]="Explore the Traveler's Rest landmark."},{["name"]="Hidden Cascade",["type"]="waterfall",["x"]=-0.825,["z"]=0.023,["scale"]=0.88,["description"]="Explore the Hidden Cascade landmark."}},["routes"]={{["name"]="Main exploration trail",["type"]="trail"},{["name"]="Scenic overlook route",["type"]="ridge path"}},["palette"]={"#507b48","#8bbf65","#6f9ec6","#d7b878","#625b73"},["settings"]={["size"]=1000,["grid"]=26,["seed"]=8,["style"]="Stylized Low Poly",["detail"]="high"},["idea"]="A volcano with lava rivers and a lost village",["engine"]="Built-in procedural planner"}
local MAP_SIZE = 1000
local GRID = 26
local SEED = 8
local TILE = MAP_SIZE / GRID
local ROOT = workspace:FindFirstChild("Idea2World_Generated") or Instance.new("Folder")
ROOT.Name = "Idea2World_Generated"
ROOT.Parent = workspace
ROOT:ClearAllChildren()
local terrainFolder = Instance.new("Folder", ROOT); terrainFolder.Name = "TerrainTiles"
local landmarkFolder = Instance.new("Folder", ROOT); landmarkFolder.Name = "Landmarks"
local decorFolder = Instance.new("Folder", ROOT); decorFolder.Name = "Decoration"
local function hash(x,z)
  local n = math.sin(x*127.1 + z*311.7 + SEED*0.013)*43758.5453
  return n - math.floor(n)
end
local function smoothNoise(x,z)
  local ix,iz = math.floor(x),math.floor(z); local fx,fz=x-ix,z-iz
  fx=fx*fx*(3-2*fx); fz=fz*fz*(3-2*fz)
  local a,b,c,d=hash(ix,iz),hash(ix+1,iz),hash(ix,iz+1),hash(ix+1,iz+1)
  local ab=a+(b-a)*fx; local cd=c+(d-c)*fx; return ab+(cd-ab)*fz
end
local function heightAt(x,z)
  local broad=smoothNoise(x*.018,z*.018); local detail=smoothNoise(x*.055+19,z*.055-8)
  local radial=1-math.clamp(math.sqrt(x*x+z*z)/(MAP_SIZE*.72),0,1)
  return math.max(2, 9+broad*38+detail*10+radial*14)
end
local function makePart(parent,name,size,pos,color,material)
  local p=Instance.new("Part"); p.Name=name; p.Size=size; p.Position=pos; p.Anchored=true; p.TopSurface=Enum.SurfaceType.Smooth; p.BottomSurface=Enum.SurfaceType.Smooth; p.Material=material or Enum.Material.SmoothPlastic; p.Color=color; p.Parent=parent; return p
end
local palette={grass=Color3.fromRGB(92,151,83), forest=Color3.fromRGB(49,112,58), rock=Color3.fromRGB(104,103,100), sand=Color3.fromRGB(199,175,112), snow=Color3.fromRGB(224,231,239)}
local green=palette[1].grass; local forest=palette[1].forest; local rock=palette[1].rock; local sand=palette[1].sand
-- Heightfield tiled in anchored parts. Each tile has slight color variation.
for ix=1,GRID do for iz=1,GRID do
  local x=-MAP_SIZE/2+(ix-.5)*TILE; local z=-MAP_SIZE/2+(iz-.5)*TILE; local h=heightAt(x,z)
  local n=hash(ix,iz); local color=green:Lerp(forest,n*.35)
  if h>38 then color=color:Lerp(rock,.5) end
  if n>.91 then color=color:Lerp(sand,.25) end
  makePart(terrainFolder,"Ground_"..ix.."_"..iz,Vector3.new(TILE+1,h,TILE+1),Vector3.new(x,h/2-2,z),color,Enum.Material.Grass)
end end
-- A winding river ribbon with stone banks.
local riverFolder=Instance.new("Folder",ROOT); riverFolder.Name="River"
for i=1,45 do local z=-MAP_SIZE*.46+i*(MAP_SIZE*.92/45); local x=math.sin(i*.19+SEED)*MAP_SIZE*.14; local y=heightAt(x,z)+.15
  local w=TILE*1.05; local water=makePart(riverFolder,"Water_"..i,Vector3.new(w,1.2,TILE*1.15),Vector3.new(x,y,z),Color3.fromRGB(65,147,199),Enum.Material.Glass); water.Transparency=.25
end
-- Landmark primitives; each landmark receives a small silhouette built from readable shapes.
local function buildLandmark(lm,index)
 local x,z=lm.x*MAP_SIZE*.43,lm.z*MAP_SIZE*.43; local y=heightAt(x,z); local s=lm.scale*TILE*1.6; local kind=string.lower(lm.type or "monument"); local model=Instance.new("Model",landmarkFolder); model.Name=lm.name or ("Landmark_"..index)
 local stone=Color3.fromRGB(134,125,112); local accent=Color3.fromRGB(206,173,92)
 if kind=="volcano" then
   makePart(model,"VolcanoBase",Vector3.new(s*3, s*1.3,s*3),Vector3.new(x,y+s*.65,z),Color3.fromRGB(92,61,49),Enum.Material.Rock)
   makePart(model,"LavaCrater",Vector3.new(s*1.2,2,s*1.2),Vector3.new(x,y+s*1.4,z),Color3.fromRGB(255,85,20),Enum.Material.Neon)
 elseif kind=="waterfall" or kind=="lake" then
   makePart(model,"Pool",Vector3.new(s*2,1.4,s*2),Vector3.new(x,y+1,z),Color3.fromRGB(55,151,206),Enum.Material.Glass)
   if kind=="waterfall" then makePart(model,"Fall",Vector3.new(s*.55,s*2.5,2),Vector3.new(x,y+s*1.4,z),Color3.fromRGB(94,184,222),Enum.Material.Glass) end
 elseif kind=="giant_tree" then
   makePart(model,"Trunk",Vector3.new(s*.38,s*2,s*.38),Vector3.new(x,y+s,z),Color3.fromRGB(105,74,45),Enum.Material.Wood)
   for k=1,5 do local offset=Vector3.new(math.sin(k*5)*s*.3,s*(1.1+k*.28),math.cos(k*5)*s*.3); local orb=makePart(model,"Canopy_"..k,Vector3.new(s*1.2,s*1.05,s*1.2),Vector3.new(x,y,z)+offset,Color3.fromRGB(55+ k*4,125+k*7,54),Enum.Material.Grass); orb.Shape=Enum.PartType.Ball end
 else
   local base=makePart(model,"Foundation",Vector3.new(s*1.8,3,s*1.8),Vector3.new(x,y+1.5,z),stone,Enum.Material.Slate)
   if kind=="tower" or kind=="monument" or kind=="portal" then
     makePart(model,"MainTower",Vector3.new(s*.7,s*2.8,s*.7),Vector3.new(x,y+s*1.4,z),stone,Enum.Material.Slate)
     makePart(model,"Crown",Vector3.new(s*1.05,4,s*1.05),Vector3.new(x,y+s*2.9,z),accent,Enum.Material.Metal)
   elseif kind=="bridge" then
     makePart(model,"BridgeDeck",Vector3.new(s*3,3,s*.65),Vector3.new(x,y+4,z),stone,Enum.Material.Slate)
     for side=-1,1,2 do makePart(model,"Pillar",Vector3.new(4,s*1.2,4),Vector3.new(x+side*s*1.2,y+s*.6,z),stone,Enum.Material.Rock) end
   elseif kind=="village" or kind=="factory" or kind=="castle" then
     for k=1,5 do local ox=(k-3)*s*.45; local hh=s*(.5+hash(k,index)*.6); makePart(model,"Building_"..k,Vector3.new(s*.4,hh,s*.4),Vector3.new(x+ox,y+hh/2,z+math.cos(k)*s*.5),Color3.fromRGB(157,119,82),Enum.Material.Wood) end
   else
     for k=1,4 do local block=makePart(model,"Structure_"..k,Vector3.new(s*.65,s*(.5+k*.25),s*.65),Vector3.new(x+(k-2.5)*s*.55,y+s*.4,z),stone,Enum.Material.Rock) end
   end
 end
end
for i,lm in ipairs(Blueprint.landmarks) do buildLandmark(lm,i) end
-- Forest decoration is seeded, spread across the map but kept clear of major focal points.
local rng=Random.new(SEED); local treeCount=math.floor(GRID*GRID*.22)
for i=1,treeCount do local x=rng:NextNumber(-MAP_SIZE*.46,MAP_SIZE*.46); local z=rng:NextNumber(-MAP_SIZE*.46,MAP_SIZE*.46); local y=heightAt(x,z); local trunkH=rng:NextNumber(7,15); local trunk=makePart(decorFolder,"TreeTrunk",Vector3.new(2,trunkH,2),Vector3.new(x,y+trunkH/2,z),Color3.fromRGB(101,72,47),Enum.Material.Wood); local crown=makePart(decorFolder,"TreeCrown",Vector3.new(rng:NextNumber(8,14),rng:NextNumber(8,14),rng:NextNumber(8,14)),Vector3.new(x,y+trunkH+4,z),Color3.fromRGB(58,129,62),Enum.Material.Grass); crown.Shape=Enum.PartType.Ball end
print("Idea2World created: "..Blueprint.title.." | tiles="..(GRID*GRID).." | landmarks="..#Blueprint.landmarks)
