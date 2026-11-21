-- IDEA2WORLD 3.0 | Verdant Frontier
-- Paste into Roblox Studio Command Bar (Edit mode). Generated from a World Blueprint.
-- Builds in bounded batches. Terrain is written inside the generated world footprint.
local BP={"schema_version":4,"visual_theme":"cosmic","visual_profile":{"accent":"#8b5cf6","props":["floating_obelisk","star_orb","crystal_cluster","rift_arch"],"vfx":["stardust","nebula_mist","arcane_rings","meteor_sparks"]},"title":"Verdant Frontier","overview":"Verdant Frontier: A cosmic celestial sanctuary with floating crystal islands, star portals, nebula waterfalls, ancient observatories and glowing astral forests. Authored with a focal landmark, readable districts, natural terrain silhouettes, exploration loops and sightline hierarchy.","style":"Stylized Low Poly","biomes":["Highlands","River Basin","Woodlands","Ancient Ruins"],"landmarks":[{"id":"poi_01","name":"Beacon Spire","type":"tower","x":0.0,"z":0.0,"scale":1.37,"priority":"primary","description":"Tower landmark designed as a readable destination."},{"id":"poi_02","name":"Traveler’s Rest","type":"village","x":0.293,"z":-0.052,"scale":1.17,"priority":"major","description":"Village landmark designed as a readable destination."},{"id":"poi_03","name":"Sunken Shrine","type":"temple","x":-0.359,"z":0.329,"scale":1.1,"priority":"major","description":"Temple landmark designed as a readable destination."},{"id":"poi_04","name":"Hidden Cascade","type":"waterfall","x":0.147,"z":-0.495,"scale":1.04,"priority":"major","description":"Waterfall landmark designed as a readable destination."},{"id":"poi_05","name":"Skyspan Crossing","type":"bridge","x":0.407,"z":0.422,"scale":1.49,"priority":"major","description":"Bridge landmark designed as a readable destination."},{"id":"poi_06","name":"Crystal Hollow","type":"cave","x":-0.645,"z":-0.099,"scale":1.12,"priority":"minor","description":"Cave landmark designed as a readable destination."},{"id":"poi_07","name":"Broken Gate","type":"ruins","x":0.534,"z":-0.451,"scale":1.77,"priority":"minor","description":"Ruins landmark designed as a readable destination."},{"id":"poi_08","name":"Elderwood","type":"giant_tree","x":-0.255,"z":0.68,"scale":1.31,"priority":"minor","description":"Giant Tree landmark designed as a readable destination."},{"id":"poi_09","name":"World Pillar","type":"monument","x":-0.345,"z":-0.694,"scale":1.25,"priority":"minor","description":"Monument landmark designed as a readable destination."},{"id":"poi_10","name":"Blue Basin","type":"lake","x":0.754,"z":0.297,"scale":1.67,"priority":"minor","description":"Lake landmark designed as a readable destination."}],"routes":[{"name":"Grand Exploration Loop","type":"loop","waypoints":[[0.0,0.0],[0.293,-0.052],[-0.359,0.329],[0.147,-0.495],[0.407,0.422],[-0.645,-0.099],[0.534,-0.451],[0.0,0.0]]},{"name":"Ridge Traverse","type":"scenic","waypoints":[[-0.88,-0.45],[-0.45,-0.1],[0.1,0.2],[0.48,0.48],[0.88,0.65]]}],"palette":["#426b48","#80a85d","#b6a06d","#638da0"],"archetype":"temperate","seed":314,"composition":{"focal_point":"center","layout":"irregular radial districts","sightline_priority":["primary landmark","ridge silhouettes","watercourse"],"negative_space":"preserve clearings around POIs and along routes"},"systems":["modular cosmetic prop kits","layered VFX emitters","themed lighting accents","ridge mountain chains","stratified cliff faces","carved cave entrances","clustered forest groves","architectural landmark kits","curated exploration routes"],"settings":{"size":2200,"grid":48,"seed":314,"style":"Stylized Low Poly","detail":"high","relief":1.0,"decor":65,"visual_theme":"cosmic","vfx_density":82,"cosmetic_detail":95},"idea":"A cosmic celestial sanctuary with floating crystal islands, star portals, nebula waterfalls, ancient observatories and glowing astral forests","engine":"Procedural World Engine v4"}
local SIZE,GRID,SEED,RELIEF,DECOR=2200,48,314,1.0,65
local TILE=SIZE/GRID; local Terrain=workspace.Terrain; local rng=Random.new(SEED)
local VFX_DENSITY=math.clamp(82,0,100); local COSMETIC_DETAIL=math.clamp(95,0,100)
local VISUAL_THEME=BP.visual_theme or 'natural'; local VISUAL_PROFILE=BP.visual_profile or {accent='#86b96b'}
local old=workspace:FindFirstChild('Idea2World_Generated'); if old then old:Destroy() end
local root=Instance.new('Folder');root.Name='Idea2World_Generated';root.Parent=workspace
local folders={}; for _,n in ipairs({'Landmarks','Forests','Cliffs','Caves','Routes','Details'}) do local f=Instance.new('Folder');f.Name=n;f.Parent=root;folders[n]=f end
local Lighting=game:GetService('Lighting'); Lighting.ClockTime=16.2; Lighting.Brightness=2.1
local atm=Lighting:FindFirstChild('Idea2World_Atmosphere') or Instance.new('Atmosphere');atm.Name='Idea2World_Atmosphere';atm.Density=.22;atm.Haze=1.4;atm.Parent=Lighting
local biome=BP.archetype or 'temperate'
local function hash(x,z) local n=math.sin(x*127.1+z*311.7+SEED*.013)*43758.5453;return n-math.floor(n) end
local function noise(x,z) local ix,iz=math.floor(x),math.floor(z);local fx,fz=x-ix,z-iz;fx=fx*fx*(3-2*fx);fz=fz*fz*(3-2*fz);local a,b,c,d=hash(ix,iz),hash(ix+1,iz),hash(ix,iz+1),hash(ix+1,iz+1);return (a+(b-a)*fx)+((c+(d-c)*fx)-(a+(b-a)*fx))*fz end
local function ridge(x,z) local n=noise(x,z);return 1-math.abs(2*n-1) end
local function riverX(t) return math.sin(t*7.4+SEED*.03)*SIZE*.13+math.sin(t*3.1+1.7)*SIZE*.08 end
local function heightAt(x,z)
 local nx,nz=x/SIZE,z/SIZE;local broad=noise(nx*5+11,nz*5-8);local detail=noise(nx*17-3,nz*17+9);local r=ridge(nx*8+2,nz*8-5)
 local mountainMask=math.clamp((noise(nx*3+30,nz*3+20)-.34)*2.5,0,1)
 local ridges=(r*r)*mountainMask*105*RELIEF;local hills=(broad*32+detail*7)*RELIEF
 local radial=math.clamp(1-math.sqrt(nx*nx+nz*nz)/.78,0,1);local h=8+hills+ridges+radial*12
 if biome=='volcanic' then h+=math.max(0,1-math.sqrt(nx*nx+nz*nz)/.42)*100*RELIEF end
 if biome=='snow' then h+=math.max(0,mountainMask-.2)*38 end
 local t=math.clamp(z/SIZE+.5,0,1);local rx=riverX(t);local dist=math.abs(x-rx);h-=math.max(0,1-dist/(SIZE*.055))*math.min(30,h*.48)
 return math.max(5,h)
