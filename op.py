import bpy
import bmesh

from threading import Thread
from mathutils import Vector

from . blocki import blockify

class BlockifyOperator(bpy.types.Operator):
	bl_idname = "view3d.blockify"
	bl_label = "Blockify"
	bl_description = "Turn 'em into bloccs"

	def execute(self, context):
		scene = context.scene
		mytool = scene.blockify
		
		### TODO:
		### - revise comments before declaring product finished
		### - test parenting
		### - multiple frames

		precision = mytool.precision
		div = mytool.divide_by_vector
		blockSize = Vector(mytool.block_size)

		if div:
			blockSize = Vector((1/blockSize.x,1/blockSize.y,1/blockSize.z))

		blockify(blockSize=blockSize, precision=precision)
		self.report({'INFO'}, "Done current frame")
		return {"FINISHED"}