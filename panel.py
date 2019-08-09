import bpy


class BlockifyPanel(bpy.types.Panel):
    bl_idname = "TEST_PT_Panel"
    bl_label = "Blockify Panel"
    bl_category = "Blockify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        mytool = scene.blockify

        layout.prop(mytool, "block_size", text="Block size")
        layout.prop(mytool, "divide_by_vector", text="Invert block size")

        layout.prop(mytool, "precision", text="Precision")

        layout.operator("view3d.blockify", text="Blockify selected object")
