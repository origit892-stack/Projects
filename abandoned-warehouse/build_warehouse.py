import bpy, math, random, os
from mathutils import Vector
random.seed(19)
OUT='/Users/origan/Documents/Projects/abandoned-warehouse'
# Keep the user's existing scene and create this model in its own scene.
scene=bpy.data.scenes.new('Abandoned Warehouse')
bpy.context.window.scene=scene
bpy.context.preferences.filepaths.file_preview_type='NONE'
collections={}
for name in ['01 Building shell','02 Steel structure','03 Pendant lamps','04 Worktable','05 Abandoned contents','06 Surface damage','07 Lighting and camera']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name[:2]]=c

def place(obj,group):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 collections[group].objects.link(obj)
 return obj

def material(name,base,rough=.8,metal=0,noise=5,bump=.12,second=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*base,1)
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Base Color'].default_value=(*base,1)
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise;tex.inputs['Detail'].default_value=4
 coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Generated'],tex.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[1].position=.78
 ramp.color_ramp.elements[0].color=(*[v*.32 for v in base],1)
 ramp.color_ramp.elements[1].color=(*(second or base),1)
 l.new(tex.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=bump;bn.inputs['Distance'].default_value=.09
 l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
 return m
concrete=material('Damp stained concrete',(0.32,.34,.29),noise=7,bump=.35)
floor=material('Dusty worn concrete floor',(.27,.24,.19),noise=32,bump=.28)
ceiling=material('Soot-dark ceiling',(.14,.14,.12),noise=18,bump=.3)
rust=material('Oxidized structural iron',(.33,.13,.045),rough=.76,metal=.65,noise=8,bump=.23,second=(.22,.24,.21))
steel=material('Lamp enamel - midnight green',(.055,.095,.08),rough=.38,metal=.7,noise=10,bump=.09)
brass=material('Tarnished warm brass',(.56,.34,.10),rough=.35,metal=.8,noise=7,bump=.08)
wood=material('Weathered oak grain',(.44,.26,.105),noise=5,bump=.23,second=(.5,.36,.21))
# Stretch the wood texture into long grain.
for n in wood.node_tree.nodes:
 if n.type=='TEX_NOISE':
  mapping=wood.node_tree.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,38,8)
  coord=next(x for x in wood.node_tree.nodes if x.type=='TEX_COORD')
  wood.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0]);wood.node_tree.links.new(mapping.outputs[0],n.inputs['Vector']);break
card=material('Collapsed cardboard',(.31,.21,.10),noise=22)
dark=material('Dark cracks and stains',(.047,.043,.032),noise=14)
paint=material('Faded safety yellow',(.57,.36,.075),rough=.85,noise=15)
bulb=bpy.data.materials.new('Warm amber bulb glass');bulb.use_nodes=True
p=bulb.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(1,.59,.18,1);p.inputs['Emission'].default_value=(1,.45,.10,1);p.inputs['Emission Strength'].default_value=5

def box(name,loc,size,mat,group='05',bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat);place(o,group)
 if bevel:
  mod=o.modifiers.new('Soft worn edges','BEVEL');mod.width=bevel;mod.segments=2
  mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def cylinder(name,loc,r,depth,mat,group='05',vertices=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat);place(o,group)
 for f in o.data.polygons:f.use_smooth=True
 return o

def rod(name,a,b,r,mat,group='02'):
 a=Vector(a);b=Vector(b);o=cylinder(name,(a+b)/2,r,(b-a).length,mat,group,12)
 o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def line(name,points,mat,width=.009,group='06'):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=1
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);collections[group].objects.link(o);o.data.materials.append(mat);return o

