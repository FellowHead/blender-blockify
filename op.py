import bpy
import bmesh
from bpy_extras.io_utils import ExportHelper

from mathutils import Vector

from . blocki import Blockify


class BlockifyOperator(bpy.types.Operator):
    bl_idname = "object.blockify"
    bl_label = "Blockify"
    bl_description = "Turn 'em into bloccs"

    def execute(self, context):
        scene = context.scene
        mytool = scene.blockify

        # TODO:
        # - revise comments before declaring product finished
        # - test parenting
        # - multiple frames

        precision = mytool.precision
        div = mytool.divide_by_vector
        blockSize = Vector(mytool.block_size)

        if div:
            blockSize = Vector((
                1 / blockSize.x,
                1 / blockSize.y,
                1 / blockSize.z
            ))

            grid = Blockify.compute_grid(
                context.evaluated_depsgraph_get().objects[context.object.name])
            Blockify.write_grid_file("grid.fwd", grid)
        else:
            grid = Blockify.read_grid_file("grid.fwd")
            if mytool.overwrite_destination_mesh:
                mesh = mytool.destination_mesh
            else:
                mesh = bpy.data.meshes.new(context.object.name + " blockified")
            Blockify.create_mesh(grid, mesh)
            context.evaluated_depsgraph_get().update()

        # blockify(blockSize=blockSize, precision=precision)
        # self.report({'INFO'}, "Done current frame")
        return {"FINISHED"}