end
local function mat(h,x,z) if biome=='desert' then return Enum.Material.Sand elseif biome=='snow' then return h>62 and Enum.Material.Glacier or Enum.Material.Snow elseif biome=='volcanic' then return h>58 and Enum.Material.Basalt or Enum.Material.Ground elseif biome=='swamp' then return Enum.Material.Mud end;return h>76 and Enum.Material.Rock or (noise(x*.02,z*.02)>.68 and Enum.Material.Ground or Enum.Material.Grass) end
local function part(parent,n,size,pos,color,material,shape) local p=Instance.new('Part');p.Name=n;p.Size=size;p.Position=pos;p.Anchored=true;p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth;p.Color=color;p.Material=material or Enum.Material.Slate;if shape then p.Shape=shape end;p.Parent=parent;return p end
-- Base terrain: multi-scale hills + mountain ridges, with a clear river valley.
local done=0
for ix=1,GRID do for iz=1,GRID do local x=-SIZE/2+(ix-.5)*TILE;local z=-SIZE/2+(iz-.5)*TILE;local h=heightAt(x,z);Terrain:FillBlock(CFrame.new(x,h/2-3,z),Vector3.new(TILE+1,h,TILE+1),mat(h,x,z));done+=1;if done%100==0 then task.wait() end end end
-- Watercourse and connected pools.
for i=0,120 do local t=i/120;local z=-SIZE*.48+t*SIZE*.96;local x=riverX(t);local w=SIZE*(.035+.012*math.sin(t*19)^2);Terrain:FillBlock(CFrame.new(x,heightAt(x,z)-5,z),Vector3.new(w,16,TILE*1.5),Enum.Material.Water);if i%24==0 then task.wait() end end
-- Dramatic cliff escarpments: stacked, irregular rock shelves following selected ridge bands.
for i=1,18 do local t=i/19;local x=(t-.5)*SIZE*1.55;local z=math.sin(t*11+SEED)*SIZE*.22;local y=heightAt(x,z);local h=rng:NextNumber(38,92)*RELIEF;local w=rng:NextNumber(38,95);local c=Color3.fromRGB(83,78,72)
 for layer=1,3 do local width=w*(1-(layer-1)*.17);local shelf=part(folders.Cliffs,'Strata_'..i..'_'..layer,Vector3.new(width,h/3,width*.62),Vector3.new(x+(layer-2)*5,y+h*(layer/3),z),c,Enum.Material.Rock);shelf.Orientation=Vector3.new(rng:NextNumber(-8,8),rng:NextNumber(0,180),rng:NextNumber(-8,8)) end