# Two nested, closed surfaces form a sealed hollow building, with no openings.
verts=[];faces=[];indices=[]
for inward,(x,y,z0,z1) in enumerate([(6.25,8.25,-.28,6.15),(6,8,0,5.9)]):
 start=len(verts);verts.extend([(-x,-y,z0),(x,-y,z0),(x,y,z0),(-x,y,z0),(-x,-y,z1),(x,-y,z1),(x,y,z1),(-x,y,z1)])
 fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 for i,f in enumerate(fs):faces.append(tuple(start+j for j in (tuple(reversed(f)) if inward else f)));indices.append(1 if i==0 else 2 if i==1 else 0)
mesh=bpy.data.meshes.new('Sealed warehouse shell mesh');mesh.from_pydata(verts,[],faces);mesh.update()
shell=bpy.data.objects.new('Warehouse - sealed walls floor and roof',mesh);collections['01'].objects.link(shell)
for mat in [concrete,floor,ceiling]:mesh.materials.append(mat)
for f,idx in zip(mesh.polygons,indices):f.material_index=idx
shell['description']='12 x 16 m sealed warehouse interior. Closed walls, floor and roof; no open windows or doorways.'

# Pillars and ceiling trusses.
for y in [-6,-2,2,6]:
 for x in [-5.72,5.72]:
  box('Rusted column',(x,y,2.9),(.22,.27,5.8),rust,'02',.016)
  box('Column foot plate',(x,y,.06),(.44,.48,.12),rust,'02',.01)
 box('Ceiling crossbeam',(0,y,5.58),(11.65,.2,.28),rust,'02',.012)
 for x in [-4,-2,0,2,4]:rod('Triangular truss brace',(x-1,y,5.7),(x+1,y,5.2),.035,rust)
for x in [-3.5,0,3.5]:box('Longitudinal roof girder',(x,0,5.75),(.12,15.8,.13),rust,'02')
# A bolted shut, corrugated steel gate is mounted on the rear wall.
box('Closed loading door backing',(1.1,7.92,2.0),(4.3,.09,4),steel,'01',.02)
for x in [1.1-2.04+i*.16 for i in range(26)]:box('Loading door corrugation',(x,7.84,2),(.055,.10,3.95),rust,'01',.008)
for x in [-1.14,3.34]:box('Loading door frame',(x,7.73,2.06),(.16,.16,4.12),rust,'01')
box('Loading door lintel',(1.1,7.72,4.1),(4.6,.17,.18),rust,'01')
box('Door locking crossbar',(1.1,7.64,1.5),(4.4,.12,.13),rust,'01')
# Rear warning sign.
bpy.ops.object.text_add(location=(-4.9,7.7,3.3),rotation=(math.pi/2,0,0));sign=bpy.context.object;sign.name='Faded warehouse stencil';sign.data.body='WAREHOUSE 07\nKEEP CLOSED';sign.data.size=.36;sign.data.space_line=1.25;sign.data.extrude=.001;sign.data.materials.append(paint);place(sign,'01')

# Six custom industrial pendant shades, amber bulbs, brass rims, cages and chain links.
for idx,(x,y) in enumerate([(x,y) for y in [-3.6,1,5.5] for x in [-3.1,3.1]]):
 z=4.42 if idx%2==0 else 4.58
 for k in range(10):
  bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=6,location=(x,y,5.65-k*.075),major_radius=.048,minor_radius=.011)
  o=bpy.context.object;o.name='Pendant %02d chain link'%idx;o.rotation_euler=(math.pi/2,0,(k%2)*math.pi/2);o.data.materials.append(rust);place(o,'03')
 rod('Pendant stem',(x,y,4.9),(x,y,z+.2),.028,brass,'03')
 bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.47,radius2=.13,depth=.3,end_fill_type='NOTHING',location=(x,y,z+.15))
 o=bpy.context.object;o.name='Pendant %02d enamel shade'%idx;o.data.materials.append(steel);place(o,'03');solid=o.modifiers.new('Metal shade thickness','SOLIDIFY');solid.thickness=.018
 bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=8,major_radius=.463,minor_radius=.023,location=(x,y,z))
 o=bpy.context.object;o.name='Pendant brass lip';o.data.materials.append(brass);place(o,'03')
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.10,location=(x,y,z-.075))
 o=bpy.context.object;o.name='Pendant amber bulb';o.scale=(.8,.8,1.4);o.data.materials.append(bulb);place(o,'03')
 for angle in [i*math.pi/4 for i in range(8)]:
  line('Bulb protective brass cage',[(x+.19*math.cos(angle),y+.19*math.sin(angle),z),(x+.14*math.cos(angle),y+.14*math.sin(angle),z-.25),(x,y,z-.3)],brass,.009,'03')
 data=bpy.data.lights.new('Pendant warm light %02d'%idx,'POINT');data.energy=210 if idx!=3 else 115;data.color=(1,.63,.29);data.shadow_soft_size=.22
 o=bpy.data.objects.new(data.name,data);collections['07'].objects.link(o);o.location=(x,y,z-.19)
 data=bpy.data.lights.new('Pendant downlight %02d'%idx,'AREA');data.energy=150;data.color=(1,.72,.43);data.shape='DISK';data.size=.7
 o=bpy.data.objects.new(data.name,data);collections['07'].objects.link(o);o.location=(x,y,z-.32)

