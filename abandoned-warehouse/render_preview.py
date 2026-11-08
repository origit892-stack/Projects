import bpy,os
scene=bpy.data.scenes['Abandoned Warehouse'];bpy.context.window.scene=scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.max_bounces=5
scene.render.resolution_x=1050;scene.render.resolution_y=700
scene.render.filepath='/Users/origan/Documents/Projects/abandoned-warehouse/warehouse-preview.png'
bpy.ops.render.render(write_still=True)
