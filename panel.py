import bpy

from . blocki import Blockify


class ObjectBlockifyPanel(bpy.types.Panel):
    bl_idname = "BLOCKIFY_PT_object"
    bl_label = "Blockify"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"

    def draw_header(self, context):
        if not self.is_blocki(context):
            self.layout.prop(context.object.blockify, "enabled", text="")

    @staticmethod
    def is_blocki(context):
        return (Blockify.COLLECTION_NAME in bpy.data.collections and
                bpy.data.collections[Blockify.COLLECTION_NAME]
                in context.object.users_collection)

    def draw(self, context):
        layout = self.layout
        if not self.is_blocki(context):
            blk_obj = context.object.blockify
            blk_glo = context.scene.blockify

            if blk_obj.enabled:
                layout.prop(blk_obj, "material", text="Material")

                layout.separator()

                layout.label(text="Block size:")
                layout.prop(blk_obj, "override_block_size",
                            text="Override")
                col = layout.column()
                col.enabled = blk_obj.override_block_size

                blk = blk_obj if blk_obj.override_block_size else blk_glo

                col.prop(blk, "block_size", text="")
                col.prop(blk, "divide_by_vector", text="Invert")

                layout.separator()

                layout.prop(blk_obj, "precision", text="Precision")
        else:
            layout.label(text="Can't blockify inside Blockified collection",
                         icon='ERROR')


class GlobalBlockifyPanel(bpy.types.Panel):
    bl_idname = "BLOCKIFY_PT_global"
    bl_label = "Blockify"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.blockify

        layout.prop(mytool, "block_size", text="Block size")
        layout.prop(mytool, "divide_by_vector", text="Invert block size")

        col = layout.column()
        col.prop(mytool, "frame_start", text="Start frame")
        col.prop(mytool, "frame_end", text="End frame")

        col.prop(mytool, "cache_path")

        layout.operator("scene.run_blockify",
                        text="Blockify")