# Central substantial oak worktable, assembled from real planks.
tx,ty=-.5,.1
for i in range(7):
 o=box('Worktable oak plank %02d'%i,(tx,ty+(i-3)*.205,1.04+random.uniform(-.006,.006)),(3.2,.196,.11),wood,'04',.012)
for x in [tx-1.34,tx+1.34]:
 for y in [ty-.53,ty+.53]:box('Worktable iron leg',(x,y,.48),(.1,.1,.94),rust,'04',.008)
 box('Table transverse brace',(x,ty,.22),(.07,1.18,.09),rust,'04')
for y in [ty-.53,ty+.53]:box('Table lengthwise apron',(tx,y,.92),(2.8,.075,.18),rust,'04')
box('Table lower stretcher',(tx,ty,.23),(2.8,.08,.08),rust,'04')
for x in [tx-1.34,tx+1.34]:
 for y in [ty-.53,ty+.53]:cylinder('Table brass bolt',(x,y,1.101),.024,.009,brass,'04',12)
box('Forgotten toolbox',(tx+.75,ty+.13,1.23),(.58,.32,.26),steel,'04',.025)
rod('Toolbox handle',(tx+.59,ty+.13,1.43),(tx+.91,ty+.13,1.43),.018,brass,'04')
for i in range(4):
 o=box('Dusty scattered document',(tx-.64+i*.07,ty+.13+i*.03,1.103+i*.002),(.4,.27,.002),card,'04');o.rotation_euler.z=random.uniform(-.2,.2)
cylinder('Empty enamel cup',(tx-.15,ty-.42,1.17),.065,.14,steel,'04')

# Old crates, barrels and fallen timber along the walls.
def crate(loc,size):
 x,y,z=loc;s=size
 box('Old crate body',(x,y,z+s/2),(s,s,s),wood,'05',.018)
 for off in [-.36,.36]:
  box('Crate batten',(x+off*s,y-s*.505,z+s*.5),(.09,.04,s*.97),rust,'05',.005)
  box('Crate top batten',(x+off*s,y,z+s+.025),(.09,s,.035),wood,'05')
for loc,s in [((-4.9,5.4,0),1.05),((-4.6,4.1,0),.82),((-4.95,5.4,1.06),.72),((4.7,6.7,0),.85),((4.8,5.65,0),.72),((-5.1,-3.7,0),.8)]:crate(loc,s)
for x,y in [(4.9,2.8),(5.0,1.8),(-4.7,6.9)]:
 cylinder('Rusted abandoned drum',(x,y,.56),.38,1.12,rust)
 for z in [.09,.3,.82,1.07]:
  bpy.ops.mesh.primitive_torus_add(major_radius=.385,minor_radius=.018,major_segments=32,minor_segments=8,location=(x,y,z));o=bpy.context.object;o.name='Drum reinforcing hoop';o.data.materials.append(steel);place(o,'05')