end
-- Carved cave mouths and short tunnels using Air spheres; stone portal frames remain visible.
local stone=Color3.fromRGB(91,86,79);local wood=Color3.fromRGB(103,69,43);local gold=Color3.fromRGB(190,151,86)
for i=1,math.min(8,#BP.landmarks) do local lm=BP.landmarks[i];if lm.type=='cave' or i==3 or i==7 then local x,z=lm.x*SIZE*.42,lm.z*SIZE*.42;local y=heightAt(x,z);Terrain:FillBall(Vector3.new(x,y-5,z),TILE*1.15,Enum.Material.Air);Terrain:FillBall(Vector3.new(x,y-5,z-TILE*.9),TILE*.82,Enum.Material.Air);part(folders.Caves,'CaveLintel_'..i,Vector3.new(TILE*2.1,5,6),Vector3.new(x,y+TILE*.62,z),stone,Enum.Material.Rock);for side=-1,1,2 do part(folders.Caves,'CaveJamb_'..i..'_'..side,Vector3.new(5,TILE*1.4,7),Vector3.new(x+side*TILE*.82,y-TILE*.1,z),stone,Enum.Material.Rock) end end end
-- Architectural kits: layered plinths, walls, towers, roof forms, trim and warm windows.
local function building(parent,x,y,z,s,variant,index)
 local m=Instance.new('Model');m.Name=variant..'_'..index;m.Parent=parent
 part(m,'Foundation',Vector3.new(s*1.5,5,s*1.5),Vector3.new(x,y+2,z),stone)
 if variant=='village' or variant=='factory' then
  for j=1,6 do local ox=(j%3-1)*s*.72;local oz=(math.floor((j-1)/3)-.5)*s*.95;local h=s*rng:NextNumber(.65,1.15);part(m,'HouseBody'..j,Vector3.new(s*.62,h,s*.62),Vector3.new(x+ox,y+5+h/2,z+oz),Color3.fromRGB(155,128,91),Enum.Material.Wood);local roof=part(m,'Roof'..j,Vector3.new(s*.78,5,s*.78),Vector3.new(x+ox,y+10+h,z+oz),variant=='factory' and stone or Color3.fromRGB(119,65,48),Enum.Material.Slate);roof.Shape=Enum.PartType.Wedge;part(m,'Door'..j,Vector3.new(3,h*.48,1),Vector3.new(x+ox,y+7+h*.24,z+oz-s*.315),wood,Enum.Material.Wood);part(m,'Window'..j,Vector3.new(2,3,1),Vector3.new(x+ox+s*.18,y+8+h*.58,z+oz-s*.32),Color3.fromRGB(255,196,105),Enum.Material.Neon) end
 else
  for j=1,4 do local angle=(j-1)*math.pi/2;local ox=math.cos(angle)*s*.55;local oz=math.sin(angle)*s*.55;part(m,'OuterWall'..j,Vector3.new(s*.35,s*1.4,s*1.35),Vector3.new(x+ox,y+s*.72+5,z+oz),stone,Enum.Material.Cobblestone) end
  for j=1,4 do local ox=(j%2==0 and 1 or -1)*s*.58;local oz=(j<3 and 1 or -1)*s*.58;local h=s*rng:NextNumber(1.8,2.5);part(m,'KeepTower'..j,Vector3.new(s*.38,h,s*.38),Vector3.new(x+ox,y+h/2+5,z+oz),stone,Enum.Material.Rock);part(m,'TowerCap'..j,Vector3.new(s*.52,5,s*.52),Vector3.new(x+ox,y+h+7,z+oz),gold,Enum.Material.Metal) end
  part(m,'GreatHall',Vector3.new(s*.9,s*1.1,s*.9),Vector3.new(x,y+s*.55+5,z),Color3.fromRGB(126,111,91),Enum.Material.Slate)
 end
end
for i,lm in ipairs(BP.landmarks) do local x,z=lm.x*SIZE*.42,lm.z*SIZE*.42;local y=heightAt(x,z);local s=math.max(18,lm.scale*TILE*1.35);local typ=lm.type;local m=Instance.new('Model');m.Name=lm.name;m.Parent=folders.Landmarks
 if typ=='village' or typ=='castle' or typ=='factory' or typ=='temple' or typ=='ruins' then building(m,x,y,z,s,typ=='village' and 'village' or typ=='factory' and 'factory' or 'citadel',i)
 elseif typ=='giant_tree' then part(m,'AncientTrunk',Vector3.new(s*.42,s*2.8,s*.42),Vector3.new(x,y+s*1.4,z),wood,Enum.Material.Wood);for j=1,11 do part(m,'Canopy_'..j,Vector3.new(s*1.05,s*1.05,s*1.05),Vector3.new(x+math.sin(j*2.1)*s*.38,y+s*(2+j*.12),z+math.cos(j*2.1)*s*.38),Color3.fromRGB(42+j%4*7,112+j%3*12,49),Enum.Material.Grass,Enum.PartType.Ball) end
 elseif typ=='bridge' then part(m,'BridgeDeck',Vector3.new(s*3.6,5,s*.8),Vector3.new(x,y+5,z),stone);for j=-3,3 do part(m,'Baluster'..j,Vector3.new(3,10,3),Vector3.new(x+j*s*.48,y+12,z-s*.32),gold,Enum.Material.Wood) end
 elseif typ=='lake' or typ=='waterfall' then part(m,'Pool',Vector3.new(s*2.7,4,s*2.7),Vector3.new(x,y+1,z),Color3.fromRGB(60,151,204),Enum.Material.Glass);if typ=='waterfall' then part(m,'WaterfallSheet',Vector3.new(s*.7,s*3,5),Vector3.new(x,y+s*1.4,z),Color3.fromRGB(126,205,235),Enum.Material.Glass) end
 elseif typ=='volcano' then for j=1,7 do local r=s*(3.5-j*.28);part(m,'CalderaRim'..j,Vector3.new(r,s*.28,r),Vector3.new(x,y+s*(.4+j*.18),z),Color3.fromRGB(67+j*4,49+j*2,42),Enum.Material.Basalt) end;part(m,'LavaCore',Vector3.new(s*1.1,6,s*1.1),Vector3.new(x,y+s*1.8,z),Color3.fromRGB(255,83,13),Enum.Material.Neon)
 else part(m,'MonumentBase',Vector3.new(s*1.5,7,s*1.5),Vector3.new(x,y+3,z),stone);for j=1,5 do part(m,'Spire'..j,Vector3.new(s*.24,s*(1+j*.38),s*.24),Vector3.new(x+(j-3)*s*.27,y+s*(.5+j*.2),z),stone,Enum.Material.Rock) end end
 if i%2==0 then task.wait() end
end
-- Forests are generated as groves with clustered density, clearings and varied canopy sizes.
local treeTarget=math.floor(GRID*GRID*.11*(DECOR/80));local placed=0;local attempts=0
while placed<treeTarget and attempts<treeTarget*9 do attempts+=1;local x=rng:NextNumber(-SIZE*.47,SIZE*.47);local z=rng:NextNumber(-SIZE*.47,SIZE*.47);local y=heightAt(x,z);local safe=y<115 and math.abs(x-riverX(z/SIZE+.5))>SIZE*.055
 for _,lm in ipairs(BP.landmarks) do if (Vector2.new(x,z)-Vector2.new(lm.x*SIZE*.42,lm.z*SIZE*.42)).Magnitude<TILE*lm.scale*2.1 then safe=false;break end end
 -- Clustered density field creates groves rather than even scatter.
 local grove=noise(x*.004+51,z*.004-21);safe=safe and grove>.37 and rng:NextNumber()<(.35+grove*.5)
 if safe then local h=rng:NextNumber(10,20);local crown=rng:NextNumber(9,17);part(folders.Forests,'Trunk_'..placed,Vector3.new(rng:NextNumber(1.6,2.8),h,rng:NextNumber(1.6,2.8)),Vector3.new(x,y+h/2,z),wood,Enum.Material.Wood);local crownPart=part(folders.Forests,'Canopy_'..placed,Vector3.new(crown,crown*rng:NextNumber(1.0,1.5),crown),Vector3.new(x,y+h+crown*.35,z),Color3.fromRGB(rng:NextInteger(37,72),rng:NextInteger(92,145),rng:NextInteger(38,75)),Enum.Material.Grass,Enum.PartType.Ball);crownPart.Orientation=Vector3.new(rng:NextNumber(-8,8),rng:NextNumber(0,180),rng:NextNumber(-8,8));placed+=1 end
 if attempts%350==0 then task.wait() end
end
-- Curated route ribbons, with orientation aligned to each segment.
for ri,route in ipairs(BP.routes or {}) do local pts=route.waypoints or {};for j=1,#pts-1 do local a,b=pts[j],pts[j+1];local ax,az=a[1]*SIZE*.4,a[2]*SIZE*.4;local bx,bz=b[1]*SIZE*.4,b[2]*SIZE*.4;local dx,dz=bx-ax,bz-az;local len=math.sqrt(dx*dx+dz*dz);local mx,mz=(ax+bx)/2,(az+bz)/2;local p=part(folders.Routes,'Trail_'..ri..'_'..j,Vector3.new(13,1.5,len),Vector3.new(mx,heightAt(mx,mz)+1,mz),Color3.fromRGB(143,128,99),Enum.Material.Ground);p.CFrame=CFrame.new(mx,heightAt(mx,mz)+1,mz)*CFrame.Angles(0,math.atan2(dx,dz),0) end end
-- THEMED COSMETIC ASSET KIT: distinct silhouettes, layered meshes made from primitives, trim and emissive focal details.
local Cosmetics=Instance.new('Folder');Cosmetics.Name='Cosmetics';Cosmetics.Parent=root
local VFX=Instance.new('Folder');VFX.Name='VFX';VFX.Parent=root
local accent=Color3.fromRGB(139,92,246)
if VISUAL_THEME=='sci_fi' then accent=Color3.fromRGB(34,211,238) elseif VISUAL_THEME=='fantasy' then accent=Color3.fromRGB(240,198,116) elseif VISUAL_THEME=='crystal' then accent=Color3.fromRGB(103,232,249) elseif VISUAL_THEME=='steampunk' then accent=Color3.fromRGB(214,164,93) elseif VISUAL_THEME=='natural' then accent=Color3.fromRGB(134,185,107) end
local function neon(parent,name,size,pos,color,material)
 local p=part(parent,name,size,pos,color,material or Enum.Material.Neon);p.CanCollide=false;p.CastShadow=false;return p
end
local function makeCosmetic(lm,index)
 local x,z=lm.x*SIZE*.42,lm.z*SIZE*.42;local y=heightAt(x,z);local s=TILE*math.max(.65,lm.scale);local m=Instance.new('Model');m.Name='Themed_'..index..'_'..lm.type;m.Parent=Cosmetics
 local kind=VISUAL_THEME
 if kind=='cosmic' or kind=='fantasy' or kind=='crystal' then
  for k=1,5 do local a=k*math.pi*2/5;local h=s*rng:NextNumber(1.1,2.1);local c=part(m,'PrismaticShard_'..k,Vector3.new(s*.23,h,s*.23),Vector3.new(x+math.cos(a)*s*.7,y+h*.42,z+math.sin(a)*s*.7),accent,Enum.Material.Neon);c.Shape=Enum.PartType.Wedge;c.Orientation=Vector3.new(rng:NextNumber(-12,12),k*72,rng:NextNumber(-12,12)) end
  local orb=neon(m,'FloatingCore',Vector3.new(s*.45,s*.45,s*.45),Vector3.new(x,y+s*1.9,z),accent);orb.Shape=Enum.PartType.Ball
  local light=Instance.new('PointLight');light.Color=accent;light.Brightness=2.2;light.Range=s*5;light.Parent=orb
 elseif kind=='sci_fi' then
  for k=1,4 do local a=k*math.pi/2;local px,pz=x+math.cos(a)*s*.8,z+math.sin(a)*s*.8;part(m,'TechPylon_'..k,Vector3.new(s*.22,s*1.7,s*.22),Vector3.new(px,y+s*.85,pz),stone,Enum.Material.Metal);neon(m,'PylonLight_'..k,Vector3.new(s*.28,.45,s*.28),Vector3.new(px,y+s*1.25,pz),accent) end
  local core=neon(m,'Reactor',Vector3.new(s*.65,s*.65,s*.65),Vector3.new(x,y+s*.8,z),accent);core.Shape=Enum.PartType.Ball
 elseif kind=='steampunk' then
  for k=1,4 do local gear=part(m,'GearHousing_'..k,Vector3.new(s*.75,s*.16,s*.75),Vector3.new(x+(k-2.5)*s*.42,y+s*(.6+k*.22),z),accent,Enum.Material.Metal);gear.Shape=Enum.PartType.Cylinder;gear.Orientation=Vector3.new(0,0,90) end
  part(m,'BrassPipe',Vector3.new(s*.18,s*2,s*.18),Vector3.new(x,y+s,z),gold,Enum.Material.Metal)
 else
  for k=1,4 do local rock=part(m,'ArtRock_'..k,Vector3.new(s*rng:NextNumber(.3,.8),s*rng:NextNumber(.25,.7),s*rng:NextNumber(.3,.8)),Vector3.new(x+rng:NextNumber(-s,s),y+s*.2,z+rng:NextNumber(-s,s)),stone,Enum.Material.Rock);rock.Orientation=Vector3.new(rng:NextNumber(-25,25),rng:NextNumber(0,180),rng:NextNumber(-25,25)) end
 end
end
if COSMETIC_DETAIL>0 then for i,lm in ipairs(BP.landmarks) do if i==1 or i%2==0 or lm.priority=='major' then makeCosmetic(lm,i) end end end
-- Reusable VFX emitter presets. All emitters are client-visible effects; keep rate bounded for performance.
local function attachEmitter(parent, name, texture, color, rate, lifetime, speed, size0, size1, light)
 local a=Instance.new('Attachment');a.Name=name..'_Attachment';a.Parent=parent
 local e=Instance.new('ParticleEmitter');e.Name=name;e.Texture=texture;e.Color=ColorSequence.new(color);e.Rate=rate;e.Lifetime=NumberRange.new(lifetime*.7,lifetime);e.Speed=NumberRange.new(speed*.5,speed);e.SpreadAngle=Vector2.new(180,180);e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,size0),NumberSequenceKeypoint.new(1,size1)});e.LightEmission=light or .5;e.Rotation=NumberRange.new(0,360);e.RotSpeed=NumberRange.new(-45,45);e.Parent=a;return e
