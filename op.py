import bpy
import bmesh

from mathutils import Vector

from . blocki import Blockify


class BlockifyOperator(bpy.types.Operator):
    bl_idname = "scene.run_blockify"
    bl_label = "Run object blockifier"
    bl_description = "Turn 'em into bloccs"

    def execute(self, context):
        # clear old meshes

        rm = []
        for mesh in bpy.data.meshes:
            if mesh.users == 0:  # maybe only perform on my meshes
                rm.append(mesh)
        for mesh in rm:
            bpy.data.meshes.remove(mesh)

        # real business

        if Blockify.COLLECTION_NAME not in bpy.data.collections:
            print("TIME FOR A FUCKING CRUSADE COLLECTION")
            coll = bpy.data.collections.new(Blockify.COLLECTION_NAME)
            context.scene.collection.children.link(coll)  # inline?
        else:
            coll = bpy.data.collections[Blockify.COLLECTION_NAME]

        blk_glo = context.scene.blockify

        i = blk_glo.frame_start
        while i <= blk_glo.frame_end:
            context.scene.frame_set(i)
            dg = context.evaluated_depsgraph_get()
            for obj in context.scene.objects:
                blk_obj = obj.blockify
                if blk_obj.enabled and coll not in obj.users_collection:
                    print("BLOCKBLOCK " + str(i) + " " + obj.name)

                    blk = blk_obj if blk_obj.override_block_size else blk_glo
                    block_size = Vector(blk.block_size)
                    div = blk.divide_by_vector
                    precision = blk_obj.precision

                    if div:
                        block_size = Vector((
                            1 / block_size.x,
                            1 / block_size.y,
                            1 / block_size.z
                        ))

                    grid = Blockify.compute_grid(
                        dg.objects[obj.name])
                    # Blockify.write_grid_file("grid.fwd", grid)
                    # grid = Blockify.read_grid_file("grid.fwd")

                    name = "zzz_" + obj.name + "_" + str(i)
                    if name in bpy.data.meshes:
                        mesh = bpy.data.meshes[name]
                    else:
                        mesh = bpy.data.meshes.new(name)
                    Blockify.create_mesh(grid, mesh)

                    name = "zzz_" + obj.name
                    if name not in coll.objects:
                        coll.objects.link(bpy.data.objects.new(name, mesh))
            i = i + 1
        # context.evaluated_depsgraph_get().update()
        # blockify(blockSize=blockSize, precision=precision)
        # self.report({'INFO'}, "Done current frame")
        return {"FINISHED"}