for i in range(7):
 o=box('Fallen wood plank',(4.9+random.uniform(-.3,.3),-2.1+i*.25,.06+i*.012),(1.65,.13,.09),wood,'05',.008);o.rotation_euler.z=random.uniform(-.4,.4)
# A wall pipe with elbow-like connections.
rod('Wall service pipe',(-5.82,-7,3.85),(-5.82,7,3.85),.06,rust)
rod('Pipe vertical return',(-5.82,6.9,.3),(-5.82,6.9,3.85),.06,rust)
for y in [-5,-1,3,6]:box('Pipe mounting bracket',(-5.93,y,3.85),(.12,.09,.2),steel,'02')

# Irregular fine floor cracks and small chipped concrete rubble.
for j in range(23):
 x=random.uniform(-5.5,5.5);y=random.uniform(-6.5,7)
 points=[(x,y,.006)]
 for k in range(random.randint(3,7)):
  x+=random.uniform(-.26,.28);y+=random.uniform(.08,.34);points.append((x,y,.006))
 line('Hairline concrete fracture',points,dark,random.uniform(.003,.007))
for i in range(65):
 x=random.choice([-1,1])*random.uniform(4.3,5.7);y=random.uniform(-5.5,7)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,.025));o=bpy.context.object;o.name='Concrete chip';o.scale=(random.uniform(.025,.09),random.uniform(.035,.12),random.uniform(.015,.045));o.rotation_euler.z=random.random()*6;o.data.materials.append(concrete);place(o,'06')
# Uneven stain trails, tightly attached to the walls.
for side in [-1,1]:
 for j in range(17):
  y=random.uniform(-7.7,7.7);top=random.uniform(2.2,5.5);height=random.uniform(.25,1.7)
  line('Wall damp streak',[(side*5.997,y,top),(side*5.997,y+.02,top-height)],dark,random.uniform(.008,.026))

world=bpy.data.worlds.new('Warehouse darkness');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.07,.09,1);world.node_tree.nodes['Background'].inputs[1].default_value=.09;scene.world=world
# Soft photographic fill, still inside the sealed space.
data=bpy.data.lights.new('Soft interior bounce','AREA');data.energy=110;data.color=(.49,.61,.72);data.shape='DISK';data.size=5
obj=bpy.data.objects.new(data.name,data);collections['07'].objects.link(obj);obj.location=(0,-5.6,3.8);obj.rotation_euler=(Vector((0,2,1.6))-obj.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Interior view');cam=bpy.data.objects.new('Interior view',data);collections['07'].objects.link(cam);cam.location=(.1,-7.35,2.55);cam.rotation_euler=(Vector((0,2.6,2.65))-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=21;data.clip_start=.08;data.clip_end=100;scene.camera=cam
scene.render.engine='BLENDER_EEVEE';scene.eevee.use_gtao=True;scene.eevee.gtao_distance=3;scene.eevee.gtao_factor=1.25;scene.eevee.use_soft_shadows=True;scene.eevee.use_bloom=True;scene.eevee.bloom_intensity=.075;scene.eevee.taa_render_samples=48
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Filmic';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=.4
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(OUT,'warehouse-preview.png')
# Keep lamp meshes and scene contents editable; export all physical mesh geometry.
for o in list(bpy.context.selected_objects):o.select_set(False)
for o in scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.context.view_layer.objects.active=shell
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'abandoned-warehouse.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_lights=False,export_cameras=False)
for o in list(bpy.context.selected_objects):o.select_set(False)
shell.select_set(True);bpy.context.view_layer.objects.active=shell
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.shading.type='SOLID'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'abandoned-warehouse.blend'))
print('WAREHOUSE_CREATED',len(scene.objects),'objects; shell vertices',len(mesh.vertices),'faces',len(mesh.polygons))