end
local function addPointVFX(lm,index)
 local x,z=lm.x*SIZE*.42,lm.z*SIZE*.42;local y=heightAt(x,z);local host=neon(VFX,'VFXAnchor_'..index,Vector3.new(1,1,1),Vector3.new(x,y+TILE*.9,z),accent);host.Transparency=1
 local rate=math.floor((2+VFX_DENSITY*.12)*(lm.priority=='primary' and 1.8 or 1))
 local preset='stardust';if VISUAL_THEME=='sci_fi' then preset='energy_arcs' elseif VISUAL_THEME=='fantasy' then preset='fairy_motes' elseif VISUAL_THEME=='steampunk' then preset='steam_burst' elseif VISUAL_THEME=='natural' then preset='fireflies' elseif VISUAL_THEME=='crystal' then preset='crystal_shimmer' end
 attachEmitter(host,preset,'rbxasset://textures/particles/sparkles_main.dds',accent,rate,2.8,4,.28,.02,.9)
 local light=Instance.new('PointLight');light.Name='AccentGlow';light.Color=accent;light.Brightness=VFX_DENSITY/45;light.Range=TILE*(lm.priority=='primary' and 4 or 2);light.Parent=host
 if lm.type=='portal' or VISUAL_THEME=='cosmic' or VISUAL_THEME=='fantasy' then
  for ring=1,2 do local r=neon(VFX,'ArcaneRing_'..index..'_'..ring,Vector3.new(TILE*(1.2+ring*.45),.35,.35),Vector3.new(x,y+TILE*(.55+ring*.3),z),accent);r.Shape=Enum.PartType.Cylinder;r.Orientation=Vector3.new(0,0,90);r.Transparency=.18 end
 end
end
if VFX_DENSITY>0 then for i,lm in ipairs(BP.landmarks) do if i==1 or i%2==0 then addPointVFX(lm,i) end end end
-- Ambient atmosphere is tuned to the visual theme without replacing the user's global post-processing stack.
local cc=Lighting:FindFirstChild('Idea2World_ColorGrade') or Instance.new('ColorCorrectionEffect');cc.Name='Idea2World_ColorGrade';cc.Saturation=.12;cc.Contrast=.08;cc.Parent=Lighting
local bloom=Lighting:FindFirstChild('Idea2World_Bloom') or Instance.new('BloomEffect');bloom.Name='Idea2World_Bloom';bloom.Intensity=VFX_DENSITY/100*.65;bloom.Size=32;bloom.Threshold=1.1;bloom.Parent=Lighting
print(('Idea2World 4.0 COMPLETE | %s | terrain cells=%d | trees=%d | landmarks=%d | theme=%s | VFX=%d'):format(BP.title,done,placed,#BP.landmarks,VISUAL_THEME,VFX_DENSITY))
