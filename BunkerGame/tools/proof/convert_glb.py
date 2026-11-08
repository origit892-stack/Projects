import sys
import trimesh

SRC = "/Users/Ori/Documents/Projects/BunkerGame/cube/outputs/bunker_cube_v1.obj"
DST = "/Users/Ori/Documents/Projects/BunkerGame/cube/outputs/bunker_cube_v1.glb"

m = trimesh.load(SRC)
if isinstance(m, trimesh.Scene):
    g = m.geometry()
    meshes = list(g.values()) if hasattr(g, "values") else [m]
    m = meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)

m.export(DST)
print("GLB_EXPORTED faces=%d verts=%d" % (m.faces.shape[0], m.vertices.shape[0]))
PY = None